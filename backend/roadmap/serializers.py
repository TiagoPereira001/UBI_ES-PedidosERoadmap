from rest_framework import serializers

from . import servicos
from .models import Release


class PedidoDaRelease(serializers.Serializer):
    id = serializers.IntegerField()
    titulo = serializers.CharField()
    estado = serializers.CharField()
    estado_nome = serializers.CharField(source="get_estado_display")


class ReleaseSerializer(serializers.ModelSerializer):
    estado = serializers.SerializerMethodField()
    progresso = serializers.SerializerMethodField()
    em_risco = serializers.SerializerMethodField()
    pedidos = PedidoDaRelease(many=True, read_only=True)

    class Meta:
        model = Release
        fields = [
            "id", "nome", "objetivo", "inicio", "data_prevista", "lancada_em",
            "estado", "progresso", "em_risco", "pedidos",
        ]
        read_only_fields = ["lancada_em"]

    def get_estado(self, release):
        return servicos.estado(release)

    def get_progresso(self, release):
        return servicos.progresso(release)

    def get_em_risco(self, release):
        return servicos.em_risco(release)


class PedidoSerializer(serializers.Serializer):
    pedido = serializers.IntegerField()
