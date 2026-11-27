from django.contrib import admin

from .models import Criterio, UserStory


class CriterioEmLinha(admin.TabularInline):
    model = Criterio
    extra = 0


@admin.register(UserStory)
class UserStoryAdmin(admin.ModelAdmin):
    list_display = ["texto", "pedido", "origem", "aceite_por", "aceite_em"]
    list_filter = ["origem"]
    inlines = [CriterioEmLinha]
