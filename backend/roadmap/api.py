from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from pedidos.models import Pedido
from pedidos.servicos import RegraViolada, SemPermissao

from . import servicos
from .models import Release
from .serializers import PedidoSerializer, ReleaseSerializer


def erro(falha):
    codigo = status.HTTP_403_FORBIDDEN if isinstance(falha, SemPermissao) else status.HTTP_400_BAD_REQUEST
    return Response({"erro": str(falha)}, status=codigo)


class Roadmap(APIView):
    """O roadmap (ecrã 08): todas as releases, e criar uma nova (só o product manager)."""

    def get(self, request):
        return Response({"releases": ReleaseSerializer(servicos.roadmap(), many=True).data})

    def post(self, request):
        entrada = ReleaseSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        try:
            release = servicos.criar_release(autor=request.user, **entrada.validated_data)
        except (SemPermissao, RegraViolada) as falha:
            return erro(falha)
        return Response(ReleaseSerializer(release).data, status=status.HTTP_201_CREATED)


class ReleaseDetalhe(APIView):
    def get(self, request, pk):
        return Response(ReleaseSerializer(generics.get_object_or_404(Release, pk=pk)).data)


class PedidosDaRelease(APIView):
    """Pôr um pedido aprovado numa release, ou tirá-lo."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        release = generics.get_object_or_404(Release, pk=pk)
        entrada = PedidoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        pedido = generics.get_object_or_404(Pedido, pk=entrada.validated_data["pedido"])
        try:
            servicos.por_na_release(release=release, pedido=pedido, autor=request.user)
        except (SemPermissao, RegraViolada) as falha:
            return erro(falha)
        return Response(ReleaseSerializer(release).data)

    def delete(self, request, pk, pedido):
        release = generics.get_object_or_404(Release, pk=pk)
        alvo = generics.get_object_or_404(Pedido, pk=pedido)
        try:
            servicos.tirar_da_release(release=release, pedido=alvo, autor=request.user)
        except (SemPermissao, RegraViolada) as falha:
            return erro(falha)
        return Response(ReleaseSerializer(release).data)


class LancarRelease(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        release = generics.get_object_or_404(Release, pk=pk)
        try:
            servicos.lancar_release(release=release, autor=request.user)
        except (SemPermissao, RegraViolada) as falha:
            return erro(falha)
        return Response(ReleaseSerializer(release).data)
