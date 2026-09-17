from rest_framework import viewsets, permissions
from .models import Deck
from .serializers import DeckSerializer

class DeckViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de baralhos com isolamento estrito por usuário.
    
    AC 10: Garante que um usuário só consiga listar, visualizar, editar ou remover
    os seus próprios baralhos. Requisições para baralhos de terceiros retornam 404.
    """

    serializer_class = DeckSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Escopo estrito: retorna apenas baralhos cujo proprietário seja o usuário autenticado
        return Deck.objects.filter(user=self.request.user).prefetch_related('flashcards')

    def perform_create(self, serializer):
        # Atribui automaticamente o usuário autenticado como proprietário do baralho
        serializer.save(user=self.request.user)
