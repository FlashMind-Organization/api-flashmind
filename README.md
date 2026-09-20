# FlashMind — Backend API (Django REST Framework)

O **api-flashmind** é o backend RESTful do ecossistema FlashMind, desenvolvido em Django REST Framework (DRF) com autenticação baseada em JWT (SimpleJWT).

Ele é responsável por:
- Gestão e segurança de contas de usuários (estudantes e administradores).
- Emissão, rotação e revogação (blacklist) de tokens JWT.
- Armazenamento seguro de senhas via PBKDF2-SHA256 (sem nunca expô-las na API).
- Isolamento estrito de baralhos por usuário, retornando `404 Not Found` para requisições de recursos alheios (prevenindo vazamento por enumeração de IDs).

---

## 📋 Pré-requisitos

- **Python**: `>= 3.12`
- **Gerenciador de Dependências**: [`uv`](https://github.com/astral-sh/uv) (recomendado para performance e reprodutibilidade).

> [!TIP]
> Caso ainda não possua o `uv` instalado:
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```

---

## 🚀 Instalação e Configuração

### 1. Clonar ou acessar o diretório

```bash
cd api-flashmind
```

### 2. Sincronizar dependências do ambiente virtual

O `uv` gerencia o ambiente virtual automaticamente através do `pyproject.toml` e `uv.lock`:

```bash
uv sync
```

### 3. Aplicar as migrações do banco de dados

Por padrão no ambiente de desenvolvimento (`development.py`), o banco utilizado é o SQLite local:

```bash
uv run python manage.py migrate
```

### 4. (Opcional) Criar um usuário administrador

Para acessar o painel administrativo ou testar o perfil com papel `admin`:

```bash
uv run python manage.py createsuperuser
```

---

## 🏃 Execução do Servidor

Para iniciar o servidor de desenvolvimento na porta `8000`:

```bash
uv run python manage.py runserver 0.0.0.0:8000
```

> [!NOTE]
> Usar `0.0.0.0:8000` em vez de apenas `localhost` ou `127.0.0.1` é essencial para que o emulador Android (que acessa a máquina host pelo IP `10.0.2.2`) consiga alcançar a API sem bloqueios de rede.

---

## 🧪 Testes Automatizados

A API conta com suíte de testes unitários e de integração cobrindo fluxos de autenticação, rotação de tokens, autorização e isolamento de dados:

### Executar com Pytest (Recomendado)

```bash
uv run pytest
```

### Executar com o test runner padrão do Django

```bash
uv run python manage.py test apps --settings=config.settings.test
```

---

## 📡 Visão Geral dos Endpoints Principais

| Método | Rota | Descrição | Permissão |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Criação de conta (nome, e-mail, senha) | Aberto |
| `POST` | `/api/auth/login/` | Autenticação por e-mail e senha (retorna `access`, `refresh` e dados do usuário) | Aberto |
| `POST` | `/api/auth/token/refresh/` | Renovação do access token expirado | Aberto |
| `POST` | `/api/auth/logout/` | Encerramento de sessão (invalida o refresh token na blacklist) | Autenticado |
| `GET` | `/api/auth/profile/` | Consulta dos dados do usuário conectado | Autenticado |
| `PATCH` | `/api/auth/profile/` | Atualização cadastral (nome e e-mail) | Autenticado |
| `POST` | `/api/auth/change-password/` | Troca de senha exigindo a senha atual | Autenticado |
| `GET` | `/api/decks/` | Lista baralhos pertencentes exclusivamente ao usuário | Autenticado |
| `POST` | `/api/decks/` | Cria um novo baralho associado ao usuário logado | Autenticado |
| `GET` | `/api/decks/{id}/` | Detalhes do baralho (`404` se pertencer a outro usuário) | Autenticado |
| `PATCH` | `/api/decks/{id}/` | Edição do baralho (`404` se pertencer a outro usuário) | Autenticado |
| `DELETE` | `/api/decks/{id}/` | Exclusão do baralho (`404` se pertencer a outro usuário) | Autenticado |

---

## 📂 Estrutura do Projeto

```text
api-flashmind/
├── apps/
│   ├── authentication/        # Modelo Custom User, JWT, views de login/cadastro/perfil
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── tests/
│   └── decks/                 # Modelo Deck, serializadores e ViewSets isolados por usuário
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       └── tests/
├── config/
│   ├── settings/
│   │   ├── base.py            # Configurações globais e SimpleJWT
│   │   ├── development.py     # Configurações para desenvolvimento local (CORS, SQLite)
│   │   └── test.py            # Configurações para execução ágil de testes com banco em memória
│   ├── urls.py                # Roteamento central das APIs
│   └── wsgi.py
├── pyproject.toml             # Metadados e dependências do projeto com uv
├── uv.lock                    # Trava exata de versões das dependências
└── pytest.ini                 # Configuração do pytest-django
```
