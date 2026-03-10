# Expense Tracker API

Python/Flask expense tracking application with in-memory storage, deployed to Vercel.

## Project Structure
- `app/` - Flask application code
- `api/index.py` - Vercel serverless entry point
- `tests/` - Test suite (unit, integration, scenarios)
- `vercel.json` - Vercel deployment config
- `requirements.txt` - Python dependencies

# Testing Requirements (AX)

Every feature implementation MUST include tests at all three tiers:

## Test Tiers
1. **Unit tests** — Test individual functions/methods in isolation. Mock external dependencies.
2. **Integration tests** — Test component interactions with Flask test client.
3. **Scenario tests** — Test full user workflows end-to-end.

## Test Naming
Use semantic names: `Test<Component>_<Behavior>[_<Condition>]`
- Good: `TestExpenseService_CreateWithValidData`, `TestFullExpenseWorkflow`
- Bad: `TestShouldWork`, `Test1`, `TestGivenUserWhenLoginThenSuccess`

## Reference
- See `TEST_GUIDE.md` for requirement-to-test mapping
- Every requirement in ROADMAP.md must map to at least one scenario test
