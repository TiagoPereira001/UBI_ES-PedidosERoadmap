from unittest import mock

from django.test import TestCase

from backlog.tests.base import Dados


@mock.patch.dict("os.environ", {}, clear=True)
class ApiRequisitos(Dados, TestCase):
    def setUp(self):
        super().setUp()
        self.pedido = self.aprovado("Exportação de relatórios em PDF")
        self.url = f"/api/requisitos/pedidos/{self.pedido.id}/"

    def test_propostas_so_para_o_product_owner(self):
        self.client.force_login(self.diogo)
        self.assertEqual(self.client.post(self.url + "propostas/").status_code, 403)
        self.client.force_login(self.ricardo)
        resposta = self.client.post(self.url + "propostas/")
        self.assertEqual(resposta.data["fonte"], "modelo local")
        self.assertTrue(resposta.data["propostas"][0]["texto"].startswith("Como "))

    def test_aceitar_e_ver_as_historias(self):
        self.client.force_login(self.ricardo)
        dados = {"texto": "Como cliente, quero exportar, para mandar à direção.", "criterios": ["Abre"], "origem": "ia"}
        resposta = self.client.post(self.url + "historias/", dados, content_type="application/json")
        self.assertEqual(resposta.status_code, 201)
        resposta = self.client.get(self.url + "historias/")
        self.assertEqual(resposta.data["pedido"]["total_historias"], 1)
        self.assertEqual(resposta.data["historias"][0]["origem_nome"], "IA")
        self.assertEqual(resposta.data["historias"][0]["criterios"][0]["texto"], "Abre")

    def test_aceitar_fora_do_formato_da_400(self):
        self.client.force_login(self.ricardo)
        dados = {"texto": "Exportar", "criterios": ["Abre"]}
        resposta = self.client.post(self.url + "historias/", dados, content_type="application/json")
        self.assertEqual(resposta.status_code, 400)

    def test_lista_de_pedidos(self):
        resposta = self.client.get("/api/requisitos/pedidos/")
        self.assertEqual([p["titulo"] for p in resposta.data], ["Exportação de relatórios em PDF"])
