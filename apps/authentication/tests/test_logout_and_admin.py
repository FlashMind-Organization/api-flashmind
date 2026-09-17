from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class LogoutAndAdminAPITests(APITestCase):
    """Suíte de testes para Logout (AC 6) e Verificação de Permissões de Admin (AC 9)."""

    logout_url = reverse('auth-logout')
    admin_check_url = reverse('auth-admin-check')

    def setUp(self):
        self.regular_user = User.objects.create_user(
            name='Estudante Normal',
            email='aluno@flashmind.com',
            password='SenhaValida123!',
            role='user',
        )
        self.admin_user = User.objects.create_user(
            name='Admin FlashMind',
            email='admin@flashmind.com',
            password='SenhaAdmin123!',
            role='admin',
            is_staff=True,
        )

    def test_logout_blacklists_refresh_token(self):
        """AC 6: Logout com refresh token invalida o token via blacklist."""
        refresh = RefreshToken.for_user(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        payload = {'refresh': str(refresh)}
        response = self.client.post(self.logout_url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('detail'), 'Sessão encerrada com sucesso.')

        # Tentar usar o refresh token invalidado no endpoint de refresh deve falhar
        refresh_url = reverse('auth-token-refresh')
        refresh_response = self.client.post(refresh_url, data={'refresh': str(refresh)}, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_access_admin_endpoint(self):
        """AC 9: Usuário com papel comum (user) recebe 403 ao tentar acessar endpoint administrativo."""
        refresh = RefreshToken.for_user(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.get(self.admin_check_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_access_admin_endpoint(self):
        """AC 9: Usuário com papel 'admin' possui acesso liberado ao endpoint administrativo."""
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.get(self.admin_check_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['role'], 'admin')
        self.assertEqual(response.data['detail'], 'Acesso administrativo confirmado.')
