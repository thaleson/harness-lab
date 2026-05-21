# Feature 001 - Task Engine

## Objetivo
Implementar suporte a tarefas definidas em Markdown no Harness Lab.
O sistema deve carregar, parsear e exibir resumo de tasks.

## Regras
- Usar pathlib para manipulação de arquivos
- Parser simples, sem regex complexa
- Manter princípios SOLID
- Não modificar arquivos ainda

## Arquivos Permitidos
- harness/task_loader.py
- tasks/feature-001.md
- cli.py
- tests/test_task_loader.py
- tests/test_cli.py

## Critérios de Aceite
- TaskLoader carrega e parseia task Markdown corretamente
- CLI exibe resumo estruturado da task
- Todos os testes passam
- Código passa em black, isort e flake8
