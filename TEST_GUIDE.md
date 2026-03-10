# Test Guide: Expense Tracker API

## Stack

- **Language:** Python 3.12
- **Framework:** Flask
- **Test Framework:** pytest
- **Linter:** ruff

## Test Commands

### Unit Tests
```bash
pytest tests/unit/ -v
```

### Integration Tests
```bash
pytest tests/integration/ -v -m integration
```

### Scenario Tests
```bash
pytest tests/scenarios/ -v -m scenario
```

### Full Test Pyramid
```bash
pytest tests/unit/ -v && pytest tests/integration/ -v -m integration && pytest tests/scenarios/ -v -m scenario
```

### Lint
```bash
ruff check .
```

## Test Structure

```
tests/
  unit/           # Pure function tests, mocked dependencies
  integration/    # API endpoint tests with Flask test client
  scenarios/      # Full user workflow tests end-to-end
```

## Requirement → Test Mapping

| Requirement | Test File | Test Name |
|-------------|-----------|-----------|
| (To be filled as tests are written) | | |

## Phase Coverage Log

| Phase | Unit | Integration | Scenario | Notes |
|-------|------|-------------|----------|-------|
| (To be filled per phase) | | | | |

---
*Created: 2026-03-10*
