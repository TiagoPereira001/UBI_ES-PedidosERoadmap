from django.contrib import admin

from .models import Dependencia, Milestone, Release


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ["nome", "inicio", "data_prevista", "lancada_em"]
    filter_horizontal = ["pedidos"]


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ["nome", "data", "release"]
    list_filter = ["data"]
    filter_horizontal = ["pedidos"]
    search_fields = ["nome"]


@admin.register(Dependencia)
class DependenciaAdmin(admin.ModelAdmin):
    list_display = ["pedido", "depende_de", "criada_por", "criada_em"]
    search_fields = ["pedido__titulo", "depende_de__titulo"]
