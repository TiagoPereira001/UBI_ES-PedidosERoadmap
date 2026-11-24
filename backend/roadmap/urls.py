from django.urls import path

from . import api

urlpatterns = [
    path("", api.Roadmap.as_view(), name="roadmap"),
    path("releases/<int:pk>/", api.ReleaseDetalhe.as_view(), name="release"),
    path("releases/<int:pk>/pedidos/", api.PedidosDaRelease.as_view(), name="release-pedidos"),
    path("releases/<int:pk>/pedidos/<int:pedido>/", api.PedidosDaRelease.as_view(), name="release-pedido"),
    path("releases/<int:pk>/lancar/", api.LancarRelease.as_view(), name="release-lancar"),
]
