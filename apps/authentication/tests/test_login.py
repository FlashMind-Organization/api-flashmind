from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class LoginAPITests(APITestCase):
    """Suíte de testes para autenticação e prevenção contra enumeração de usuários (AC 4)."""

    url = reverse('auth-login')

    def setUp(self):
        self.user = User.objects.create_user(
            name='Estudante Ativo',
            email='estudante@flashmind.com',
            password='SenhaCorreta123!',
        )

    def test_login_success(self):
        """Login bem-sucedido retorna tokens JWT (access/refresh) e payload do usuário."""
        payload = {
            'email': 'estudante@flashmind.com',
            'password': 'SenhaCorreta123!',
        }

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'estudante@flashmind.com')
        self.assertEqual(response.data['user']['role'], 'user')

    def test_login_invalid_password_returns_generic_error(self):
        """AC 4: Senha incorreta retorna 401 com mensagem genérica."""
        payload = {
            'email': 'estudante@flashmind.com',
            'password': 'SenhaErrada999!',
        }

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get('detail'), 'Credenciais inválidas.')

    def test_login_nonexistent_email_returns_identical_generic_error(self):
        """AC 4: E-mail inexistente retorna o mesmo 401 e a MESMA mensagem que senha incorreta."""
        payload = {
            'email': 'fantasma@flashmind.com',
            'password': 'QualquerSenha123!',
        }

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get('detail'), 'Credenciais inválidas.')

    def test_login_inactive_user_returns_generic_error(self):
        """Usuário desativado não acessa e recebe o mesmo erro genérico."""
        User.objects.create_user(
            name='Inativo',
            email='inativo@flashmind.com',
            password='SenhaValida123!',
            is_active=False,
        )

        payload = {
            'email': 'inativo@flashmind.com',
            'password': 'SenhaValida123!',
        }

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get('detail'), 'Credenciais inválidas.')
