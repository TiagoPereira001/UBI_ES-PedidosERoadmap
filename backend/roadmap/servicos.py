"""Regras do roadmap, releases, milestones e dependências (US-14 a US-17).

Quem planeia as releases e os milestones é o product manager (a Marta).
Dependências: programador e product manager. Os outros veem o roadmap.
"""

from datetime import date, timedelta

from django.db import transaction

from contas.models import Papel
from pedidos.models import Estado, Pedido
from pedidos.servicos import RegraViolada, exigir_papel

from .models import Dependencia, Milestone, Release

# Uma release fica "em risco" quando faltam estes dias (ou menos) e ainda tem pedidos por concluir.
DIAS_DE_AVISO = 14

# Só entram numa release pedidos que já foram aprovados.
ESTADOS_QUE_ENTRAM = [Estado.APROVADO, Estado.EM_DESENVOLVIMENTO, Estado.EM_REVISAO, Estado.CONCLUIDO]

QUEM_DEPENDENCIA = {Papel.PROGRAMADOR, Papel.PRODUCT_MANAGER}

# Pedidos já em curso (ou feitos) fazem o milestone passar de "por começar".
ESTADOS_EM_CURSO = {Estado.EM_DESENVOLVIMENTO, Estado.EM_REVISAO, Estado.CONCLUIDO}


def estado(release, hoje=None):
    hoje = hoje or date.today()
    if release.lancada_em:
        return "lancada"
    return "em_curso" if release.inicio <= hoje else "planeada"


def exigir_release_nao_lancada(release):
    if release.lancada_em:
        raise RegraViolada("Esta release já foi lançada.")


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
    # list(...all()) aproveita o prefetch do roadmap; exclude().exists() faria N+1.
    por_fazer = any(p.estado != Estado.CONCLUIDO for p in release.pedidos.all())
    return por_fazer and release.data_prevista - hoje <= timedelta(days=DIAS_DE_AVISO)


def estado_milestone(milestone):
    """por_comecar / em_curso / concluido — tirado dos pedidos, não guardado."""
    pedidos = list(milestone.pedidos.all())
    if not pedidos:
        return "por_comecar"
    if all(p.estado == Estado.CONCLUIDO for p in pedidos):
        return "concluido"
    if any(p.estado in ESTADOS_EM_CURSO for p in pedidos):
        return "em_curso"
    return "por_comecar"


@transaction.atomic
def criar_release(*, autor, nome, inicio, data_prevista, objetivo=""):
    exigir_papel(autor, {Papel.PRODUCT_MANAGER}, "Só o product manager pode criar releases.")
    if data_prevista <= inicio:
        raise RegraViolada("A data prevista tem de ser depois do início.")
    if Release.objects.filter(nome__iexact=nome.strip()).exists():
        raise RegraViolada("Já há uma release com esse nome.")
    return Release.objects.create(
        nome=nome.strip(), inicio=inicio, data_prevista=data_prevista, objetivo=objetivo.strip()
    )


@transaction.atomic
def por_na_release(*, release, pedido, autor):
    exigir_papel(autor, {Papel.PRODUCT_MANAGER}, "Só o product manager pode planear releases.")
    exigir_release_nao_lancada(release)
    if pedido.estado not in ESTADOS_QUE_ENTRAM:
        raise RegraViolada("Só os pedidos aprovados entram numa release.")
    release.pedidos.add(pedido)


@transaction.atomic
def tirar_da_release(*, release, pedido, autor):
    exigir_papel(autor, {Papel.PRODUCT_MANAGER}, "Só o product manager pode planear releases.")
    exigir_release_nao_lancada(release)
    release.pedidos.remove(pedido)


@transaction.atomic
def lancar_release(*, release, autor, hoje=None):
    """Marca a release como lançada. Só se lança quando todos os pedidos estão concluídos."""
    exigir_papel(autor, {Papel.PRODUCT_MANAGER}, "Só o product manager pode lançar releases.")
    exigir_release_nao_lancada(release)
    if release.pedidos.exclude(estado=Estado.CONCLUIDO).exists():
        raise RegraViolada("Ainda há pedidos por concluir nesta release.")
    release.lancada_em = hoje or date.today()
    release.save(update_fields=["lancada_em"])
    return release


def roadmap():
    """Todas as releases pela data prevista, com pedidos e milestones já carregados."""
    return Release.objects.prefetch_related("pedidos", "milestones__pedidos")


def release_com_detalhe(pk):
    """Uma release com pedidos e milestones prontos para o ecrã 09."""
    return roadmap().get(pk=pk)


def pedidos_que_entram():
    """Pedidos que podem ir para uma release, pelo título (para os selects do ecrã 09)."""
    return Pedido.objects.filter(estado__in=ESTADOS_QUE_ENTRAM).order_by("titulo")


@transaction.atomic
def criar_milestone(*, autor, nome, data, release=None, pedidos=None):
    exigir_papel(autor, {Papel.PRODUCT_MANAGER}, "Só o product manager pode criar milestones.")
    milestone = Milestone.objects.create(nome=nome.strip(), data=data, release=release)
    if pedidos:
        milestone.pedidos.set(pedidos)
    return milestone


@transaction.atomic
def mudar_milestone(*, milestone, autor, nome=None, data=None, limpar_release=False, release=None, pedidos=None):
    exigir_papel(autor, {Papel.PRODUCT_MANAGER}, "Só o product manager pode mudar milestones.")
    campos = []
    if nome is not None:
        milestone.nome = nome.strip()
        campos.append("nome")
    if data is not None:
        milestone.data = data
        campos.append("data")
    if limpar_release:
        milestone.release = None
        campos.append("release")
    elif release is not None:
        milestone.release = release
        campos.append("release")
    if campos:
        milestone.save(update_fields=campos)
    if pedidos is not None:
        milestone.pedidos.set(pedidos)
    return milestone


@transaction.atomic
def apagar_milestone(*, milestone, autor):
    exigir_papel(autor, {Papel.PRODUCT_MANAGER}, "Só o product manager pode apagar milestones.")
    milestone.delete()


@transaction.atomic
def por_no_milestone(*, milestone, pedido, autor):
    exigir_papel(autor, {Papel.PRODUCT_MANAGER}, "Só o product manager pode mudar milestones.")
    milestone.pedidos.add(pedido)


@transaction.atomic
def tirar_do_milestone(*, milestone, pedido, autor):
    exigir_papel(autor, {Papel.PRODUCT_MANAGER}, "Só o product manager pode mudar milestones.")
    milestone.pedidos.remove(pedido)


def _ids_do_grafo(raiz_ids):
    """Todos os pedidos ligados por dependências a partir destes ids (para os bloquear juntos)."""
    vistos = set(raiz_ids)
    fila = list(raiz_ids)
    while fila:
        atual = fila.pop()
        ligados = Dependencia.objects.filter(pedido_id=atual).values_list("depende_de_id", flat=True)
        ligados = list(ligados) + list(
            Dependencia.objects.filter(depende_de_id=atual).values_list("pedido_id", flat=True)
        )
        for outro in ligados:
            if outro not in vistos:
                vistos.add(outro)
                fila.append(outro)
    return vistos


def _ha_caminho(*, de, ate):
    """Segue pedido → depende_de. True se `de` chega a `ate` (ciclo se formos acrescentar ate→de)."""
    vistos = set()
    fila = [de]
    while fila:
        atual = fila.pop()
        if atual == ate:
            return True
        if atual in vistos:
            continue
        vistos.add(atual)
        fila.extend(Dependencia.objects.filter(pedido_id=atual).values_list("depende_de_id", flat=True))
    return False


@transaction.atomic
def criar_dependencia(*, pedido, depende_de, autor):
    exigir_papel(autor, QUEM_DEPENDENCIA, "Só o programador ou o product manager registam dependências.")
    if pedido.id == depende_de.id:
        raise RegraViolada("Um pedido não pode depender de si próprio.")

    # Bloqueia os dois e todo o grafo à volta, por ordem de id, e só depois verifica o ciclo.
    relacionados = _ids_do_grafo([pedido.id, depende_de.id])
    list(Pedido.objects.select_for_update().filter(pk__in=sorted(relacionados)).order_by("pk"))

    if Dependencia.objects.filter(pedido=pedido, depende_de=depende_de).exists():
        raise RegraViolada("Essa dependência já existe.")
    if _ha_caminho(de=depende_de.id, ate=pedido.id):
        raise RegraViolada("Essa dependência formaria um ciclo (direto ou indireto).")

    return Dependencia.objects.create(pedido=pedido, depende_de=depende_de, criada_por=autor)


@transaction.atomic
def apagar_dependencia(*, dependencia, autor):
    exigir_papel(autor, QUEM_DEPENDENCIA, "Só o programador ou o product manager apagam dependências.")
    dependencia.delete()


def dependencias_da_release(release):
    """Dependências em que entra pelo menos um pedido desta release."""
    ids = list(release.pedidos.values_list("id", flat=True))
    if not ids:
        return Dependencia.objects.none()
    return (
        Dependencia.objects.filter(pedido_id__in=ids)
        .select_related("pedido", "depende_de", "criada_por")
        .order_by("id")
    )


def avisos_dependencias(release):
    """Pedidos desta release que dependem de outro sem data útil e ainda por concluir."""
    ids_nesta = set(release.pedidos.values_list("id", flat=True))
    avisos = []
    deps = (
        Dependencia.objects.filter(pedido_id__in=ids_nesta)
        .select_related("pedido", "depende_de")
        .prefetch_related("depende_de__releases")
    )
    for dep in deps:
        alvo = dep.depende_de
        if alvo.estado == Estado.CONCLUIDO:
            continue
        if alvo.id in ids_nesta:
            continue
        acaba_antes = any(r.data_prevista < release.data_prevista for r in alvo.releases.all())
        if acaba_antes:
            continue
        avisos.append(
            {
                "pedido_id": dep.pedido_id,
                "pedido_titulo": dep.pedido.titulo,
                "depende_de_id": alvo.id,
                "depende_de_titulo": alvo.titulo,
                "mensagem": (
                    f"{dep.pedido.titulo} depende de {alvo.titulo}, que não está nesta release "
                    "nem noutra que acabe antes, e ainda não está concluído."
                ),
            }
        )
    return avisos
