"""Testes à ligação aos serviços de IA. Nenhum teste chama um serviço a sério."""

import io
import json
from unittest import mock

from django.test import SimpleTestCase, override_settings

from ia import cliente, gemini, lmstudio
from ia.erros import RespostaInvalida, SemIA

GEMINI = {"GEMINI_API_KEY": "chave-gemini"}
CLAUDE = {"ANTHROPIC_API_KEY": "chave-claude"}
AS_DUAS = {**GEMINI, **CLAUDE}


def resposta_gemini(texto, fim="STOP"):
    """Simula o que o urlopen devolve: um ficheiro com o JSON da API, usado num `with`."""
    corpo = {"candidates": [{"finishReason": fim, "content": {"parts": [{"text": texto}]}}]}
    ficheiro = io.BytesIO(json.dumps(corpo).encode())
    contexto = mock.MagicMock()
    contexto.__enter__.return_value = ficheiro
    return contexto


@override_settings(IA_FORNECEDOR="", LMSTUDIO_URL="")
class EscolhaDoServico(SimpleTestCase):
    @mock.patch.dict("os.environ", {}, clear=True)
    def test_sem_chaves_nao_ha_servico(self):
        self.assertIsNone(cliente.fornecedor())
        with self.assertRaises(SemIA):
            cliente.pedir_json("instruções", [], {})

    @mock.patch.dict("os.environ", GEMINI, clear=True)
    def test_so_com_a_chave_do_gemini(self):
        self.assertEqual(cliente.fornecedor(), "gemini")

    @mock.patch.dict("os.environ", CLAUDE, clear=True)
    def test_so_com_a_chave_do_claude(self):
        self.assertEqual(cliente.fornecedor(), "claude")

    @mock.patch.dict("os.environ", AS_DUAS, clear=True)
    def test_com_as_duas_chaves_usa_o_gemini(self):
        self.assertEqual(cliente.fornecedor(), "gemini")

    @mock.patch.dict("os.environ", AS_DUAS, clear=True)
    @override_settings(IA_FORNECEDOR="claude")
    def test_ia_fornecedor_obriga_a_um_servico(self):
        self.assertEqual(cliente.fornecedor(), "claude")

    @mock.patch.dict("os.environ", GEMINI, clear=True)
    @override_settings(IA_FORNECEDOR="claude")
    def test_servico_escolhido_sem_chave_fica_sem_ia(self):
        self.assertIsNone(cliente.fornecedor())


@override_settings(IA_FORNECEDOR="", LMSTUDIO_URL="", GEMINI_MODELO="modelo-de-teste", IA_TEMPO_LIMITE=5)
@mock.patch.dict("os.environ", GEMINI, clear=True)
class Gemini(SimpleTestCase):
    def test_envia_o_pedido_e_devolve_o_json(self):
        with mock.patch("urllib.request.urlopen", return_value=resposta_gemini('{"ok": true}')) as urlopen:
            resposta, servico = cliente.pedir_json("Instruções.", [{"id": 1}], {"type": "object"})
        self.assertEqual((resposta, servico), ({"ok": True}, "gemini"))
        pedido = urlopen.call_args.args[0]
        self.assertIn("models/modelo-de-teste:generateContent", pedido.full_url)
        self.assertNotIn("chave-gemini", pedido.full_url)
        self.assertEqual(pedido.get_header("X-goog-api-key"), "chave-gemini")
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 5)
        corpo = json.loads(pedido.data)
        self.assertEqual(corpo["contents"][0]["parts"][0]["text"], '[{"id": 1}]')
        self.assertIn('"type": "object"', corpo["systemInstruction"]["parts"][0]["text"])
        self.assertEqual(corpo["generationConfig"]["responseMimeType"], "application/json")

    def test_resposta_cortada_nao_e_aceite(self):
        with mock.patch("urllib.request.urlopen", return_value=resposta_gemini("{", fim="MAX_TOKENS")):
            with self.assertRaises(RespostaInvalida):
                gemini.pedir("Instruções.", "[]", {})

    def test_resposta_que_nao_e_json(self):
        with mock.patch("urllib.request.urlopen", return_value=resposta_gemini("isto não é JSON")):
            with self.assertRaises(RespostaInvalida):
                cliente.pedir_json("Instruções.", [], {})


def resposta_lmstudio(texto, fim="stop"):
    corpo = {"choices": [{"finish_reason": fim, "message": {"content": texto}}]}
    contexto = mock.MagicMock()
    contexto.__enter__.return_value = io.BytesIO(json.dumps(corpo).encode())
    return contexto


@override_settings(
    IA_FORNECEDOR="", LMSTUDIO_URL="http://localhost:1234", LMSTUDIO_MODELO="gemma-de-teste", LMSTUDIO_TEMPO_LIMITE=7
)
@mock.patch.dict("os.environ", {}, clear=True)
class LMStudio(SimpleTestCase):
    def test_o_modelo_local_vem_antes_dos_servicos_com_chave(self):
        with mock.patch.dict("os.environ", AS_DUAS):
            self.assertEqual(cliente.fornecedor(), "lmstudio")

    def test_so_aceita_enderecos_locais(self):
        for url, aceite in [
            ("http://host.docker.internal:1234", True),
            ("http://127.0.0.1:1234", True),
            ("", False),
            ("https://exemplo.com", False),
            ("http://localhost.exemplo.com:1234", False),
            ("http://localhost@exemplo.com", False),
            ("file://localhost/etc/passwd", False),
        ]:
            with self.subTest(url), override_settings(LMSTUDIO_URL=url):
                self.assertEqual(lmstudio.disponivel(), aceite)

    def test_envia_o_esquema_e_devolve_o_json_sem_chave(self):
        with mock.patch.object(lmstudio, "_abrir", return_value=resposta_lmstudio('{"ok": true}')) as abrir:
            resposta, servico = cliente.pedir_json("Instruções.", [{"id": 1}], {"type": "object"})
        self.assertEqual((resposta, servico), ({"ok": True}, "lmstudio"))
        pedido = abrir.call_args.args[0]
        self.assertEqual(pedido.full_url, "http://localhost:1234/v1/chat/completions")
        self.assertEqual(abrir.call_args.kwargs["timeout"], 7)
        self.assertFalse(pedido.has_header("Authorization"))
        corpo = json.loads(pedido.data)
        self.assertEqual(corpo["model"], "gemma-de-teste")
        self.assertEqual(corpo["response_format"]["json_schema"]["schema"], {"type": "object"})

    def test_o_token_opcional_vai_so_no_cabecalho(self):
        with mock.patch.dict("os.environ", {"LMSTUDIO_API_KEY": "token-secreto"}):
            with mock.patch.object(lmstudio, "_abrir", return_value=resposta_lmstudio("{}")) as abrir:
                lmstudio.pedir("Instruções.", "[]", {})
        pedido = abrir.call_args.args[0]
        self.assertEqual(pedido.get_header("Authorization"), "Bearer token-secreto")
        self.assertNotIn("token-secreto", pedido.full_url + pedido.data.decode())

    def test_resposta_cortada_nao_e_aceite(self):
        with mock.patch.object(lmstudio, "_abrir", return_value=resposta_lmstudio("{", fim="length")):
            with self.assertRaises(RespostaInvalida):
                lmstudio.pedir("Instruções.", "[]", {})
