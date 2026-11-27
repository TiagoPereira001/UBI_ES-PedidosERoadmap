from django.test import TestCase

from backlog import servicos as backlog
from backlog.tests.base import Dados
from pedidos import servicos as pedidos
from pedidos.models import Estado
from requisitos import servicos
from requisitos.models import Ligacao
from roadmap.models import Release

COMMIT = "https://github.com/exemplo/repo/commit/abc123"


class Rastreabilidade(Dados, TestCase):
    def setUp(self):
        super().setUp()
        self.item = self.no_backlog("Exportar relatórios", esforco=3)
        self.pedido = self.item.pedido

    def historia(self):
        return servicos.aceitar(
            pedido=self.pedido, autor=self.ricardo, texto="Como cliente, quero exportar.", criterios=["Abre", "Imprime"]
        )

    def linha(self):
        return self.client.get("/api/requisitos/rastreabilidade/").json()[0]

    def ligar(self, historia, url=COMMIT, quem=None):
        self.client.force_login(quem or self.diogo)
        corpo = {"url": url, "descricao": "Exportação em PDF"}
        return self.client.post(f"/api/requisitos/historias/{historia.id}/ligacoes/", corpo, "application/json")

    def test_mostra_a_cadeia_do_pedido_ate_a_release(self):
        historia = self.historia()
        sprint = self.sprint()
        backlog.por_no_sprint(item=self.item, sprint=sprint, autor=self.ricardo)
        Release.objects.create(nome="1.0", inicio="2026-11-01", data_prevista="2026-12-01").pedidos.add(self.pedido)
        self.assertEqual(self.ligar(historia).status_code, 201)
        linha = self.linha()
        self.assertEqual((linha["autor"], linha["sprint"], linha["releases"]), ("sofia", "Sprint 4", ["1.0"]))
        self.assertEqual(linha["historias"][0]["ligacoes"][0]["url"], COMMIT)
        self.assertEqual(linha["falta"], [])

    def test_diz_o_que_falta_ligar(self):
        self.assertEqual(self.linha()["falta"], ["Sem user stories"])
        self.historia()
        self.assertEqual(self.linha()["falta"], ["Fora de qualquer sprint"])
        pedidos.Pedido.objects.filter(pk=self.pedido.pk).update(estado=Estado.CONCLUIDO)
        self.assertIn("User story sem ligação ao código", self.linha()["falta"])

    def test_pedido_por_aprovar_nao_aparece(self):
        pedidos.criar_pedido(autor=self.sofia, titulo="Novo", descricao="x", categoria=self.cat)
        self.assertEqual(len(self.client.get("/api/requisitos/rastreabilidade/").json()), 1)

    def test_o_numero_de_consultas_nao_cresce_com_os_pedidos(self):
        self.historia()
        with self.assertNumQueries(6):
            self.linha()
        self.no_backlog("Outro", esforco=2)
        with self.assertNumQueries(6):
            self.linha()

    def test_quem_liga_o_codigo(self):
        historia = self.historia()
        self.assertEqual(self.ligar(historia, quem=self.sofia).status_code, 403)
        self.client.logout()
        resposta = self.client.post(f"/api/requisitos/historias/{historia.id}/ligacoes/", {}, "application/json")
        self.assertEqual(resposta.status_code, 403)
        self.assertFalse(Ligacao.objects.exists())

    def test_so_aceita_enderecos_https_e_uma_vez(self):
        historia = self.historia()
        for url in ("javascript:alert(1)", "http://github.com/x", "nada"):
            with self.subTest(url):
                self.assertEqual(self.ligar(historia, url=url).status_code, 400)
        self.assertEqual(self.ligar(historia).status_code, 201)
        self.assertEqual(self.ligar(historia).status_code, 400)

    def test_so_o_product_owner_marca_criterios(self):
        criterio = self.historia().criterios.first()
        caminho = f"/api/requisitos/criterios/{criterio.id}/"
        self.client.force_login(self.diogo)
        self.assertEqual(self.client.patch(caminho, {"cumprido": True}, "application/json").status_code, 403)
        self.client.force_login(self.ricardo)
        self.assertEqual(self.client.patch(caminho, {}, "application/json").status_code, 400)
        self.assertEqual(self.client.patch(caminho, {"cumprido": True}, "application/json").status_code, 200)
        criterio.refresh_from_db()
        self.assertTrue(criterio.cumprido)
