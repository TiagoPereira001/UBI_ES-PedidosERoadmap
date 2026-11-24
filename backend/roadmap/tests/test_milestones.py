"""Milestones do roadmap (US-16 / EDS-188)."""

from datetime import date

from django.test import TestCase

from backlog.tests.base import Dados
from pedidos import servicos as pedidos
from pedidos.models import Estado
from pedidos.servicos import SemPermissao
from roadmap import servicos
from roadmap.models import Milestone


class Milestones(Dados, TestCase):
    def setUp(self):
        super().setUp()
        self.release = servicos.criar_release(
            autor=self.marta, nome="Release 1.0", inicio=date(2026, 11, 2), data_prevista=date(2026, 11, 27)
        )

    def test_so_product_manager_cria(self):
        with self.assertRaises(SemPermissao):
            servicos.criar_milestone(autor=self.ricardo, nome="Beta", data=date(2026, 11, 15))

    def test_estado_calculado_dos_pedidos(self):
        pedido = self.aprovado("Exportar")
        milestone = servicos.criar_milestone(
            autor=self.marta, nome="Beta", data=date(2026, 11, 15), release=self.release, pedidos=[pedido]
        )
        self.assertEqual(servicos.estado_milestone(milestone), "por_comecar")
        pedidos.mudar_estado(pedido=pedido, para=Estado.EM_DESENVOLVIMENTO, autor=self.diogo)
        self.assertEqual(servicos.estado_milestone(milestone), "em_curso")
        pedidos.mudar_estado(pedido=pedido, para=Estado.EM_REVISAO, autor=self.diogo)
        pedidos.mudar_estado(pedido=pedido, para=Estado.CONCLUIDO, autor=self.ricardo)
        self.assertEqual(servicos.estado_milestone(milestone), "concluido")

    def test_api_cria_muda_e_apaga(self):
        self.client.force_login(self.marta)
        resposta = self.client.post(
            "/api/roadmap/milestones/",
            {"nome": "Beta", "data": "2026-11-15", "release": self.release.id},
            content_type="application/json",
        )
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.data["estado"], "por_comecar")
        mid = resposta.data["id"]
        resposta = self.client.patch(
            f"/api/roadmap/milestones/{mid}/",
            {"nome": "Beta clientes"},
            content_type="application/json",
        )
        self.assertEqual(resposta.data["nome"], "Beta clientes")
        self.assertEqual(self.client.delete(f"/api/roadmap/milestones/{mid}/").status_code, 204)
        self.assertFalse(Milestone.objects.filter(pk=mid).exists())

    def test_roadmap_traz_milestones_sem_n_mais_1(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        for i in range(2):
            r = servicos.criar_release(
                autor=self.marta,
                nome=f"R{i}",
                inicio=date(2026, 12, 1),
                data_prevista=date(2026, 12, 10 + i),
            )
            p = self.aprovado(f"Ped {i}")
            servicos.por_na_release(release=r, pedido=p, autor=self.marta)
            servicos.criar_milestone(
                autor=self.marta, nome=f"M{i}", data=date(2026, 12, 5), release=r, pedidos=[p]
            )
        with CaptureQueriesContext(connection) as pouco:
            self.client.get("/api/roadmap/")
        for i in range(2, 5):
            r = servicos.criar_release(
                autor=self.marta,
                nome=f"R{i}",
                inicio=date(2026, 12, 1),
                data_prevista=date(2026, 12, 10 + i),
            )
            p = self.aprovado(f"Ped {i}")
            servicos.por_na_release(release=r, pedido=p, autor=self.marta)
            servicos.criar_milestone(
                autor=self.marta, nome=f"M{i}", data=date(2026, 12, 5), release=r, pedidos=[p]
            )
        with CaptureQueriesContext(connection) as muito:
            resposta = self.client.get("/api/roadmap/")
        self.assertEqual(len(pouco), len(muito), "mais releases não podem acrescentar queries")
        self.assertTrue(any(r["milestones"] for r in resposta.data["releases"]))

    def test_nome_longo_demais_da_400(self):
        self.client.force_login(self.marta)
        resposta = self.client.post(
            "/api/roadmap/milestones/",
            {"nome": "x" * 81, "data": "2026-11-15"},
            content_type="application/json",
        )
        self.assertEqual(resposta.status_code, 400)
