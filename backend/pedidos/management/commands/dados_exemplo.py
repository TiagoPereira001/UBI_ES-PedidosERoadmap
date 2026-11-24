"""Cria utilizadores de teste e pedidos de exemplo para as demonstrações.

Só para desenvolvimento. A palavra-passe de cada utilizador de teste é o nome seguido de 123
(sofia / sofia123). Também cria o administrador admin / admin123 para entrar em /admin/.
"""

from datetime import date

from django.core.management.base import BaseCommand

from backlog import servicos as backlog
from backlog.models import Equipa
from contas.models import Papel, Utilizador
from pedidos import servicos
from pedidos.models import Categoria, Estado, Pedido
from priorizacao import servicos as priorizacao
from roadmap import servicos as roadmap

UTILIZADORES = [
    ("sofia", Papel.CLIENTE),
    ("marta", Papel.PRODUCT_MANAGER),
    ("ricardo", Papel.PRODUCT_OWNER),
    ("diogo", Papel.PROGRAMADOR),
    ("helena", Papel.GESTOR_PROJETO),
]

CATEGORIAS = ["Relatórios", "Integrações", "Usabilidade", "Desempenho", "Notificações"]

# (título, descrição, categoria, etiquetas)
PEDIDOS = [
    (
        "Exportação de relatórios em PDF",
        "Queria exportar os relatórios mensais em PDF para mandar à direção.",
        "Relatórios",
        ["relatórios", "exportar"],
    ),
    (
        "Filtrar pedidos de reposição por data de validade",
        "Perco muito tempo a ver um por um. Um filtro por data de validade resolvia.",
        "Usabilidade",
        ["filtros"],
    ),
    (
        "Ligação ao Slack",
        "Receber no Slack os avisos quando um pedido muda de estado.",
        "Integrações",
        ["slack", "avisos"],
    ),
    (
        "Lista de pedidos mais rápida",
        "A lista demora a abrir quando há muitos pedidos.",
        "Desempenho",
        [],
    ),
    (
        "Aviso por email quando o pedido é lido",
        "Quero saber quando alguém lê o meu pedido, sem ter de perguntar.",
        "Notificações",
        ["avisos", "email"],
    ),
]


def palavra_passe_teste(nome):
    return f"{nome}123"


EQUIPAS = ["Equipa A", "Equipa B", "Equipa C"]

# Pedidos que a Marta aprova e o Ricardo estima e põe no backlog: (início do título, impacto, esforço, equipa)
PLANEAMENTO = [
    ("Aviso por email", 3, 2, "Equipa A"),
    ("Filtrar pedidos", 2, 3, "Equipa B"),
    ("Ligação ao Slack", 2, 8, None),
]


def planear(pessoas):
    """Aprova três pedidos, estima-os, ordena-os, põe-nos no backlog e prepara o Sprint 4 com o primeiro."""
    marta, ricardo, helena = pessoas["marta"], pessoas["ricardo"], pessoas["helena"]
    equipas = {nome: Equipa.objects.get_or_create(nome=nome)[0] for nome in EQUIPAS}
    ordem = []
    for inicio, impacto, esforco, equipa in PLANEAMENTO:
        pedido = Pedido.objects.get(titulo__startswith=inicio)
        servicos.mudar_estado(pedido=pedido, para=Estado.EM_ANALISE, autor=marta)
        servicos.mudar_estado(pedido=pedido, para=Estado.APROVADO, autor=marta)
        priorizacao.estimar(pedido=pedido, autor=ricardo, impacto=impacto, esforco=esforco)
        item = backlog.acrescentar_ao_backlog(pedido=pedido, autor=ricardo)
        if equipa:
            backlog.atribuir_equipa(item=item, equipa=equipas[equipa], autor=helena)
        ordem.append(pedido.id)
    priorizacao.ordenar(autor=ricardo, ids=ordem, razao="Primeiro o que pede menos esforço para o valor que traz.")
    sprint = backlog.criar_sprint(
        autor=ricardo,
        nome="Sprint 4",
        objetivo="Priorizar e planear dentro do sistema",
        inicio=date(2026, 11, 9),
        fim=date(2026, 11, 20),
        capacidade=10,
    )
    primeiro = Pedido.objects.get(id=ordem[0]).item_backlog
    backlog.por_no_sprint(item=primeiro, sprint=sprint, autor=ricardo)


# Releases que a Marta planeia: (nome, objetivo, início, data prevista, início dos títulos dos pedidos)
RELEASES = [
    ("Release 1.0", "Avisos e filtros", date(2026, 11, 2), date(2026, 11, 27), ["Aviso por email", "Filtrar pedidos"]),
    ("Release 2.0", "Integrações", date(2026, 11, 30), date(2026, 12, 18), ["Ligação ao Slack"]),
]


def planear_releases(marta, diogo):
    """Duas releases, um milestone e uma dependência que gera aviso no ecrã 09."""
    criadas = {}
    for nome, objetivo, inicio, prevista, titulos in RELEASES:
        release = roadmap.criar_release(
            autor=marta, nome=nome, objetivo=objetivo, inicio=inicio, data_prevista=prevista
        )
        for titulo in titulos:
            roadmap.por_na_release(release=release, pedido=Pedido.objects.get(titulo__startswith=titulo), autor=marta)
        criadas[nome] = release
    release1 = criadas["Release 1.0"]
    roadmap.criar_milestone(
        autor=marta,
        nome="Beta para clientes",
        data=date(2026, 11, 15),
        release=release1,
        pedidos=list(release1.pedidos.all()),
    )
    roadmap.criar_milestone(
        autor=marta, nome="Lançamento", data=date(2026, 11, 27), release=release1
    )
    # Slack (Release 2.0) depende da lista rápida, que não está em nenhuma release → aviso.
    slack = Pedido.objects.get(titulo__startswith="Ligação ao Slack")
    lista = Pedido.objects.get(titulo__startswith="Lista de pedidos")
    roadmap.criar_dependencia(pedido=slack, depende_de=lista, autor=diogo)


class Command(BaseCommand):
    help = "Cria utilizadores de teste e pedidos de exemplo (só para desenvolvimento)."

    def handle(self, *args, **options):
        pessoas = {}
        for nome, papel in UTILIZADORES:
            u, _ = Utilizador.objects.get_or_create(username=nome, defaults={"papel": papel})
            # Repõe sempre a palavra-passe, para quem já tinha a base de dados criada.
            u.set_password(palavra_passe_teste(nome))
            u.save()
            pessoas[nome] = u

        admin, _ = Utilizador.objects.get_or_create(
            username="admin", defaults={"papel": Papel.PRODUCT_MANAGER, "is_staff": True, "is_superuser": True}
        )
        admin.set_password(palavra_passe_teste("admin"))
        admin.save()

        cats = {nome: Categoria.objects.get_or_create(nome=nome)[0] for nome in CATEGORIAS}

        if Pedido.objects.exists():
            self.stdout.write("Já há pedidos; não criei mais.")
            return
        for titulo, descricao, cat, etiquetas in PEDIDOS:
            pedido = servicos.criar_pedido(
                autor=pessoas["sofia"], titulo=titulo, descricao=descricao, categoria=cats[cat]
            )
            servicos.classificar(pedido=pedido, autor=pessoas["marta"], etiquetas=etiquetas)

        primeiro = Pedido.objects.get(titulo__startswith="Exportação")
        servicos.mudar_estado(pedido=primeiro, para=Estado.EM_ANALISE, autor=pessoas["marta"])
        for nome in ["marta", "diogo", "helena"]:
            servicos.alternar_voto(pedido=primeiro, utilizador=pessoas[nome])
        planear(pessoas)
        planear_releases(pessoas["marta"], pessoas["diogo"])
        nomes = ", ".join(pessoas)
        self.stdout.write(self.style.SUCCESS(f"Pronto. Utilizadores: {nomes} e admin (palavra-passe: nome + 123)."))
