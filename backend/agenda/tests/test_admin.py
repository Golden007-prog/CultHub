from django.test import TestCase
from django.urls import reverse

from agenda.models import InteresseEmEvento, PresencaEmEvento
from catalogo.tests.fabrica import criar_evento
from usuarios.models import Usuario


class AdminAgendaTests(TestCase):
    modelos = (InteresseEmEvento, PresencaEmEvento)

    def setUp(self):
        self.admin = Usuario.objects.create_superuser(
            "admin@exemplo.com", "senha-forte-123", nome="Admin"
        )
        self.usuario = Usuario.objects.create_user(
            "visitante@exemplo.com", "senha-forte-123", nome="Visitante"
        )
        self.client.force_login(self.admin)
        evento = criar_evento()
        self.marcas = {
            modelo: modelo.objects.create(usuario=self.admin, evento=evento)
            for modelo in self.modelos
        }

    def test_admin_lista_salvos_e_presencas(self):
        for modelo, marca in self.marcas.items():
            nome = modelo._meta.model_name
            with self.subTest(modelo=nome):
                url = reverse(f"admin:agenda_{nome}_changelist")
                modelo.objects.create(
                    usuario=self.usuario, evento=marca.evento
                )
                resposta = self.client.get(url, {"q": self.admin.email})
                self.assertEqual(resposta.status_code, 200)
                self.assertEqual(
                    list(resposta.context["cl"].result_list), [marca]
                )

    def test_admin_nao_permite_adicionar(self):
        for nome in ("interesseemevento", "presencaemevento"):
            with self.subTest(modelo=nome):
                resposta = self.client.get(reverse(f"admin:agenda_{nome}_add"))
                self.assertEqual(resposta.status_code, 403)

    def test_admin_nao_permite_editar(self):
        for modelo, marca in self.marcas.items():
            nome = modelo._meta.model_name
            with self.subTest(modelo=nome):
                url = reverse(f"admin:agenda_{nome}_change", args=[marca.pk])
                resposta = self.client.post(
                    url,
                    {"usuario": self.usuario.pk, "evento": marca.evento_id},
                )
                self.assertEqual(resposta.status_code, 403)
                marca.refresh_from_db()
                self.assertEqual(marca.usuario_id, self.admin.pk)

    def test_usuario_sem_is_staff_nao_acessa_admin(self):
        self.client.force_login(self.usuario)
        for modelo in self.modelos:
            nome = modelo._meta.model_name
            with self.subTest(modelo=nome):
                url = reverse(f"admin:agenda_{nome}_changelist")
                resposta = self.client.get(url)
                self.assertRedirects(
                    resposta, f"{reverse('admin:login')}?next={url}"
                )
