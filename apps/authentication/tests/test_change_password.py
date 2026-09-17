from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class ChangePasswordAPITests(APITestCase):
    """Suíte de testes para alteração de senha exigindo validação da senha atual (AC 8)."""

    url = reverse('auth-change-password')

    def setUp(self):
        self.auth_user = User.objects.create_user(
            name='Lucas Senha',
            email='lucas@flashmind.com',
            password='SenhaAtual123!',
        )
        refresh = RefreshToken.for_user(self.auth_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_change_password_success_issues_fresh_tokens(self):
        """AC 8: Altera a senha ao fornecer a senha atual correta e emite novos tokens."""
        payload = {
            'current_password': 'SenhaAtual123!',
            'new_password': 'NovaSenhaForte456!@#',
        }

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # Valida que a senha no banco foi alterada
        self.auth_user.refresh_from_db()
        self.assertTrue(self.auth_user.check_password('NovaSenhaForte456!@#'))
        self.assertFalse(self.auth_user.check_password('SenhaAtual123!'))

        # Valida que o login com a nova senha funciona
        self.client.credentials()
        login_url = reverse('auth-login')
        login_res = self.client.post(
            login_url,
            data={'email': 'lucas@flashmind.com', 'password': 'NovaSenhaForte456!@#'},
            format='json',
        )
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)

    def test_change_password_rejects_wrong_current_password(self):
        """AC 8: Rejeita a troca quando a senha atual fornecida estiver incorreta."""
        payload = {
            'current_password': 'SenhaTotalmenteIncorreta!',
            'new_password': 'NovaSenhaForte456!@#',
        }

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('current_password', response.data)
        self.assertIn('A senha atual está incorreta.', str(response.data['current_password']))

        # Senha antiga deve permanecer válida
        self.auth_user.refresh_from_db()
        self.assertTrue(self.auth_user.check_password('SenhaAtual123!'))

    def test_change_password_unauthenticated_rejected(self):
        """Acesso não autenticado é rejeitado com 401."""
        self.client.credentials()
        response = self.client.post(self.url, data={'current_password': 'a', 'new_password': 'b'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
