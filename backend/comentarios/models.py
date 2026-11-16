import uuid

from django.conf import settings
from django.db import models

TAMANHO_MAXIMO = 2000


def profundidade_maxima():
    """Níveis de resposta permitidos (1 = só respostas diretas)."""
    return max(1, settings.COMENTARIOS_PROFUNDIDADE_MAXIMA)


class Comentario(models.Model):
    """Comentário sobre um evento, ou resposta a outro comentário.

    `nivel` é 0 no comentário e 1, 2… nas respostas. Responder além da
    profundidade máxima vira resposta ao ancestral mais profundo permitido
    (com profundidade 1, responder a uma resposta responde ao comentário).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evento = models.ForeignKey(
        "catalogo.Evento",
        on_delete=models.CASCADE,
        related_name="comentarios",
    )
    # SET_NULL: apagar a conta não apaga as respostas de outras pessoas.
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="comentarios",
    )
    resposta_a = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="respostas",
    )
    nivel = models.PositiveSmallIntegerField(default=0, editable=False)
    texto = models.TextField(max_length=TAMANHO_MAXIMO, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    editado_em = models.DateTimeField(null=True, blank=True)
    # Removido pela pessoa: some o texto, mas as respostas continuam.
    removido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "comentário"
        verbose_name_plural = "comentários"
        indexes = (
            models.Index(
                fields=("evento", "resposta_a", "criado_em"),
                name="comentario_por_evento",
            ),
        )

    def __str__(self):
        return f"{self.autor} em {self.evento}"

    @property
    def removido(self) -> bool:
        return self.removido_em is not None

    @staticmethod
    def alvo_da_resposta(comentario):
        """Comentário que de fato recebe a resposta, respeitando o limite."""
        limite = profundidade_maxima()
        while comentario.nivel >= limite:
            comentario = comentario.resposta_a
        return comentario

    def save(self, *args, **kwargs):
        # Só ao criar: editar ou remover não muda a quem o comentário responde.
        if self._state.adding and self.resposta_a_id is not None:
            self.resposta_a = self.alvo_da_resposta(self.resposta_a)
            self.evento_id = self.resposta_a.evento_id
            self.nivel = self.resposta_a.nivel + 1
        super().save(*args, **kwargs)
