from rest_framework import serializers

from . import servicos
from .models import Dependencia, Milestone, Release


class PedidoDaRelease(serializers.Serializer):
    id = serializers.IntegerField()
    titulo = serializers.CharField()
    estado = serializers.CharField()
    estado_nome = serializers.CharField(source="get_estado_display")


class MilestoneResumoSerializer(serializers.ModelSerializer):
    estado = serializers.SerializerMethodField()

    class Meta:
        model = Milestone
        fields = ["id", "nome", "data", "estado"]

    def get_estado(self, milestone):
        return servicos.estado_milestone(milestone)


class MilestoneSerializer(serializers.ModelSerializer):
    estado = serializers.SerializerMethodField()
    pedidos = PedidoDaRelease(many=True, read_only=True)
    nome = serializers.CharField(max_length=80)
    release_id = serializers.IntegerField(source="release.id", read_only=True, allow_null=True)

    class Meta:
        model = Milestone
        fields = ["id", "nome", "data", "release_id", "estado", "pedidos"]

    def get_estado(self, milestone):
        return servicos.estado_milestone(milestone)


class MilestoneEscreverSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=80)
    data = serializers.DateField()
    release = serializers.IntegerField(required=False, allow_null=True)
    pedidos = serializers.ListField(child=serializers.IntegerField(), required=False)


class MilestoneMudarSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=80, required=False)
    data = serializers.DateField(required=False)
    release = serializers.IntegerField(required=False, allow_null=True)
    pedidos = serializers.ListField(child=serializers.IntegerField(), required=False)


class DependenciaSerializer(serializers.ModelSerializer):
    pedido_titulo = serializers.CharField(source="pedido.titulo", read_only=True)
    depende_de_titulo = serializers.CharField(source="depende_de.titulo", read_only=True)
    criada_por = serializers.CharField(source="criada_por.username", read_only=True)

    class Meta:
        model = Dependencia
        fields = ["id", "pedido", "pedido_titulo", "depende_de", "depende_de_titulo", "criada_por", "criada_em"]
        read_only_fields = ["criada_por", "criada_em"]


class DependenciaCriarSerializer(serializers.Serializer):
    pedido = serializers.IntegerField()
    depende_de = serializers.IntegerField()


class ReleaseSerializer(serializers.ModelSerializer):
    estado = serializers.SerializerMethodField()
    progresso = serializers.SerializerMethodField()
    em_risco = serializers.SerializerMethodField()
    pedidos = PedidoDaRelease(many=True, read_only=True)
    milestones = MilestoneResumoSerializer(many=True, read_only=True)
    nome = serializers.CharField(max_length=60)

    class Meta:
        model = Release
        fields = [
            "id", "nome", "objetivo", "inicio", "data_prevista", "lancada_em",
            "estado", "progresso", "em_risco", "pedidos", "milestones",
        ]
        read_only_fields = ["lancada_em"]

    def get_estado(self, release):
        return servicos.estado(release)

    def get_progresso(self, release):
        return servicos.progresso(release)

    def get_em_risco(self, release):
        return servicos.em_risco(release)


class AprovadoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    titulo = serializers.CharField()


class ReleaseDetalheSerializer(ReleaseSerializer):
    dependencias = serializers.SerializerMethodField()
    avisos = serializers.SerializerMethodField()
    aprovados = serializers.SerializerMethodField()
    milestones = MilestoneSerializer(many=True, read_only=True)

    class Meta(ReleaseSerializer.Meta):
        fields = ReleaseSerializer.Meta.fields + ["dependencias", "avisos", "aprovados"]

    def get_dependencias(self, release):
        return DependenciaSerializer(servicos.dependencias_da_release(release), many=True).data

    def get_avisos(self, release):
        return servicos.avisos_dependencias(release)

    def get_aprovados(self, release):
        return AprovadoSerializer(servicos.pedidos_que_entram(), many=True).data


class PedidoSerializer(serializers.Serializer):
    pedido = serializers.IntegerField()
