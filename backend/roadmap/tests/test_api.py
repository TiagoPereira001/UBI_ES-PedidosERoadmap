from datetime import date

from django.test import TestCase

from backlog.tests.base import Dados
from roadmap import servicos


class ApiRoadmap(Dados, TestCase):
    def setUp(self):
        super().setUp()
        self.release = servicos.criar_release(
            autor=self.marta, nome="Release 1.0", inicio=date(2026, 11, 2), data_prevista=date(2026, 11, 27)
        )
        self.pedido = self.aprovado("Aviso por email")

    def test_qualquer_um_ve_o_roadmap(self):
        resposta = self.client.get("/api/roadmap/")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data["releases"][0]["nome"], "Release 1.0")
        self.assertIn("em_risco", resposta.data["releases"][0])

    def test_criar_release_so_o_product_manager(self):
        dados = {"nome": "Release 2.0", "inicio": "2026-12-01", "data_prevista": "2026-12-18"}
        self.client.force_login(self.ricardo)
        self.assertEqual(self.client.post("/api/roadmap/", dados, content_type="application/json").status_code, 403)
        self.client.force_login(self.marta)
        resposta = self.client.post("/api/roadmap/", dados, content_type="application/json")
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.data["estado"], "planeada")

    def test_por_e_tirar_pedido(self):
        self.client.force_login(self.marta)
        url = f"/api/roadmap/releases/{self.release.id}/pedidos/"
        resposta = self.client.post(url, {"pedido": self.pedido.id}, content_type="application/json")
        self.assertEqual([p["titulo"] for p in resposta.data["pedidos"]], ["Aviso por email"])
        resposta = self.client.delete(f"{url}{self.pedido.id}/")
        self.assertEqual(resposta.data["pedidos"], [])

    def test_lancar_com_pedidos_por_fazer_da_erro(self):
        self.client.force_login(self.marta)
        self.release.pedidos.add(self.pedido)
        resposta = self.client.post(f"/api/roadmap/releases/{self.release.id}/lancar/")
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("por concluir", resposta.data["erro"])

    def test_detalhe(self):
        resposta = self.client.get(f"/api/roadmap/releases/{self.release.id}/")
        self.assertEqual(resposta.data["nome"], "Release 1.0")

    def test_detalhe_traz_aprovados_ordenados_por_titulo(self):
        self.aprovado("Zeta tarde")
        self.aprovado("Alfa cedo")
        resposta = self.client.get(f"/api/roadmap/releases/{self.release.id}/")
        aprovados = resposta.data["aprovados"]
        self.assertEqual([p["titulo"] for p in aprovados], sorted(p["titulo"] for p in aprovados))
        self.assertTrue(all(set(p) == {"id", "titulo"} for p in aprovados))
        self.assertIn("Alfa cedo", [p["titulo"] for p in aprovados])
