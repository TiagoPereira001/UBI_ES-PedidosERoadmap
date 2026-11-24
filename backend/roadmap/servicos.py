"""Regras do roadmap e das releases (US-14 e US-15).

Quem planeia as releases é o product manager (a Marta). Os outros veem o roadmap.
"""

from datetime import date, timedelta

from django.db import transaction

from contas.models import Papel
from pedidos.models import Estado
from pedidos.servicos import RegraViolada, SemPermissao

from .models import Release

# Uma release fica "em risco" quando faltam estes dias (ou menos) e ainda tem pedidos por concluir.
DIAS_DE_AVISO = 14

# Só entram numa release pedidos que já foram aprovados.
ESTADOS_QUE_ENTRAM = [Estado.APROVADO, Estado.EM_DESENVOLVIMENTO, Estado.EM_REVISAO, Estado.CONCLUIDO]


def _so_product_manager(autor, acao):
    if autor.papel != Papel.PRODUCT_MANAGER:
        raise SemPermissao(f"Só o product manager pode {acao}.")


def estado(release, hoje=None):
    hoje = hoje or date.today()
    if release.lancada_em:
        return "lancada"
    return "em_curso" if release.inicio <= hoje else "planeada"


def progresso(release):
    """Percentagem de pedidos concluídos. Sem pedidos, 0."""
    pedidos = list(release.pedidos.all())
    if not pedidos:
        return 0
    feitos = sum(1 for p in pedidos if p.estado == Estado.CONCLUIDO)
    return round(100 * feitos / len(pedidos))


def em_risco(release, hoje=None):
    """Falta pouco para a data prevista (ou já passou) e ainda há pedidos por concluir."""
    hoje = hoje or date.today()
    if release.lancada_em:
        return False
    por_fazer = release.pedidos.exclude(estado=Estado.CONCLUIDO).exists()
    return por_fazer and release.data_prevista - hoje <= timedelta(days=DIAS_DE_AVISO)


@transaction.atomic
def criar_release(*, autor, nome, inicio, data_prevista, objetivo=""):
    _so_product_manager(autor, "criar releases")
    if data_prevista <= inicio:
        raise RegraViolada("A data prevista tem de ser depois do início.")
    if Release.objects.filter(nome__iexact=nome.strip()).exists():
        raise RegraViolada("Já há uma release com esse nome.")
    return Release.objects.create(
        nome=nome.strip(), inicio=inicio, data_prevista=data_prevista, objetivo=objetivo.strip()
    )


@transaction.atomic
def por_na_release(*, release, pedido, autor):
    _so_product_manager(autor, "planear releases")
    if release.lancada_em:
        raise RegraViolada("Esta release já foi lançada.")
    if pedido.estado not in ESTADOS_QUE_ENTRAM:
        raise RegraViolada("Só os pedidos aprovados entram numa release.")
    release.pedidos.add(pedido)


@transaction.atomic
def tirar_da_release(*, release, pedido, autor):
    _so_product_manager(autor, "planear releases")
    if release.lancada_em:
        raise RegraViolada("Esta release já foi lançada.")
    release.pedidos.remove(pedido)


@transaction.atomic
def lancar_release(*, release, autor, hoje=None):
    """Marca a release como lançada. Só se lança quando todos os pedidos estão concluídos."""
    _so_product_manager(autor, "lançar releases")
    if release.lancada_em:
        raise RegraViolada("Esta release já foi lançada.")
    if release.pedidos.exclude(estado=Estado.CONCLUIDO).exists():
        raise RegraViolada("Ainda há pedidos por concluir nesta release.")
    release.lancada_em = hoje or date.today()
    release.save(update_fields=["lancada_em"])
    return release


def roadmap():
    """Todas as releases pela data prevista, com os pedidos já carregados."""
    return Release.objects.prefetch_related("pedidos")
