from django.test import TestCase

from backlog.tests.base import Dados
from pedidos import servicos as pedidos
from pedidos.servicos import RegraViolada, SemPermissao
from requisitos import servicos
from requisitos.models import Origem


class Aceitar(Dados, TestCase):
    def setUp(self):
        super().setUp()
        self.pedido = self.aprovado("Exportação de relatórios em PDF")

    def aceitar(self, **extra):
        dados = {"texto": "Como cliente, quero exportar, para mandar à direção.", "criterios": ["Abre", " "]}
        return servicos.aceitar(pedido=self.pedido, autor=self.ricardo, **{**dados, **extra})

    def test_guarda_a_historia_e_os_criterios_nao_vazios(self):
        historia = self.aceitar(origem=Origem.IA)
        self.assertEqual(historia.origem, Origem.IA)
        self.assertEqual(list(historia.criterios.values_list("texto", flat=True)), ["Abre"])

    def test_so_o_product_owner(self):
        with self.assertRaises(SemPermissao):
            servicos.aceitar(pedido=self.pedido, autor=self.marta, texto="Como x, quero y.", criterios=["z"])
        with self.assertRaises(SemPermissao):
            servicos.propor(pedido=self.pedido, autor=self.diogo)

    def test_tem_de_estar_no_formato_e_ter_criterios(self):
        with self.assertRaises(RegraViolada):
            self.aceitar(texto="Exportar relatórios")
        with self.assertRaises(RegraViolada):
            self.aceitar(criterios=[])

    def test_so_de_pedidos_aprovados(self):
        novo = pedidos.criar_pedido(autor=self.sofia, titulo="Novo", descricao="x", categoria=self.cat)
        with self.assertRaises(RegraViolada):
            servicos.propor(pedido=novo, autor=self.ricardo)

    def test_lista_os_pedidos_aprovados(self):
        pedidos.criar_pedido(autor=self.sofia, titulo="Ainda novo", descricao="x", categoria=self.cat)
        self.aceitar()
        titulos = [p.titulo for p in servicos.pedidos_com_historias()]
        self.assertEqual(titulos, ["Exportação de relatórios em PDF"])
