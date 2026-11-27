"""Regras das user stories e dos critérios de aceitação (US-18).

Quem gera e aceita user stories é o Product Owner (o Ricardo). Toda a gente as pode ler.
"""

from django.db import transaction

from contas.models import Papel
from pedidos.models import Estado, Pedido
from pedidos.servicos import RegraViolada, SemPermissao

from . import gerar
from .models import Criterio, Origem, UserStory

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
