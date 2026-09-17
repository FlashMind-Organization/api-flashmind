from rest_framework import serializers
from .models import Deck, Flashcard

class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = [
            'id',
            'deck',
            'question',
            'answer',
            'review_step',
            'times_reviewed',
            'next_review_at',
            'last_reviewed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'deck', 'created_at', 'updated_at']

class DeckSerializer(serializers.ModelSerializer):
    """Serializer para visualização e criação de baralhos vinculados ao usuário autenticado."""

    total_cards = serializers.IntegerField(source='flashcards.count', read_only=True)

    class Meta:
        model = Deck
        fields = [
            'id',
            'title',
            'description',
            'total_cards',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'total_cards', 'created_at', 'updated_at']

    def validate_title(self, value):
        title = value.strip()
        if not title:
            raise serializers.ValidationError('O título do baralho é obrigatório.')
        if len(title) > 100:
            raise serializers.ValidationError('O título deve ter no máximo 100 caracteres.')
        return title

    def validate_description(self, value):
        description = value.strip()
        if len(description) > 300:
            raise serializers.ValidationError('A descrição deve ter no máximo 300 caracteres.')
        return description
