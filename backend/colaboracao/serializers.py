from rest_framework import serializers

from .models import Comentario, MensagemEquipa, Notificacao, Preferencias


class ComentarioSerializer(serializers.ModelSerializer):
    autor = serializers.CharField(source="autor.username", read_only=True)
    meu = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = ["id", "autor", "texto", "criado_em", "editado_em", "meu"]
        read_only_fields = ["criado_em", "editado_em"]

    def get_meu(self, comentario):
        utilizador = self.context["request"].user
        return utilizador.is_authenticated and comentario.autor_id == utilizador.pk


class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = ["id", "pedido", "tipo", "texto", "criada_em", "lida"]


class PreferenciasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferencias
        fields = ["estados", "mencoes", "comentarios", "email"]


class LidasSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)


class MembroSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    papel = serializers.CharField()
    papel_nome = serializers.CharField(source="get_papel_display")


class TrabalhoSerializer(serializers.Serializer):
    pedido = serializers.IntegerField(source="pedido.id")
    titulo = serializers.CharField(source="pedido.titulo")
    estado = serializers.CharField(source="pedido.estado")
    estado_nome = serializers.CharField(source="pedido.get_estado_display")
    sprint = serializers.CharField(source="sprint.nome", default=None)


class MensagemSerializer(serializers.ModelSerializer):
    autor = serializers.CharField(source="autor.username", read_only=True)

    class Meta:
        model = MensagemEquipa
        fields = ["id", "autor", "texto", "criada_em"]
