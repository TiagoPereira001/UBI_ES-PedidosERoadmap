from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from pedidos.models import Pedido
from pedidos.servicos import RegraViolada, SemPermissao

from . import servicos
from .serializers import AceitarSerializer, PedidoComHistorias, UserStorySerializer


def erro(falha):
    codigo = status.HTTP_403_FORBIDDEN if isinstance(falha, SemPermissao) else status.HTTP_400_BAD_REQUEST
    return Response({"erro": str(falha)}, status=codigo)


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
        try:
            historia = servicos.aceitar(pedido=alvo, autor=request.user, **entrada.validated_data)
        except (SemPermissao, RegraViolada) as falha:
            return erro(falha)
        return Response(UserStorySerializer(historia).data, status=status.HTTP_201_CREATED)


class Propostas(APIView):
    """Gera propostas de user stories. É um POST porque pode chamar um serviço de IA, que custa."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pedido):
        alvo = generics.get_object_or_404(Pedido, pk=pedido)
        try:
            propostas, fonte, servico = servicos.propor(pedido=alvo, autor=request.user)
        except (SemPermissao, RegraViolada) as falha:
            return erro(falha)
        return Response({"fonte": fonte, "servico": servico, "propostas": propostas})
