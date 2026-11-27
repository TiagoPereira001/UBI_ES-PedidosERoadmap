from django.contrib import admin

from .models import Criterio, Ligacao, UserStory


class CriterioEmLinha(admin.TabularInline):
    model = Criterio
    extra = 0


class LigacaoEmLinha(admin.TabularInline):
    model = Ligacao
    extra = 0


@admin.register(UserStory)
class UserStoryAdmin(admin.ModelAdmin):
    list_display = ["texto", "pedido", "origem", "aceite_por", "aceite_em"]
    list_filter = ["origem"]
    inlines = [CriterioEmLinha, LigacaoEmLinha]
