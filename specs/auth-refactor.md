# Auth Refactor Spec

## Description
Refatorar o módulo de autenticação para suportar refresh tokens e separar responsabilidades em camadas.

## Requirements
- Usar pathlib para manipulação de caminhos
- Funções puras onde possível
- Type hints obrigatórios
- Separar lógica de auth em handler, middleware e tokens

## Constraints
- Não quebrar API existente
- Manter compatibilidade com tokens JWT atuais
- Cobertura mínima de testes: 80%

## Files
- src/auth/handler.py
- src/auth/middleware.py
- src/auth/tokens.py
- src/auth/refresh.py
- tests/test_auth.py

## Acceptance Criteria
- Refresh tokens funcionam corretamente
- Middleware valida access e refresh tokens
- Testes passam com cobertura >= 80%
- Código passa em black, isort e flake8
