# FlashMind Backend API Project Context

@.ia/INDEX.md

## Diretrizes do Backend Django REST (`api-flashmind`)

Este é o futuro backend centralizado do ecossistema FlashMind (Django 5 + Django REST Framework + PostgreSQL + uv).
- **Estrutura por Apps**: `apps/authentication`, `apps/decks`, `apps/progress`.
- **Invariantes**:
  1. Separação de camadas: Models Django ORM, Serializers DRF e ViewSets.
  2. Todos os modelos principais terminam com `created_at`, `updated_at`, `deleted_at`.
  3. Autenticação via `djangorestframework-simplejwt`.
  4. Suíte de testes com `pytest-django` e `APITestCase`.
