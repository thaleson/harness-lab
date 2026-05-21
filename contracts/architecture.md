# Architecture Rules

## Directory Structure

- `src/` - Application source code
- `tests/` - Test files
- `harness/` - Harness engine (do not modify during sprints)
- `contracts/` - Sprint contracts (Markdown)
- `reports/` - Generated reports

## Import Rules

- No circular imports allowed.
- `src/` modules must not import from `harness/`.
- `tests/` may import from `src/` and `harness/`.
