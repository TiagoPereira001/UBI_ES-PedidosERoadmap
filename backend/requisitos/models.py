from django.conf import settings
from django.db import models

from pedidos.models import Pedido


class Origem(models.TextChoices):
    """De onde veio o texto da user story, para se saber o que foi a IA a escrever."""

    IA = "ia", "IA"
    LOCAL = "local", "Modelo local"
    MANUAL = "manual", "Escrita à mão"


class UserStory(models.Model):
    """User story aceite pelo Product Owner a partir de um pedido (US-18).

    As propostas não se guardam: só fica o que o Product Owner aceitou, já com as edições dele.
    """

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="user_stories")
    texto = models.TextField(help_text="Como..., quero..., para...")
    origem = models.CharField(max_length=10, choices=Origem.choices)
    aceite_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    aceite_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["aceite_em", "id"]

    def __str__(self):
        return self.texto[:60]


class Criterio(models.Model):
    """Critério de aceitação de uma user story. Marca-se como cumprido quando se verifica."""

    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE, related_name="criterios")
    texto = models.CharField(max_length=200)
    cumprido = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.texto
