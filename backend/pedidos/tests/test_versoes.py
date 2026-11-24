"""Versões de um pedido (US-03 / EDS-186)."""

from rest_framework.test import APITestCase

from contas.models import Papel, Utilizador
from pedidos import servicos
from pedidos.models import Categoria, Estado, VersaoPedido


class VersoesPedido(APITestCase):
    def setUp(self):
        self.sofia = Utilizador.objects.create_user("sofia", password="x", papel=Papel.CLIENTE)
        self.outro = Utilizador.objects.create_user("cliente2", password="x", papel=Papel.CLIENTE)
        self.marta = Utilizador.objects.create_user("marta", password="x", papel=Papel.PRODUCT_MANAGER)
        self.ricardo = Utilizador.objects.create_user("ricardo", password="x", papel=Papel.PRODUCT_OWNER)
        self.cat = Categoria.objects.create(nome="Relatórios")
        self.pedido = servicos.criar_pedido(
            autor=self.sofia, titulo="Exportar em PDF", descricao="Para a direção.", categoria=self.cat
        )

    def editar(self, utilizador, pedido=None, titulo="Exportar em PDF v2", descricao="Texto novo."):
        self.client.force_authenticate(utilizador)
        alvo = pedido or self.pedido
        return self.client.patch(
            f"/api/pedidos/{alvo.id}/",
            {"titulo": titulo, "descricao": descricao},
            format="json",
        )

    def test_autor_em_novo_edita(self):
        resposta = self.editar(self.sofia)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data["titulo"], "Exportar em PDF v2")
        self.assertTrue(resposta.data["pode_editar"])
        self.assertEqual(VersaoPedido.objects.filter(pedido=self.pedido).count(), 2)

    def test_autor_depois_de_em_analise_leva_403(self):
        servicos.mudar_estado(pedido=self.pedido, para=Estado.EM_ANALISE, autor=self.marta)
        resposta = self.editar(self.sofia)
        self.assertEqual(resposta.status_code, 403)
        self.assertIn("erro", resposta.data)

    def test_outro_cliente_leva_403(self):
        resposta = self.editar(self.outro)
        self.assertEqual(resposta.status_code, 403)

    def test_sem_login_e_recusado(self):
        resposta = self.client.patch(
            f"/api/pedidos/{self.pedido.id}/",
            {"titulo": "X", "descricao": "Y"},
            format="json",
        )
        self.assertEqual(resposta.status_code, 403)

    def test_product_manager_e_owner_editam_sempre(self):
        servicos.mudar_estado(pedido=self.pedido, para=Estado.EM_ANALISE, autor=self.marta)
        self.assertEqual(self.editar(self.marta, titulo="Pela Marta", descricao="ok").status_code, 200)
        self.assertEqual(self.editar(self.ricardo, titulo="Pelo Ricardo", descricao="ok").status_code, 200)

    def test_duas_edicoes_dao_tres_versoes(self):
        self.editar(self.sofia, titulo="Segunda", descricao="d2")
        self.editar(self.sofia, titulo="Terceira", descricao="d3")
        versoes = list(VersaoPedido.objects.filter(pedido=self.pedido).order_by("id"))
        self.assertEqual(len(versoes), 3)
        self.assertEqual(versoes[0].titulo, "Exportar em PDF")
        self.assertEqual(versoes[0].autor_id, self.sofia.id)
        self.assertEqual(versoes[0].quando, self.pedido.criado_em)
        self.assertEqual([v.titulo for v in versoes], ["Exportar em PDF", "Segunda", "Terceira"])

    def test_repor_cria_versao_nova_e_mantem_as_antigas(self):
        self.editar(self.sofia, titulo="Segunda", descricao="d2")
        original = VersaoPedido.objects.filter(pedido=self.pedido).order_by("id").first()
        self.client.force_authenticate(self.sofia)
        resposta = self.client.post(f"/api/pedidos/{self.pedido.id}/versoes/{original.id}/repor/")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data["titulo"], "Exportar em PDF")
        self.assertEqual(VersaoPedido.objects.filter(pedido=self.pedido).count(), 3)
        self.assertTrue(VersaoPedido.objects.filter(pk=original.id).exists())

    def test_editar_sem_mudar_nada_nao_cria(self):
        self.client.force_authenticate(self.sofia)
        resposta = self.client.patch(
            f"/api/pedidos/{self.pedido.id}/",
            {"titulo": "Exportar em PDF", "descricao": "Para a direção."},
            format="json",
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(VersaoPedido.objects.filter(pedido=self.pedido).count(), 0)

    def test_titulo_vazio_da_400(self):
        resposta = self.editar(self.sofia, titulo="   ", descricao="ainda tem texto")
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.data)

    def test_titulo_com_mais_de_120_letras_da_400(self):
        self.assertEqual(self.editar(self.sofia, titulo="a" * 121).status_code, 400)

    def test_versao_de_outro_pedido_da_404(self):
        outro = servicos.criar_pedido(
            autor=self.sofia, titulo="Outro pedido", descricao="x", categoria=self.cat
        )
        self.editar(self.sofia, titulo="Segunda", descricao="d2")
        self.editar(self.sofia, pedido=outro, titulo="Outro v2", descricao="y")
        versao_deste = VersaoPedido.objects.filter(pedido=self.pedido).first()
        self.client.force_authenticate(self.sofia)
        resposta = self.client.post(f"/api/pedidos/{outro.id}/versoes/{versao_deste.id}/repor/")
        self.assertEqual(resposta.status_code, 404)

    def test_lista_versoes(self):
        self.editar(self.sofia, titulo="Segunda", descricao="d2")
        resposta = self.client.get(f"/api/pedidos/{self.pedido.id}/versoes/")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(resposta.data), 2)
        self.assertEqual(resposta.data[0]["titulo"], "Exportar em PDF")
