from rest_framework import serializers

from .models import Criterio, Origem, UserStory


class CriterioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criterio
        fields = ["id", "texto", "cumprido"]


class UserStorySerializer(serializers.ModelSerializer):
    criterios = CriterioSerializer(many=True, read_only=True)
    origem_nome = serializers.CharField(source="get_origem_display", read_only=True)
    aceite_por = serializers.CharField(source="aceite_por.username", read_only=True)

    class Meta:
        model = UserStory
        fields = ["id", "texto", "origem", "origem_nome", "aceite_por", "aceite_em", "criterios"]


class PedidoComHistorias(serializers.Serializer):
    id = serializers.IntegerField()
    titulo = serializers.CharField()
    descricao = serializers.CharField()
    estado = serializers.CharField()
    estado_nome = serializers.CharField(source="get_estado_display")
    total_historias = serializers.SerializerMethodField()

    def get_total_historias(self, pedido):
        return len(pedido.user_stories.all())


class AceitarSerializer(serializers.Serializer):
    texto = serializers.CharField()
    criterios = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    origem = serializers.ChoiceField(choices=Origem.choices, default=Origem.MANUAL)
