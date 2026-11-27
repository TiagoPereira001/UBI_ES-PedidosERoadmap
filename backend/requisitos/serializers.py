from django.core.validators import URLValidator
from rest_framework import serializers

from . import servicos
from .models import Criterio, Ligacao, Origem, UserStory


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


class LigacaoSerializer(serializers.ModelSerializer):
    # O DRF não usa o validador do modelo num URLField, por isso repete-se aqui.
    url = serializers.URLField(max_length=200, validators=[URLValidator(schemes=["https"])])
    criada_por = serializers.CharField(source="criada_por.username", read_only=True)

    class Meta:
        model = Ligacao
        fields = ["id", "url", "descricao", "criada_por", "criada_em"]


class HistoriaLigada(UserStorySerializer):
    ligacoes = LigacaoSerializer(many=True, read_only=True)

    class Meta(UserStorySerializer.Meta):
        fields = [*UserStorySerializer.Meta.fields, "ligacoes"]


class CriterioCumprido(serializers.Serializer):
    cumprido = serializers.BooleanField()


class CadeiaSerializer(serializers.Serializer):
    """Uma linha da rastreabilidade: de onde veio o pedido e onde foi feito."""

    id = serializers.IntegerField()
    titulo = serializers.CharField()
    autor = serializers.CharField(source="autor.username")
    criado_em = serializers.DateTimeField()
    estado = serializers.CharField()
    estado_nome = serializers.CharField(source="get_estado_display")
    historias = HistoriaLigada(source="user_stories", many=True)
    sprint = serializers.CharField(source="item_backlog.sprint.nome", default=None)
    equipa = serializers.CharField(source="item_backlog.equipa.nome", default=None)
    releases = serializers.SerializerMethodField()
    falta = serializers.SerializerMethodField()

    def get_releases(self, pedido):
        return [r.nome for r in pedido.releases.all()]

    def get_falta(self, pedido):
        return servicos.em_falta(pedido)
