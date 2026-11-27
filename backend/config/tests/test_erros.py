from unittest.mock import patch

from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from colaboracao.models import Comentario
from config.erros import tratar_excecao
from pedidos.servicos import RegraViolada, SemPermissao

from colaboracao.tests.base import Dados


class TestTratamentoDeErros(APITestCase):
    def test_sem_permissao_vira_403_com_mensagem(self):
        resposta = tratar_excecao(SemPermissao("Acesso recusado."), {})

        self.assertEqual(resposta.status_code, 403)
        self.assertEqual(resposta.data, {"erro": "Acesso recusado."})

    def test_regra_violada_vira_400_com_mensagem(self):
        resposta = tratar_excecao(RegraViolada("Regra inválida."), {})

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(resposta.data, {"erro": "Regra inválida."})

    def test_outras_excecoes_sao_delegadas_ao_drf(self):
        with patch("config.erros.exception_handler") as handler:
            resposta_drf = object()
            handler.return_value = resposta_drf
            exc = ValidationError("Campo inválido.")
            contexto = {"request": object()}

            resposta = tratar_excecao(exc, contexto)

        self.assertIs(resposta, resposta_drf)
        handler.assert_called_once_with(exc, contexto)


class TestAtomicComHandler(Dados, APITestCase):
    def test_excecao_de_negocio_reverte_gravacao_atomica(self):
        self.client.force_authenticate(self.ricardo)
        url = f"/api/colaboracao/pedidos/{self.pedido.id}/comentarios/"

        with patch("colaboracao.servicos.notificar", side_effect=RegraViolada("Falhou ao notificar.")):
            resposta = self.client.post(url, {"texto": "Comentário"}, format="json")

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(resposta.data, {"erro": "Falhou ao notificar."})
        self.assertEqual(Comentario.objects.count(), 0)
