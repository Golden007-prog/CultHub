from django.test import TestCase, override_settings

from catalogo.tests.fabrica import criar_evento
from comentarios.models import Comentario
from usuarios.models import Usuario


class ProfundidadeTest(TestCase):
    def setUp(self):
        self.autor = Usuario.objects.create_user(
            "ana@exemplo.com", "senha-forte-123", nome="Ana Souza"
        )
        self.evento = criar_evento()
        self.raiz = Comentario.objects.create(
            evento=self.evento, autor=self.autor, texto="Raiz"
        )

    def responder(self, alvo, texto="Resposta"):
        return Comentario.objects.create(
            evento=self.evento, autor=self.autor, resposta_a=alvo, texto=texto
        )

    def test_comentario_comeca_no_nivel_zero(self):
        self.assertEqual(self.raiz.nivel, 0)
        self.assertFalse(self.raiz.removido)
        self.assertIn("ana@exemplo.com", str(self.raiz))

    def test_com_um_nivel_responder_a_resposta_responde_a_raiz(self):
        resposta = self.responder(self.raiz)
        da_resposta = self.responder(resposta)

        self.assertEqual(resposta.nivel, 1)
        self.assertEqual(da_resposta.resposta_a, self.raiz)
        self.assertEqual(da_resposta.nivel, 1)

    @override_settings(COMENTARIOS_PROFUNDIDADE_MAXIMA=3)
    def test_profundidade_maior_vira_arvore_ate_o_limite(self):
        n1 = self.responder(self.raiz)
        n2 = self.responder(n1)
        n3 = self.responder(n2)
        alem = self.responder(n3)

        self.assertEqual([n1.nivel, n2.nivel, n3.nivel], [1, 2, 3])
        self.assertEqual(alem.resposta_a, n2)
        self.assertEqual(alem.nivel, 3)

    @override_settings(COMENTARIOS_PROFUNDIDADE_MAXIMA=0)
    def test_profundidade_zero_e_tratada_como_um(self):
        resposta = self.responder(self.responder(self.raiz))
        self.assertEqual(resposta.resposta_a, self.raiz)

    def test_resposta_herda_o_evento_do_comentario(self):
        outro = criar_evento(titulo="Outro")
        resposta = Comentario.objects.create(
            evento=outro, autor=self.autor, resposta_a=self.raiz, texto="x"
        )
        self.assertEqual(resposta.evento, self.evento)
