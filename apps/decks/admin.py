from django.contrib import admin
from .models import Deck, Flashcard

class FlashcardInline(admin.TabularInline):
    model = Flashcard
    extra = 1

@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'description', 'user__email', 'user__name')
    inlines = [FlashcardInline]

@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('question', 'deck', 'review_step', 'times_reviewed', 'next_review_at')
    list_filter = ('review_step', 'created_at')
    search_fields = ('question', 'answer', 'deck__title')
