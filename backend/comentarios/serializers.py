from rest_framework import serializers

from comentarios.models import TAMANHO_MAXIMO, Comentario


class AutorSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    nome = serializers.CharField()
    iniciais = serializers.CharField()


class ComentarioSerializer(serializers.ModelSerializer):
    """Comentário com as respostas visíveis aninhadas.

    Comentário removido aparece sem texto e sem autor, mas só enquanto tiver
    alguma resposta visível; sem elas, some da lista.
    """

    autor = serializers.SerializerMethodField()
    texto = serializers.SerializerMethodField()
    removido = serializers.BooleanField(read_only=True)
    meu = serializers.SerializerMethodField()
    respostas = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = (
            "id",
            "evento",
            "resposta_a",
            "nivel",
            "autor",
            "texto",
            "criado_em",
            "editado_em",
            "removido",
            "meu",
            "respostas",
        )

    def get_autor(self, obj) -> AutorSerializer(allow_null=True):
        if obj.removido or obj.autor is None:
            return None
        return AutorSerializer(obj.autor).data

    def get_texto(self, obj) -> str | None:
        return None if obj.removido else obj.texto

    def get_meu(self, obj) -> bool:
        usuario = self.context["request"].user
        return (
            not obj.removido
            and usuario.is_authenticated
            and obj.autor_id == usuario.pk
        )

    def get_respostas(self, obj) -> list[dict]:
        # Mesmo formato, recursivo; no schema fica como lista genérica.
        visiveis = [r for r in obj.respostas.all() if visivel(r)]
        return ComentarioSerializer(
            visiveis, many=True, context=self.context
        ).data


def visivel(comentario):
    """Não removido, ou removido mas com alguma resposta visível."""
    return not comentario.removido or any(
        visivel(resposta) for resposta in comentario.respostas.all()
    )


class TextoSerializer(serializers.Serializer):
    texto = serializers.CharField(
        max_length=TAMANHO_MAXIMO,
        trim_whitespace=True,
        error_messages={
            "blank": "Escreva algo antes de enviar.",
            "max_length": (
                f"O comentário pode ter até {TAMANHO_MAXIMO} caracteres."
            ),
        },
    )


class EventoResumoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    titulo = serializers.CharField()


class MeuComentarioSerializer(serializers.ModelSerializer):
    """Comentário na lista do autor, com o evento de onde ele veio."""

    evento = EventoResumoSerializer(read_only=True)

    class Meta:
        model = Comentario
        fields = (
            "id",
            "evento",
            "resposta_a",
            "nivel",
            "texto",
            "criado_em",
            "editado_em",
        )
