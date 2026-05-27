# Greet Refactor Spec

## Description
Refatorar a função greet para aceitar pontuação customizada opcional.

## Requirements
- A função greet deve aceitar parâmetro punctuation opcional.
- Se punctuation não for informado, usar "!" por padrão.
- greet("Alice") deve continuar funcionando.

## Constraints
- Modificar apenas arquivos permitidos.
- Não alterar auth-refactor.md.
- Não quebrar comandos existentes.

## Files
- src/app.py
- tests/test_app.py

## Acceptance Criteria
- greet("World") retorna "Hello, World! Welcome to Harness Lab."
- greet("World", "?") retorna "Hello, World? Welcome to Harness Lab."
- pytest passa
- black passa
- isort passa
- flake8 passa
