from django.contrib import admin

from comentarios.models import Comentario


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    """Consulta e moderação; comentários são escritos pela API."""

    list_display = ("__str__", "nivel", "criado_em", "removido_em")
    list_filter = ("removido_em",)
    search_fields = ("texto", "autor__email", "evento__titulo")
    list_select_related = ("autor", "evento")
    readonly_fields = (
        "evento",
        "autor",
        "resposta_a",
        "nivel",
        "criado_em",
        "editado_em",
    )

    def has_add_permission(self, request):
        return False
