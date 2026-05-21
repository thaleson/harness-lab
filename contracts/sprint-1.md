# Sprint 1 - Quality Gate Contract

## Checks

| Check    | Tool    | Threshold         |
|----------|---------|-------------------|
| Tests    | pytest  | all pass          |
| Format   | black   | 0 errors          |
| Imports  | isort   | 0 errors          |
| Lint     | flake8  | max 5 warnings    |

## Rules

- All checks MUST pass for the sprint to be approved.
- If any check fails, the report must flag it as BLOCKED.
- Format and lint checks run against `src/` directory.
- Tests run against `tests/` directory.

## Approval

- Status: PASS if all checks meet thresholds
- Status: FAIL if any check exceeds threshold
