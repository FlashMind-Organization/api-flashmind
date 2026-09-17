# IA do FlashMind Backend API (api-flashmind)

Guia de contexto e arquitetura para o desenvolvimento da API em Django REST Framework do FlashMind.

| Para entender | Leia |
|---|---|
| **Contrato projetado com o Flutter** | `../docs-flashmind/guias/Contrato Futuro da API.md` |
| **Plano de transição** | `../docs-flashmind/guias/Plano de Transição para a API.md` |
| **Apps planejados** | `authentication`, `decks`, `progress` |

## Convenções de Backend Django REST

1. Organização por apps Django com separação clara: `models.py` → `serializers.py` → `views.py` → `urls.py`.
2. Split settings em `config/settings/` (`base.py`, `development.py`, `production.py`).
3. Painel administrativo ativo em `/admin/` para gestão de dados.
4. Autenticação JWT via `djangorestframework-simplejwt`.
5. Gestão de pacotes ultra-rápida com `uv`.
