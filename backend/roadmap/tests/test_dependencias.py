"""Dependências entre pedidos (US-17 / EDS-188)."""

from datetime import date

from django.test import TestCase

from backlog.tests.base import Dados
from pedidos import servicos as pedidos
from pedidos.models import Estado
from pedidos.servicos import RegraViolada, SemPermissao
from roadmap import servicos
from roadmap.models import Dependencia


class Dependencias(Dados, TestCase):
    def setUp(self):
        super().setUp()
        self.a = self.aprovado("Pedido A")
        self.b = self.aprovado("Pedido B")
        self.c = self.aprovado("Pedido C")
        self.release = servicos.criar_release(
            autor=self.marta, nome="Release 2.0", inicio=date(2026, 11, 30), data_prevista=date(2026, 12, 18)
        )
        servicos.por_na_release(release=self.release, pedido=self.a, autor=self.marta)

    def test_programador_e_pm_registam(self):
        servicos.criar_dependencia(pedido=self.a, depende_de=self.b, autor=self.diogo)
        servicos.criar_dependencia(pedido=self.b, depende_de=self.c, autor=self.marta)
        with self.assertRaises(SemPermissao):
            servicos.criar_dependencia(pedido=self.c, depende_de=self.a, autor=self.sofia)

    def test_nao_depende_de_si_proprio(self):
        with self.assertRaises(RegraViolada) as ctx:
            servicos.criar_dependencia(pedido=self.a, depende_de=self.a, autor=self.diogo)
        self.assertIn("si próprio", str(ctx.exception))

    def test_ciclo_direto(self):
        servicos.criar_dependencia(pedido=self.a, depende_de=self.b, autor=self.diogo)
        with self.assertRaises(RegraViolada) as ctx:
            servicos.criar_dependencia(pedido=self.b, depende_de=self.a, autor=self.diogo)
        self.assertIn("ciclo", str(ctx.exception))

    def test_ciclo_indireto(self):
        servicos.criar_dependencia(pedido=self.a, depende_de=self.b, autor=self.diogo)
        servicos.criar_dependencia(pedido=self.b, depende_de=self.c, autor=self.diogo)
        with self.assertRaises(RegraViolada) as ctx:
            servicos.criar_dependencia(pedido=self.c, depende_de=self.a, autor=self.diogo)
        self.assertIn("ciclo", str(ctx.exception))

    def test_aviso_quando_dependencia_fica_de_fora(self):
        servicos.criar_dependencia(pedido=self.a, depende_de=self.b, autor=self.diogo)
        avisos = servicos.avisos_dependencias(self.release)
        self.assertEqual(len(avisos), 1)
        self.assertEqual(avisos[0]["depende_de_id"], self.b.id)
        # Se B está noutra release que acaba antes, deixa de haver aviso.
        anterior = servicos.criar_release(
            autor=self.marta, nome="Release 1.0", inicio=date(2026, 11, 2), data_prevista=date(2026, 11, 27)
        )
        servicos.por_na_release(release=anterior, pedido=self.b, autor=self.marta)
        self.assertEqual(servicos.avisos_dependencias(self.release), [])
        # Concluído também remove o aviso (mesmo sem release).
        servicos.tirar_da_release(release=anterior, pedido=self.b, autor=self.marta)
        pedidos.mudar_estado(pedido=self.b, para=Estado.EM_DESENVOLVIMENTO, autor=self.diogo)
        pedidos.mudar_estado(pedido=self.b, para=Estado.EM_REVISAO, autor=self.diogo)
        pedidos.mudar_estado(pedido=self.b, para=Estado.CONCLUIDO, autor=self.ricardo)
        self.assertEqual(servicos.avisos_dependencias(self.release), [])

    def test_api_cria_e_recusa_ciclo(self):
        self.client.force_login(self.diogo)
        resposta = self.client.post(
            "/api/roadmap/dependencias/",
            {"pedido": self.a.id, "depende_de": self.b.id},
            content_type="application/json",
        )
        self.assertEqual(resposta.status_code, 201)
        resposta = self.client.post(
            "/api/roadmap/dependencias/",
            {"pedido": self.b.id, "depende_de": self.a.id},
            content_type="application/json",
        )
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("ciclo", resposta.data["erro"])

    def test_detalhe_da_release_traz_avisos_sem_n_mais_1(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        servicos.criar_dependencia(pedido=self.a, depende_de=self.b, autor=self.diogo)
        with CaptureQueriesContext(connection) as pouco:
            self.client.get(f"/api/roadmap/releases/{self.release.id}/")
        for i, alvo in enumerate([self.c, self.aprovado("Pedido D"), self.aprovado("Pedido E")]):
            extra = self.aprovado(f"Na release {i}")
            servicos.por_na_release(release=self.release, pedido=extra, autor=self.marta)
            servicos.criar_dependencia(pedido=extra, depende_de=alvo, autor=self.diogo)
        with CaptureQueriesContext(connection) as muito:
            resposta = self.client.get(f"/api/roadmap/releases/{self.release.id}/")
        self.assertEqual(len(pouco), len(muito), "mais dependências não podem acrescentar queries")
        self.assertGreaterEqual(len(resposta.data["avisos"]), 2)
        self.assertGreaterEqual(len(resposta.data["dependencias"]), 2)

    def test_apagar_dependencia(self):
        dep = servicos.criar_dependencia(pedido=self.a, depende_de=self.b, autor=self.diogo)
        self.client.force_login(self.diogo)
        self.assertEqual(self.client.delete(f"/api/roadmap/dependencias/{dep.id}/").status_code, 204)
        self.assertFalse(Dependencia.objects.filter(pk=dep.id).exists())
