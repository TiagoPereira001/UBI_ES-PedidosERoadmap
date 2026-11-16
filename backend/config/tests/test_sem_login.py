"""Sem login lê-se o que é público, mas não se escreve nada (IsAuthenticatedOrReadOnly e IsAuthenticated)."""

from django.test import TestCase

ESCRITAS = [
    ("post", "/api/pedidos/"),
    ("post", "/api/pedidos/1/voto/"),
    ("post", "/api/pedidos/1/estado/"),
    ("patch", "/api/pedidos/1/classificar/"),
    ("patch", "/api/priorizacao/1/estimativa/"),
    ("post", "/api/priorizacao/ordem/"),
    ("post", "/api/backlog/"),
    ("post", "/api/backlog/sprints/"),
    ("patch", "/api/backlog/1/equipa/"),
    ("post", "/api/colaboracao/pedidos/1/comentarios/"),
    ("post", "/api/colaboracao/notificacoes/lidas/"),
]

SO_COM_LOGIN = ["/api/priorizacao/sugestao/", "/api/colaboracao/notificacoes/", "/api/colaboracao/pessoas/"]

PUBLICAS = ["/api/saude/", "/api/pedidos/", "/api/categorias/", "/api/priorizacao/", "/api/backlog/"]


class SemLogin(TestCase):
    def test_nao_se_escreve_nada(self):
        for metodo, url in ESCRITAS:
            with self.subTest(f"{metodo.upper()} {url}"):
                resposta = getattr(self.client, metodo)(url, {}, content_type="application/json")
                self.assertIn(resposta.status_code, (401, 403))

    def test_o_que_e_pessoal_pede_login(self):
        for url in SO_COM_LOGIN:
            with self.subTest(url):
                self.assertIn(self.client.get(url).status_code, (401, 403))

    def test_o_que_e_publico_le_se(self):
        for url in PUBLICAS:
            with self.subTest(url):
                self.assertEqual(self.client.get(url).status_code, 200)
