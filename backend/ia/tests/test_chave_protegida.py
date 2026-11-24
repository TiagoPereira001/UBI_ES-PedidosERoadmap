"""A chave do Gemini nunca sai do servidor: nem no endereço, nem nas respostas da API, nem nos registos."""

import io
import urllib.error
from unittest import mock

from django.test import TestCase, override_settings

from backlog.tests.base import Dados
from ia import gemini

CHAVE = "chave-secreta-de-teste-123"


def erro_http(codigo):
    return urllib.error.HTTPError(gemini.URL.format(modelo="m"), codigo, "Erro", {}, io.BytesIO(b"{}"))


@override_settings(IA_FORNECEDOR="", LMSTUDIO_URL="", GEMINI_MODELO="m")
@mock.patch.dict("os.environ", {"GEMINI_API_KEY": CHAVE}, clear=True)
class ChaveProtegida(Dados, TestCase):
    def setUp(self):
        super().setUp()
        self.aprovado("Exportar relatórios", esforco=3)
        self.client.force_login(self.ricardo)

    def pedir_sugestao(self, falha):
        with mock.patch("urllib.request.urlopen", side_effect=falha) as urlopen:
            with self.assertLogs("priorizacao.ia", level="WARNING") as registos:
                resposta = self.client.get("/api/priorizacao/sugestao/")
        return resposta, "\n".join(registos.output), urlopen

    def test_chave_errada_ou_sem_quota_usa_a_regra_local_sem_mostrar_a_chave(self):
        for codigo in (400, 403, 429):
            with self.subTest(codigo):
                resposta, registos, _ = self.pedir_sugestao(erro_http(codigo))
                self.assertEqual(resposta.status_code, 200)
                self.assertEqual(resposta.data["fonte"], "regra local")
                self.assertNotIn(CHAVE, resposta.content.decode())
                self.assertNotIn(CHAVE, registos)

    def test_sem_rede_usa_a_regra_local(self):
        resposta, registos, _ = self.pedir_sugestao(urllib.error.URLError("sem rede"))
        self.assertEqual(resposta.data["fonte"], "regra local")
        self.assertNotIn(CHAVE, registos)

    def test_a_chave_vai_so_no_cabecalho(self):
        _, _, urlopen = self.pedir_sugestao(erro_http(400))
        pedido = urlopen.call_args.args[0]
        self.assertNotIn(CHAVE, pedido.full_url)
        self.assertNotIn("key=", pedido.full_url)
        self.assertNotIn(CHAVE, pedido.data.decode())
        self.assertEqual(pedido.get_header("X-goog-api-key"), CHAVE)
