from django.test import TestCase

from backlog import servicos as backlog
from backlog.tests.base import Dados
from colaboracao import servicos
from pedidos.servicos import RegraViolada, SemPermissao


class EspacoDaEquipa(Dados, TestCase):
    def setUp(self):
        super().setUp()
        servicos.juntar_a_equipa(equipa=self.equipa, utilizador=self.diogo, autor=self.helena)

    def test_so_o_gestor_de_projeto_muda_os_membros(self):
        with self.assertRaises(SemPermissao):
            servicos.juntar_a_equipa(equipa=self.equipa, utilizador=self.sofia, autor=self.ricardo)
        servicos.juntar_a_equipa(equipa=self.equipa, utilizador=self.diogo, autor=self.helena)
        self.assertEqual(list(servicos.membros(self.equipa)), [self.diogo])

    def test_escrevem_os_membros_e_o_gestor(self):
        servicos.escrever_na_equipa(equipa=self.equipa, autor=self.diogo, texto="Bom dia")
        servicos.escrever_na_equipa(equipa=self.equipa, autor=self.helena, texto="Olá")
        with self.assertRaises(SemPermissao):
            servicos.escrever_na_equipa(equipa=self.equipa, autor=self.sofia, texto="Posso?")
        with self.assertRaises(RegraViolada):
            servicos.escrever_na_equipa(equipa=self.equipa, autor=self.diogo, texto="   ")
        self.assertEqual(self.equipa.mensagens.count(), 2)

    def test_o_trabalho_e_o_que_esta_atribuido_e_por_acabar(self):
        item = self.no_backlog("Exportar", esforco=3)
        backlog.atribuir_equipa(item=item, equipa=self.equipa, autor=self.helena)
        self.no_backlog("De outra equipa", esforco=2)
        self.assertEqual([i.pedido.titulo for i in backlog.itens_da_equipa(self.equipa)], ["Exportar"])
