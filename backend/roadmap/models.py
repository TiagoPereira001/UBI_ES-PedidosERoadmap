from django.conf import settings
from django.db import models

from pedidos.models import Pedido


class Release(models.Model):
    """Uma entrega com data prevista e os pedidos que leva (US-14, US-15).

    O estado (planeada, em curso ou lançada) não se guarda: tira-se das datas, para não ficar desatualizado.
    """

    nome = models.CharField(max_length=60, unique=True)
    objetivo = models.TextField(blank=True)
    inicio = models.DateField()
    data_prevista = models.DateField()
    lancada_em = models.DateField(null=True, blank=True)
    pedidos = models.ManyToManyField(Pedido, blank=True, related_name="releases")

    class Meta:
        ordering = ["data_prevista", "id"]

    def __str__(self):
        return self.nome


class Milestone(models.Model):
    """Marco no roadmap (US-16). O estado não se guarda: calcula-se dos pedidos."""

    nome = models.CharField(max_length=80)
    data = models.DateField()
    release = models.ForeignKey(
        Release, null=True, blank=True, on_delete=models.CASCADE, related_name="milestones"
    )
    pedidos = models.ManyToManyField(Pedido, blank=True, related_name="milestones")

    class Meta:
        ordering = ["data", "id"]

    def __str__(self):
        return self.nome


class Dependencia(models.Model):
    """O pedido depende de depende_de (US-17). Única por par; nunca se criam ciclos."""

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="dependencias")
    depende_de = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="dependentes")
    criada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["pedido", "depende_de"], name="dependencia_unica"),
        ]
        ordering = ["id"]

    def __str__(self):
        return f"{self.pedido_id} → {self.depende_de_id}"
