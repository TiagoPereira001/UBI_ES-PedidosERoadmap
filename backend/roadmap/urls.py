from django.urls import path

from . import api

urlpatterns = [
    path("", api.Roadmap.as_view(), name="roadmap"),
    path("releases/<int:pk>/", api.ReleaseDetalhe.as_view(), name="release"),
    path("releases/<int:pk>/pedidos/", api.PedidosDaRelease.as_view(), name="release-pedidos"),
    path("releases/<int:pk>/pedidos/<int:pedido>/", api.PedidosDaRelease.as_view(), name="release-pedido"),
    path("releases/<int:pk>/lancar/", api.LancarRelease.as_view(), name="release-lancar"),
    path("milestones/", api.MilestoneLista.as_view(), name="milestones"),
    path("milestones/<int:pk>/", api.MilestoneDetalhe.as_view(), name="milestone"),
    path("milestones/<int:pk>/pedidos/", api.PedidosDoMilestone.as_view(), name="milestone-pedidos"),
    path(
        "milestones/<int:pk>/pedidos/<int:pedido>/",
        api.PedidosDoMilestone.as_view(),
        name="milestone-pedido",
    ),
    path("dependencias/", api.DependenciaLista.as_view(), name="dependencias"),
    path("dependencias/<int:pk>/", api.DependenciaDetalhe.as_view(), name="dependencia"),
]
