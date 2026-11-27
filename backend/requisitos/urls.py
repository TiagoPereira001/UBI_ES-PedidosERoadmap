from django.urls import path

from . import api

urlpatterns = [
    path("pedidos/", api.Pedidos.as_view(), name="requisitos-pedidos"),
    path("pedidos/<int:pedido>/historias/", api.HistoriasDoPedido.as_view(), name="historias"),
    path("pedidos/<int:pedido>/propostas/", api.Propostas.as_view(), name="propostas"),
    path("rastreabilidade/", api.Rastreabilidade.as_view(), name="rastreabilidade"),
    path("historias/<int:pk>/ligacoes/", api.LigacoesDaHistoria.as_view(), name="ligacoes"),
    path("criterios/<int:pk>/", api.CriterioDetalhe.as_view(), name="criterio"),
]
