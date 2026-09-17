# FlashMind Backend API — Orientação para Agentes

## Contexto da API

Backend em Django 5 + Django REST Framework (DRF) para o ecossistema FlashMind.
Atende o aplicativo mobile Flutter.

## Padrão de Organização

```text
apps/<app>/
├── models.py       # Modelos Django ORM com UUID primary key
├── serializers.py  # ModelSerializer do DRF
├── views.py        # ModelViewSet ou APIView
├── urls.py         # DefaultRouter ou caminhos de URL
└── tests/          # APITestCase / pytest-django
```

## Regras Obrigatórias

- Evite N+1 queries: use sempre `select_related` e `prefetch_related`.
- Operações de escrita em múltiplos passos exigem `transaction.atomic()`.
- Testes usam o banco de teste isolado e nunca dependem de serviços externos.
- Rotas autenticadas usam `IsAuthenticated` e tokens do SimpleJWT.
