from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from pedidos.models import Pedido
from . import servicos
from .models import Criterio, UserStory
from .serializers import (
    AceitarSerializer,
    CadeiaSerializer,
    CriterioCumprido,
    CriterioSerializer,
    LigacaoSerializer,
    PedidoComHistorias,
    UserStorySerializer,
)


class Pedidos(APIView):
    """Os pedidos aprovados de onde se geram user stories (ecrã 10)."""

    def get(self, request):
        return Response(PedidoComHistorias(servicos.pedidos_com_historias(), many=True).data)


class HistoriasDoPedido(APIView):
    """As user stories aceites de um pedido, e aceitar uma nova (só o Product Owner)."""

    def get(self, request, pedido):
        alvo = generics.get_object_or_404(Pedido, pk=pedido)
        historias = alvo.user_stories.prefetch_related("criterios")
        return Response(
            {"pedido": PedidoComHistorias(alvo).data, "historias": UserStorySerializer(historias, many=True).data}
        )

    def post(self, request, pedido):
        alvo = generics.get_object_or_404(Pedido, pk=pedido)
        entrada = AceitarSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        historia = servicos.aceitar(pedido=alvo, autor=request.user, **entrada.validated_data)
        return Response(UserStorySerializer(historia).data, status=status.HTTP_201_CREATED)


class Propostas(APIView):
    """Gera propostas de user stories. É um POST porque pode chamar um serviço de IA, que custa."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pedido):
        alvo = generics.get_object_or_404(Pedido, pk=pedido)
        propostas, fonte, servico = servicos.propor(pedido=alvo, autor=request.user)
        return Response({"fonte": fonte, "servico": servico, "propostas": propostas})


class Rastreabilidade(APIView):
    """Do pedido ao código e à release, com o que falta ligar (ecrã 11, US-19)."""

    def get(self, request):
        return Response(CadeiaSerializer(servicos.rastreabilidade(), many=True).data)


class LigacoesDaHistoria(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        historia = generics.get_object_or_404(UserStory, pk=pk)
        entrada = LigacaoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        ligacao = servicos.ligar_codigo(historia=historia, autor=request.user, **entrada.validated_data)
        return Response(LigacaoSerializer(ligacao).data, status=status.HTTP_201_CREATED)


class CriterioDetalhe(APIView):
    """Marcar ou desmarcar um critério de aceitação como cumprido (só o Product Owner)."""

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        criterio = generics.get_object_or_404(Criterio, pk=pk)
        entrada = CriterioCumprido(data=request.data)
        entrada.is_valid(raise_exception=True)
        servicos.marcar_criterio(criterio=criterio, autor=request.user, **entrada.validated_data)
        return Response(CriterioSerializer(criterio).data)
