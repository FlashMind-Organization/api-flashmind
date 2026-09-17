from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class RegisterAPITests(APITestCase):
    """Suíte de testes para criação de conta de usuário (AC 1, AC 2, AC 3)."""

    url = reverse('auth-register')

    def test_create_account_success(self):
        """AC 1 & AC 3: Cria conta com nome, e-mail e senha com hash seguro (nunca plaintext)."""
        payload = {
            'name': 'Carlos Silva',
            'email': 'carlos@flashmind.com',
            'password': 'SenhaForte123!@#',
        }

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Carlos Silva')
        self.assertEqual(response.data['email'], 'carlos@flashmind.com')
        self.assertEqual(response.data['role'], 'user')
        self.assertNotIn('password', response.data)

        # Verifica persistência e hashing no banco (AC 3)
        user = User.objects.get(email='carlos@flashmind.com')
        self.assertEqual(user.name, 'Carlos Silva')
        self.assertNotEqual(user.password, 'SenhaForte123!@#')
        self.assertTrue(user.check_password('SenhaForte123!@#'))
        self.assertFalse(user.password.startswith('Senha'))

    def test_reject_duplicate_email_with_clear_message(self):
        """AC 2: Rejeita e-mail já registrado com mensagem explicativa clara."""
        User.objects.create_user(
            name='Maria Existente',
            email='maria@flashmind.com',
            password='SenhaAntiga123!',
        )

        payload = {
            'name': 'Maria Nova Tentativa',
            'email': 'maria@flashmind.com',
            'password': 'NovaSenha123!@#',
        }

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('Este e-mail já está cadastrado.', str(response.data['email']))

    def test_reject_duplicate_email_case_insensitive(self):
        """AC 2: Validação de duplicidade deve ser case-insensitive."""
        User.objects.create_user(
            name='Joao Silva',
            email='joao@flashmind.com',
            password='SenhaValida123!',
        )

        payload = {
            'name': 'Joao Outro',
            'email': 'JOAO@FLASHMIND.COM',
            'password': 'SenhaValida123!',
        }

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Este e-mail já está cadastrado.', str(response.data['email']))

    def test_reject_weak_or_short_password(self):
        """Rejeita senhas curtas segundo a política de segurança do Django."""
        payload = {
            'name': 'Pedro',
            'email': 'pedro@flashmind.com',
            'password': '123',
        }

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
