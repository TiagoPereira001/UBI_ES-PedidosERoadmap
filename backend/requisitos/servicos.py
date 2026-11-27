"""Regras das user stories, dos critérios de aceitação (US-18) e da rastreabilidade (US-19).

Quem gera e aceita user stories, e marca critérios, é o Product Owner (o Ricardo). Quem liga o código
é o programador (o Diogo). Toda a gente pode ler.
"""

from django.db import transaction

from contas.models import Papel
from pedidos.models import Estado, Pedido
from pedidos.servicos import RegraViolada, SemPermissao

from . import gerar
from .models import Criterio, Ligacao, Origem, UserStory

# Só se escrevem user stories de pedidos que já foram aprovados.
ESTADOS_COM_HISTORIAS = [Estado.APROVADO, Estado.EM_DESENVOLVIMENTO, Estado.EM_REVISAO, Estado.CONCLUIDO]


def _so_product_owner(autor, acao):
    if autor.papel != Papel.PRODUCT_OWNER:
        raise SemPermissao(f"Só o Product Owner pode {acao}.")


def _aprovado(pedido):
    if pedido.estado not in ESTADOS_COM_HISTORIAS:
        raise RegraViolada("Só se escrevem user stories de pedidos aprovados.")


def pedidos_com_historias():
    """Os pedidos de onde se podem gerar user stories, com quantas já têm."""
    return Pedido.objects.filter(estado__in=ESTADOS_COM_HISTORIAS).prefetch_related("user_stories").order_by("titulo")


def propor(*, pedido, autor):
    _so_product_owner(autor, "gerar user stories")
    _aprovado(pedido)
    return gerar.propor(pedido)


@transaction.atomic
def aceitar(*, pedido, autor, texto, criterios, origem=Origem.MANUAL):
    """Guarda a user story que o Product Owner aceitou (com as edições dele) e os critérios."""
    _so_product_owner(autor, "aceitar user stories")
    _aprovado(pedido)
    texto = texto.strip()
    criterios = [c.strip() for c in criterios if c.strip()]
    if not texto.startswith("Como "):
        raise RegraViolada("Uma user story começa por «Como...»: quem quer, o quê e para quê.")
    if not criterios:
        raise RegraViolada("Uma user story precisa de pelo menos um critério de aceitação.")
    historia = UserStory.objects.create(pedido=pedido, texto=texto, origem=origem, aceite_por=autor)
    Criterio.objects.bulk_create([Criterio(user_story=historia, texto=c[:200]) for c in criterios])
    return historia


@transaction.atomic
def marcar_criterio(*, criterio, autor, cumprido):
    _so_product_owner(autor, "marcar critérios")
    criterio.cumprido = cumprido
    criterio.save(update_fields=["cumprido"])
    return criterio


@transaction.atomic
def ligar_codigo(*, historia, autor, url, descricao):
    """Liga uma user story ao commit ou ao pull request onde foi feita."""
    if autor.papel not in (Papel.PROGRAMADOR, Papel.PRODUCT_OWNER):
        raise SemPermissao("Só o programador ou o Product Owner ligam o código.")
    if historia.ligacoes.filter(url=url).exists():
        raise RegraViolada("Essa ligação já existe nesta user story.")
    return Ligacao.objects.create(user_story=historia, url=url, descricao=descricao.strip(), criada_por=autor)


def em_falta(pedido):
    """O que falta ligar neste pedido, para a Helena ver onde a cadeia se parte."""
    historias = list(pedido.user_stories.all())
    if not historias:
        return ["Sem user stories"]
    falta = []
    item = getattr(pedido, "item_backlog", None)
    if not item or not item.sprint:
        falta.append("Fora de qualquer sprint")
    acabado = pedido.estado in (Estado.EM_REVISAO, Estado.CONCLUIDO)
    if acabado and any(not h.ligacoes.all() for h in historias):
        falta.append("User story sem ligação ao código")
    return falta


def rastreabilidade():
    """Pedido, user stories, sprint, código e release de tudo o que já foi aprovado, sem uma consulta por linha."""
    return (
        Pedido.objects.filter(estado__in=ESTADOS_COM_HISTORIAS)
        .select_related("autor", "item_backlog__sprint", "item_backlog__equipa")
        .prefetch_related("user_stories__criterios", "user_stories__aceite_por",
                          "user_stories__ligacoes__criada_por", "releases")
        .order_by("titulo")
    )
