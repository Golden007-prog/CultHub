from django.test import TestCase
from django.urls import reverse

from catalogo.tests.fabrica import criar_evento
from comentarios.models import Comentario
from usuarios.models import Usuario


class AdminTest(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_superuser(
            "admin@exemplo.com", "senha-forte-123", nome="Admin"
        )
        self.client.force_login(self.admin)
        self.comentario = Comentario.objects.create(
            evento=criar_evento(), autor=self.admin, texto="Oi"
        )

    def test_lista_e_abre_o_comentario_mas_nao_cria(self):
        lista = self.client.get(
            reverse("admin:comentarios_comentario_changelist")
        )
        detalhe = self.client.get(
            reverse(
                "admin:comentarios_comentario_change",
                args=[self.comentario.pk],
            )
        )
        criar = self.client.get(reverse("admin:comentarios_comentario_add"))

        self.assertEqual(lista.status_code, 200)
        self.assertEqual(detalhe.status_code, 200)
        self.assertEqual(criar.status_code, 403)
