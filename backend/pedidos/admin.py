from django.contrib import admin

from .models import Categoria, Etiqueta, MudancaEstado, Pedido, VersaoPedido, Voto


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ["titulo", "categoria", "estado", "origem", "autor", "criado_em"]
    list_filter = ["estado", "categoria", "origem"]
    search_fields = ["titulo", "descricao"]


@admin.register(VersaoPedido)
class VersaoPedidoAdmin(admin.ModelAdmin):
    list_display = ["pedido", "titulo", "autor", "quando"]
    list_filter = ["quando"]
    search_fields = ["titulo", "descricao"]


admin.site.register(Categoria)
admin.site.register(Etiqueta)
admin.site.register(Voto)
admin.site.register(MudancaEstado)
