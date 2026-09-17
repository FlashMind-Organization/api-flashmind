import uuid
from django.db import models
from django.conf import settings

class Deck(models.Model):
    """Modelo de baralho vinculado obrigatoriamente a um usuário proprietário."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='decks',
    )
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Baralho'
        verbose_name_plural = 'Baralhos'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.user.email})"

class Flashcard(models.Model):
    """Modelo de cartão de memorização pertencente a um baralho."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name='flashcards',
    )
    question = models.TextField()
    answer = models.TextField()
    review_step = models.PositiveSmallIntegerField(default=0)
    times_reviewed = models.PositiveIntegerField(default=0)
    next_review_at = models.DateTimeField(null=True, blank=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Flashcard'
        verbose_name_plural = 'Flashcards'
        ordering = ['created_at']

    def __str__(self):
        return f"Card #{self.id} em {self.deck.title}"
