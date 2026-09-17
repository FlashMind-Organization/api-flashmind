from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.decks.models import Deck

User = get_user_model()

class DeckIsolationAPITests(APITestCase):
    """Suíte de testes para isolamento estrito de baralhos entre usuários (AC 10)."""

    base_url = '/api/decks/'

    def setUp(self):
        self.user_a = User.objects.create_user(
            name='Estudante A',
            email='aluno.a@flashmind.com',
            password='SenhaValida123!',
        )
        self.user_b = User.objects.create_user(
            name='Estudante B',
            email='aluno.b@flashmind.com',
            password='SenhaValida123!',
        )

    def _auth_as(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_user_only_lists_own_decks(self):
        """AC 10: Cada usuário visualiza somente os seus próprios baralhos na listagem."""
        deck_a1 = Deck.objects.create(user=self.user_a, title='Linux Basics')
        deck_a2 = Deck.objects.create(user=self.user_a, title='Git Fundamentals')
        deck_b1 = Deck.objects.create(user=self.user_b, title='Python Avançado')

        # Usuário A lista baralhos
        self._auth_as(self.user_a)
        res_a = self.client.get(self.base_url)
        self.assertEqual(res_a.status_code, status.HTTP_200_OK)
        results_a = res_a.data.get('results', res_a.data)
        ids_a = [d['id'] for d in results_a]

        self.assertIn(str(deck_a1.id), ids_a)
        self.assertIn(str(deck_a2.id), ids_a)
        self.assertNotIn(str(deck_b1.id), ids_a)

        # Usuário B lista baralhos
        self._auth_as(self.user_b)
        res_b = self.client.get(self.base_url)
        self.assertEqual(res_b.status_code, status.HTTP_200_OK)
        results_b = res_b.data.get('results', res_b.data)
        ids_b = [d['id'] for d in results_b]

        self.assertIn(str(deck_b1.id), ids_b)
        self.assertNotIn(str(deck_a1.id), ids_b)
        self.assertNotIn(str(deck_a2.id), ids_b)

    def test_user_cannot_retrieve_another_user_deck_returns_404(self):
        """AC 10: Tentar obter detalhes de baralho de outro usuário retorna 404 Not Found."""
        deck_a = Deck.objects.create(user=self.user_a, title='Baralho Confidencial A')

        self._auth_as(self.user_b)
        detail_url = f'{self.base_url}{deck_a.id}/'
        response = self.client.get(detail_url)

        # Retorna 404 (evita vazamento de confirmação da existência do ID)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_update_another_user_deck_returns_404(self):
        """AC 10: Tentar atualizar baralho de outro usuário retorna 404 e preserva os dados originais."""
        deck_a = Deck.objects.create(user=self.user_a, title='Título Original', description='Desc Original')

        self._auth_as(self.user_b)
        detail_url = f'{self.base_url}{deck_a.id}/'
        payload = {'title': 'Tentativa de Hack'}

        response = self.client.patch(detail_url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        deck_a.refresh_from_db()
        self.assertEqual(deck_a.title, 'Título Original')

    def test_user_cannot_delete_another_user_deck_returns_404(self):
        """AC 10: Tentar deletar baralho de outro usuário retorna 404 e não remove o registro."""
        deck_a = Deck.objects.create(user=self.user_a, title='Baralho Protegido')

        self._auth_as(self.user_b)
        detail_url = f'{self.base_url}{deck_a.id}/'
        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Deck.objects.filter(id=deck_a.id).exists())

    def test_owner_can_manage_own_deck(self):
        """O proprietário consegue criar, visualizar, atualizar e deletar seu próprio baralho."""
        self._auth_as(self.user_a)

        # Criar
        create_res = self.client.post(self.base_url, data={'title': 'Meu Baralho'}, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        deck_id = create_res.data['id']

        detail_url = f'{self.base_url}{deck_id}/'

        # Obter
        get_res = self.client.get(detail_url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data['title'], 'Meu Baralho')

        # Atualizar
        patch_res = self.client.patch(detail_url, data={'title': 'Meu Baralho Atualizado'}, format='json')
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data['title'], 'Meu Baralho Atualizado')

        # Deletar
        delete_res = self.client.delete(detail_url)
        self.assertEqual(delete_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Deck.objects.filter(id=deck_id).exists())
