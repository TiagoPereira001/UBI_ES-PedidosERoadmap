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
