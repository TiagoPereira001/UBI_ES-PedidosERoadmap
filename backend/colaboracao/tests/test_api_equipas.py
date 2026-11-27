from django.test import TestCase

from backlog.tests.base import Dados
from colaboracao import servicos


class ApiEspacoDaEquipa(Dados, TestCase):
    def setUp(self):
        super().setUp()
        servicos.juntar_a_equipa(equipa=self.equipa, utilizador=self.diogo, autor=self.helena)
        self.url = f"/api/colaboracao/equipas/{self.equipa.id}/"

    def test_qualquer_um_ve_mas_so_os_membros_escrevem(self):
        resposta = self.client.get(self.url)
        self.assertEqual([m["username"] for m in resposta.data["membros"]], ["diogo"])
        self.assertFalse(resposta.data["pode_escrever"])
        self.client.force_login(self.sofia)
        resposta = self.client.post(self.url + "mensagens/", {"texto": "Olá"}, content_type="application/json")
        self.assertEqual(resposta.status_code, 403)
        self.client.force_login(self.diogo)
        resposta = self.client.post(self.url + "mensagens/", {"texto": "Olá"}, content_type="application/json")
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.data["mensagens"][0]["autor"], "diogo")

    def test_o_gestor_junta_pessoas(self):
        self.client.force_login(self.helena)
        resposta = self.client.post(self.url + "membros/", {"utilizador": "ricardo"}, content_type="application/json")
        self.assertTrue(resposta.data["pode_gerir"])
        self.assertEqual([m["username"] for m in resposta.data["membros"]], ["diogo", "ricardo"])
        self.client.force_login(self.diogo)
        resposta = self.client.post(self.url + "membros/", {"utilizador": "sofia"}, content_type="application/json")
        self.assertEqual(resposta.status_code, 403)
