"""Regras da colaboração: comentários, menções, notificações e o espaço de cada equipa (US-21 a US-24).

Os avisos de mudança de estado chegam por um sinal (sinais.py): o módulo Pedidos
não sabe que este módulo existe, e assim as dependências continuam num só sentido.
"""

import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from contas.models import Papel
from pedidos.servicos import RegraViolada, SemPermissao

from .models import Comentario, MembroEquipa, MensagemEquipa, Notificacao, Preferencias, TipoNotificacao

MENCAO = re.compile(r"@([\w.+-]+)")


def preferencias(utilizador):
    return Preferencias.objects.get_or_create(utilizador=utilizador)[0]


def seguidores(pedido):
    """Quem segue um pedido: quem o pediu, quem votou e quem comentou."""
    ids = {pedido.autor_id}
    ids |= set(pedido.votos.values_list("utilizador_id", flat=True))
    ids |= set(pedido.comentarios.values_list("autor_id", flat=True))
    return get_user_model().objects.filter(id__in=ids)


def notificar(*, utilizadores, pedido, tipo, texto, exceto=None):
    """Cria uma notificação para cada pessoa que a quer receber. Devolve quantas criou."""
    criadas = 0
    for pessoa in utilizadores:
        if exceto is not None and pessoa.pk == exceto.pk:
            continue
        prefs = preferencias(pessoa)
        if not prefs.quer(tipo):
            continue
        Notificacao.objects.create(utilizador=pessoa, pedido=pedido, tipo=tipo, texto=texto[:200])
        criadas += 1
        if prefs.email and pessoa.email:
            # Em desenvolvimento o email aparece no terminal do back-end (EMAIL_BACKEND em settings.py).
            send_mail("Pedidos e Roadmap", texto, settings.DEFAULT_FROM_EMAIL, [pessoa.email], fail_silently=True)
    return criadas


def mencionados(texto):
    nomes = {nome.rstrip(".") for nome in MENCAO.findall(texto)}
    return get_user_model().objects.filter(username__in=nomes)


@transaction.atomic
def comentar(*, pedido, autor, texto):
    """Grava o comentário, avisa quem foi mencionado e quem segue o pedido."""
    texto = texto.strip()
    if not texto:
        raise RegraViolada("O comentário está vazio.")
    comentario = Comentario.objects.create(pedido=pedido, autor=autor, texto=texto)
    nomeados = list(mencionados(texto))
    notificar(
        utilizadores=nomeados,
        pedido=pedido,
        tipo=TipoNotificacao.MENCAO,
        texto=f"{autor.username} mencionou-te em «{pedido.titulo}»",
        exceto=autor,
    )
    # Quem já foi avisado pela menção não recebe outro aviso pelo mesmo comentário.
    restantes = [p for p in seguidores(pedido) if p not in nomeados]
    notificar(
        utilizadores=restantes,
        pedido=pedido,
        tipo=TipoNotificacao.COMENTARIO,
        texto=f"{autor.username} comentou em «{pedido.titulo}»",
        exceto=autor,
    )
    return comentario


def _so_o_autor(comentario, utilizador):
    if comentario.autor_id != utilizador.pk:
        raise SemPermissao("Só quem escreveu o comentário o pode mudar ou apagar.")


@transaction.atomic
def editar(*, comentario, autor, texto):
    _so_o_autor(comentario, autor)
    if not texto.strip():
        raise RegraViolada("O comentário está vazio.")
    comentario.texto = texto.strip()
    comentario.editado_em = timezone.now()
    comentario.save(update_fields=["texto", "editado_em"])
    return comentario


@transaction.atomic
def apagar(*, comentario, autor):
    _so_o_autor(comentario, autor)
    comentario.delete()


def marcar_lidas(*, utilizador, ids=None):
    """Marca como lidas as notificações dadas, ou todas se não vier nenhuma."""
    por_ler = Notificacao.objects.filter(utilizador=utilizador, lida=False)
    if ids:
        por_ler = por_ler.filter(id__in=ids)
    return por_ler.update(lida=True)


# Espaço de cada equipa (US-24)


def membros(equipa):
    return get_user_model().objects.filter(equipas__equipa=equipa).order_by("username")


def pode_escrever(utilizador, equipa):
    """Escrevem na conversa da equipa os membros e o gestor de projeto."""
    if not utilizador.is_authenticated:
        return False
    return utilizador.papel == Papel.GESTOR_PROJETO or membros(equipa).filter(pk=utilizador.pk).exists()


def pode_gerir(utilizador):
    return utilizador.is_authenticated and utilizador.papel == Papel.GESTOR_PROJETO


@transaction.atomic
def escrever_na_equipa(*, equipa, autor, texto):
    if not pode_escrever(autor, equipa):
        raise SemPermissao("Só os membros da equipa e o gestor de projeto escrevem aqui.")
    texto = texto.strip()
    if not texto:
        raise RegraViolada("A mensagem está vazia.")
    return MensagemEquipa.objects.create(equipa=equipa, autor=autor, texto=texto)


@transaction.atomic
def juntar_a_equipa(*, equipa, utilizador, autor):
    """O gestor de projeto (a Helena) diz quem faz parte de cada equipa."""
    if not pode_gerir(autor):
        raise SemPermissao("Só o gestor de projeto muda quem faz parte das equipas.")
    return MembroEquipa.objects.get_or_create(equipa=equipa, utilizador=utilizador)[0]
