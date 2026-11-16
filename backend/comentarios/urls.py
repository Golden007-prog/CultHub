from django.urls import path

from comentarios.views import (
    ComentariosDoEventoView,
    ComentarioView,
    MeusComentariosView,
    RespostasView,
)

urlpatterns = [
    path(
        "eventos/<uuid:pk>/comentarios/",
        ComentariosDoEventoView.as_view(),
        name="evento-comentarios",
    ),
    path(
        "comentarios/<uuid:pk>/respostas/",
        RespostasView.as_view(),
        name="comentario-respostas",
    ),
    path(
        "comentarios/<uuid:pk>/",
        ComentarioView.as_view(),
        name="comentario",
    ),
    path(
        "eu/comentarios/", MeusComentariosView.as_view(), name="eu-comentarios"
    ),
]
