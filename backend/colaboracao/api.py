from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backlog import servicos as backlog
from backlog.models import Equipa
from pedidos.models import Pedido
from . import servicos
from .models import Comentario, Notificacao
from .serializers import (
    ComentarioSerializer,
    LidasSerializer,
    MembroSerializer,
    MensagemSerializer,
    NotificacaoSerializer,
    PreferenciasSerializer,
    TrabalhoSerializer,
)


class Comentarios(APIView):
    """A conversa de um pedido (US-21). Ler é para todos; escrever, para quem tem conta."""

    def get(self, request, pedido):
        comentarios = Comentario.objects.filter(pedido_id=pedido).select_related("autor")
        return Response(ComentarioSerializer(comentarios, many=True, context={"request": request}).data)

    def post(self, request, pedido):
        alvo = generics.get_object_or_404(Pedido, pk=pedido)
        comentario = servicos.comentar(pedido=alvo, autor=request.user, texto=request.data.get("texto", ""))
        dados = ComentarioSerializer(comentario, context={"request": request}).data
        return Response(dados, status=status.HTTP_201_CREATED)


class ComentarioDetalhe(APIView):
    """Só o autor edita ou apaga o seu comentário."""

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        comentario = generics.get_object_or_404(Comentario, pk=pk)
        servicos.editar(comentario=comentario, autor=request.user, texto=request.data.get("texto", ""))
        return Response(ComentarioSerializer(comentario, context={"request": request}).data)

    def delete(self, request, pk):
        comentario = generics.get_object_or_404(Comentario, pk=pk)
        servicos.apagar(comentario=comentario, autor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class Pessoas(APIView):
    """Nomes para as menções com @ (US-23)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        nomes = get_user_model().objects.filter(is_active=True).order_by("username").values_list("username", flat=True)
        return Response(list(nomes))


class Notificacoes(APIView):
    """As notificações de quem está autenticado, as mais recentes primeiro (US-22)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        minhas = Notificacao.objects.filter(utilizador=request.user)
        return Response(
            {
                "por_ler": minhas.filter(lida=False).count(),
                "itens": NotificacaoSerializer(minhas[:50], many=True).data,
            }
        )


class MarcarLidas(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entrada = LidasSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        servicos.marcar_lidas(utilizador=request.user, ids=entrada.validated_data["ids"])
        return Notificacoes().get(request)


class PreferenciasView(APIView):
    """O que cada um quer receber (US-22)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(PreferenciasSerializer(servicos.preferencias(request.user)).data)

    def put(self, request):
        entrada = PreferenciasSerializer(servicos.preferencias(request.user), data=request.data)
        entrada.is_valid(raise_exception=True)
        entrada.save()
        return Response(entrada.data)


def espaco(equipa, utilizador):
    return {
        "equipa": {"id": equipa.id, "nome": equipa.nome},
        "membros": MembroSerializer(servicos.membros(equipa), many=True).data,
        "trabalho": TrabalhoSerializer(backlog.itens_da_equipa(equipa), many=True).data,
        "mensagens": MensagemSerializer(equipa.mensagens.select_related("autor"), many=True).data,
        "pode_escrever": servicos.pode_escrever(utilizador, equipa),
        "pode_gerir": servicos.pode_gerir(utilizador),
    }


class EspacoEquipa(APIView):
    """O espaço de uma equipa (ecrã 13): quem lá está, o trabalho em curso e a conversa (US-24)."""

    def get(self, request, pk):
        return Response(espaco(generics.get_object_or_404(Equipa, pk=pk), request.user))


class MensagensEquipa(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        equipa = generics.get_object_or_404(Equipa, pk=pk)
        servicos.escrever_na_equipa(equipa=equipa, autor=request.user, texto=request.data.get("texto", ""))
        return Response(espaco(equipa, request.user), status=status.HTTP_201_CREATED)


class MembrosEquipa(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        equipa = generics.get_object_or_404(Equipa, pk=pk)
        pessoa = generics.get_object_or_404(get_user_model(), username=request.data.get("utilizador", ""))
        servicos.juntar_a_equipa(equipa=equipa, utilizador=pessoa, autor=request.user)
        return Response(espaco(equipa, request.user))
