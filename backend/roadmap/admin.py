from django.contrib import admin

from .models import Release


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ["nome", "inicio", "data_prevista", "lancada_em"]
    filter_horizontal = ["pedidos"]
