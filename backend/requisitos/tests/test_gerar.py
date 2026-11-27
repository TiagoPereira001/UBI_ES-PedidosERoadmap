"""Testes às propostas de user stories. O serviço de IA nunca é chamado a sério nos testes."""

from unittest import mock

from django.test import TestCase

from backlog.tests.base import Dados
from ia import cliente as servico_ia
from pedidos import servicos as pedidos
from requisitos import gerar

RESPOSTA_IA = {
    "historias": [
        {
            "texto": "Como cliente, quero exportar em PDF, para mandar à direção.",
            "criterios": ["Abre no leitor de PDF"],
        },
    ]
}


class ModeloLocal(Dados, TestCase):
    def test_monta_a_frase_com_o_papel_e_o_para_que(self):
        pedido = pedidos.criar_pedido(
            autor=self.sofia, titulo="Exportação de relatórios em PDF",
            descricao="Queria exportar os relatórios mensais em PDF para mandar à direção.", categoria=self.cat,
        )
        propostas = gerar.propor_local(pedido)
        self.assertEqual(
            propostas[0]["texto"], "Como cliente, quero exportação de relatórios em PDF, para mandar à direção."
        )
        self.assertTrue(all(p["texto"].startswith("Como ") and p["criterios"] for p in propostas))

    def test_sem_para_que_na_descricao_usa_uma_frase_neutra(self):
        pedido = pedidos.criar_pedido(
            autor=self.sofia, titulo="Lista mais rápida", descricao="Demora.", categoria=self.cat
        )
        self.assertIn("para não ter de o fazer à mão", gerar.propor_local(pedido)[0]["texto"])


class ComIA(Dados, TestCase):
    def setUp(self):
        super().setUp()
        self.pedido = self.aprovado("Exportação de relatórios em PDF")

    def test_usa_a_resposta_da_ia(self):
        with mock.patch.object(servico_ia, "pedir_json", return_value=(RESPOSTA_IA, "gemini")) as pedir:
            propostas, fonte, servico = gerar.propor(self.pedido)
        self.assertEqual((fonte, servico, len(propostas)), ("ia", "gemini", 1))
        enviado = pedir.call_args.args[1]
        self.assertEqual(set(enviado), {"titulo", "descricao", "categoria", "papel_de_quem_pediu"})

    def test_resposta_fora_do_formato_usa_o_modelo_local(self):
        errada = {"historias": [{"texto": "Exportar em PDF", "criterios": ["x"]}]}
        with mock.patch.object(servico_ia, "pedir_json", return_value=(errada, "claude")):
            with self.assertLogs("requisitos.gerar", level="WARNING"):
                _, fonte, servico = gerar.propor(self.pedido)
        self.assertEqual((fonte, servico), ("modelo local", None))

    def test_se_a_ia_falhar_usa_o_modelo_local(self):
        with mock.patch.object(servico_ia, "pedir_json", side_effect=TimeoutError("sem resposta")):
            with self.assertLogs("requisitos.gerar", level="WARNING"):
                propostas, fonte, _ = gerar.propor(self.pedido)
        self.assertEqual(fonte, "modelo local")
        self.assertEqual(len(propostas), 2)

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_sem_chave_usa_o_modelo_local_sem_avisos(self):
        with self.assertNoLogs("requisitos.gerar", level="WARNING"):
            _, fonte, _ = gerar.propor(self.pedido)
        self.assertEqual(fonte, "modelo local")
