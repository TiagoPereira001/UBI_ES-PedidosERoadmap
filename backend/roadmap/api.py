from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from pedidos.models import Pedido
from pedidos.servicos import RegraViolada

from . import servicos
from .models import Dependencia, Milestone, Release
from .serializers import (
    DependenciaCriarSerializer,
    DependenciaSerializer,
    MilestoneEscreverSerializer,
    MilestoneMudarSerializer,
    MilestoneSerializer,
    PedidoSerializer,
    ReleaseDetalheSerializer,
    ReleaseSerializer,
)


def _pedidos_por_ids(ids):
    if not ids:
        return []
    encontrados = list(Pedido.objects.filter(pk__in=ids))
    if len(encontrados) != len(set(ids)):
        raise RegraViolada("Há um pedido que não existe.")
    return encontrados


class Roadmap(APIView):
    """O roadmap (ecrã 08): todas as releases, e criar uma nova (só o product manager)."""

    def get(self, request):
        return Response({"releases": ReleaseSerializer(servicos.roadmap(), many=True).data})

    def post(self, request):
        entrada = ReleaseSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        release = servicos.criar_release(autor=request.user, **entrada.validated_data)
        return Response(ReleaseSerializer(release).data, status=status.HTTP_201_CREATED)


class ReleaseDetalhe(APIView):
    def get(self, request, pk):
        release = generics.get_object_or_404(servicos.roadmap(), pk=pk)
        return Response(ReleaseDetalheSerializer(release).data)


class PedidosDaRelease(APIView):
    """Pôr um pedido aprovado numa release, ou tirá-lo."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        release = generics.get_object_or_404(Release, pk=pk)
        entrada = PedidoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        pedido = generics.get_object_or_404(Pedido, pk=entrada.validated_data["pedido"])
        servicos.por_na_release(release=release, pedido=pedido, autor=request.user)
        release = servicos.release_com_detalhe(pk)
        return Response(ReleaseDetalheSerializer(release).data)

    def delete(self, request, pk, pedido):
        release = generics.get_object_or_404(Release, pk=pk)
        alvo = generics.get_object_or_404(Pedido, pk=pedido)
        servicos.tirar_da_release(release=release, pedido=alvo, autor=request.user)
        release = servicos.release_com_detalhe(pk)
        return Response(ReleaseDetalheSerializer(release).data)


class LancarRelease(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        release = generics.get_object_or_404(Release, pk=pk)
        servicos.lancar_release(release=release, autor=request.user)
        return Response(ReleaseDetalheSerializer(servicos.release_com_detalhe(pk)).data)


class MilestoneLista(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entrada = MilestoneEscreverSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        dados = entrada.validated_data
        release = None
        if "release" in dados and dados["release"] is not None:
            release = generics.get_object_or_404(Release, pk=dados["release"])
        pedidos = _pedidos_por_ids(dados.get("pedidos") or [])
        milestone = servicos.criar_milestone(
            autor=request.user,
            nome=dados["nome"],
            data=dados["data"],
            release=release,
            pedidos=pedidos or None,
        )
        milestone = Milestone.objects.prefetch_related("pedidos").get(pk=milestone.pk)
        return Response(MilestoneSerializer(milestone).data, status=status.HTTP_201_CREATED)


class MilestoneDetalhe(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        milestone = generics.get_object_or_404(Milestone, pk=pk)
        entrada = MilestoneMudarSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        dados = entrada.validated_data
        kwargs = {}
        if "nome" in dados:
            kwargs["nome"] = dados["nome"]
        if "data" in dados:
            kwargs["data"] = dados["data"]
        if "release" in dados:
            if dados["release"] is None:
                kwargs["limpar_release"] = True
            else:
                kwargs["release"] = generics.get_object_or_404(Release, pk=dados["release"])
        if "pedidos" in dados:
            kwargs["pedidos"] = _pedidos_por_ids(dados["pedidos"])
        servicos.mudar_milestone(milestone=milestone, autor=request.user, **kwargs)
        milestone = Milestone.objects.prefetch_related("pedidos").get(pk=pk)
        return Response(MilestoneSerializer(milestone).data)

    def delete(self, request, pk):
        milestone = generics.get_object_or_404(Milestone, pk=pk)
        servicos.apagar_milestone(milestone=milestone, autor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PedidosDoMilestone(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        milestone = generics.get_object_or_404(Milestone, pk=pk)
        entrada = PedidoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        pedido = generics.get_object_or_404(Pedido, pk=entrada.validated_data["pedido"])
        servicos.por_no_milestone(milestone=milestone, pedido=pedido, autor=request.user)
        milestone = Milestone.objects.prefetch_related("pedidos").get(pk=pk)
        return Response(MilestoneSerializer(milestone).data)

    def delete(self, request, pk, pedido):
        milestone = generics.get_object_or_404(Milestone, pk=pk)
        alvo = generics.get_object_or_404(Pedido, pk=pedido)
        servicos.tirar_do_milestone(milestone=milestone, pedido=alvo, autor=request.user)
        milestone = Milestone.objects.prefetch_related("pedidos").get(pk=pk)
        return Response(MilestoneSerializer(milestone).data)


class DependenciaLista(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entrada = DependenciaCriarSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        pedido = generics.get_object_or_404(Pedido, pk=entrada.validated_data["pedido"])
        depende_de = generics.get_object_or_404(Pedido, pk=entrada.validated_data["depende_de"])
        dependencia = servicos.criar_dependencia(pedido=pedido, depende_de=depende_de, autor=request.user)
        dependencia = Dependencia.objects.select_related("pedido", "depende_de", "criada_por").get(
            pk=dependencia.pk
        )
        return Response(DependenciaSerializer(dependencia).data, status=status.HTTP_201_CREATED)


class DependenciaDetalhe(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        dependencia = generics.get_object_or_404(Dependencia, pk=pk)
        servicos.apagar_dependencia(dependencia=dependencia, autor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
