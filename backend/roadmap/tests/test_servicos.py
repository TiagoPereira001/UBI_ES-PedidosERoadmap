from datetime import date

from django.test import TestCase

from backlog.tests.base import Dados
from pedidos import servicos as pedidos
from pedidos.models import Estado
from pedidos.servicos import RegraViolada, SemPermissao
from roadmap import servicos

HOJE = date(2026, 11, 16)


class Releases(Dados, TestCase):
    def release(self, nome="Release 1.0", inicio=date(2026, 11, 2), prevista=date(2026, 11, 27)):
        return servicos.criar_release(autor=self.marta, nome=nome, inicio=inicio, data_prevista=prevista)

    def test_so_o_product_manager_cria_releases(self):
        with self.assertRaises(SemPermissao):
            servicos.criar_release(autor=self.ricardo, nome="R", inicio=HOJE, data_prevista=date(2026, 12, 1))

    def test_a_data_prevista_tem_de_ser_depois_do_inicio(self):
        with self.assertRaises(RegraViolada):
            self.release(inicio=date(2026, 12, 1), prevista=date(2026, 11, 1))

    def test_nome_repetido_nao(self):
        self.release()
        with self.assertRaises(RegraViolada):
            self.release(nome="release 1.0")

    def test_so_entram_pedidos_aprovados(self):
        release = self.release()
        novo = pedidos.criar_pedido(autor=self.sofia, titulo="Novo", descricao="x", categoria=self.cat)
        with self.assertRaises(RegraViolada):
            servicos.por_na_release(release=release, pedido=novo, autor=self.marta)
        servicos.por_na_release(release=release, pedido=self.aprovado("Aprovado"), autor=self.marta)
        self.assertEqual(release.pedidos.count(), 1)

    def test_estado_vem_das_datas(self):
        release = self.release()
        self.assertEqual(servicos.estado(release, hoje=date(2026, 11, 1)), "planeada")
        self.assertEqual(servicos.estado(release, hoje=HOJE), "em_curso")

    def test_em_risco_perto_da_data_com_pedidos_por_fazer(self):
        release = self.release(prevista=date(2026, 11, 27))
        self.assertFalse(servicos.em_risco(release, hoje=HOJE), "sem pedidos não há risco")
        servicos.por_na_release(release=release, pedido=self.aprovado("Exportar"), autor=self.marta)
        self.assertTrue(servicos.em_risco(release, hoje=HOJE))
        self.assertFalse(servicos.em_risco(release, hoje=date(2026, 11, 1)), "ainda falta muito")

    def test_progresso_conta_os_concluidos(self):
        release = self.release()
        feito = self.aprovado("Feito")
        for para, quem in [(Estado.EM_DESENVOLVIMENTO, self.diogo), (Estado.EM_REVISAO, self.diogo),
                           (Estado.CONCLUIDO, self.ricardo)]:
            pedidos.mudar_estado(pedido=feito, para=para, autor=quem)
        for pedido in [feito, self.aprovado("Por fazer")]:
            servicos.por_na_release(release=release, pedido=pedido, autor=self.marta)
        self.assertEqual(servicos.progresso(release), 50)

    def test_so_se_lanca_com_tudo_concluido(self):
        release = self.release()
        servicos.por_na_release(release=release, pedido=self.aprovado("Por fazer"), autor=self.marta)
        with self.assertRaises(RegraViolada):
            servicos.lancar_release(release=release, autor=self.marta)
        release.pedidos.clear()
        servicos.lancar_release(release=release, autor=self.marta, hoje=HOJE)
        self.assertEqual(servicos.estado(release), "lancada")
        with self.assertRaises(RegraViolada):
            servicos.por_na_release(release=release, pedido=self.aprovado("Tarde"), autor=self.marta)
