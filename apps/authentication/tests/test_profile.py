from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class ProfileAPITests(APITestCase):
    """Suíte de testes para visualização e edição do próprio perfil (AC 7)."""

    url = reverse('auth-profile')

    def setUp(self):
        self.auth_user = User.objects.create_user(
            name='Ana Perfil',
            email='ana@flashmind.com',
            password='SenhaSegura123!',
        )
        refresh = RefreshToken.for_user(self.auth_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_get_profile_authenticated(self):
        """AC 7: Usuário autenticado visualiza seus dados de perfil."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.auth_user.id))
        self.assertEqual(response.data['name'], 'Ana Perfil')
        self.assertEqual(response.data['email'], 'ana@flashmind.com')
        self.assertEqual(response.data['role'], 'user')

    def test_get_profile_unauthenticated(self):
        """Acesso não autenticado é rejeitado com 401."""
        self.client.credentials()  # Remove autenticação
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_name_and_email_success(self):
        """AC 7: Usuário edita nome e e-mail com sucesso."""
        payload = {
            'name': 'Ana Silva Santos',
            'email': 'ana.santos@flashmind.com',
        }

        response = self.client.patch(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Ana Silva Santos')
        self.assertEqual(response.data['email'], 'ana.santos@flashmind.com')

        self.auth_user.refresh_from_db()
        self.assertEqual(self.auth_user.name, 'Ana Silva Santos')
        self.assertEqual(self.auth_user.email, 'ana.santos@flashmind.com')

    def test_update_profile_email_already_taken_rejected(self):
        """AC 7: Não permite alterar o e-mail para um que já pertença a outro usuário."""
        User.objects.create_user(
            name='Outro Usuario',
            email='outro@flashmind.com',
            password='SenhaOutro123!',
        )

        payload = {
            'email': 'outro@flashmind.com',
        }

        response = self.client.patch(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('Este e-mail já está em uso.', str(response.data['email']))

        self.auth_user.refresh_from_db()
        self.assertEqual(self.auth_user.email, 'ana@flashmind.com')
