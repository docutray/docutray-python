## Context

The SDK has 212 tests achieving 63% coverage. Key coverage gaps exist in:
- `_polling.py` (38%): Async polling methods untested
- `_response.py` (18%): WithRawResponse classes largely untested
- `_http.py` (72%): Async request methods need coverage
- Resource async methods (42-68%): All resources need async test coverage

The project uses pytest with pytest-asyncio (asyncio_mode="auto"), respx for HTTP mocking, and pytest-cov for coverage. Quality tools (ruff, mypy) are configured in pyproject.toml but no pre-commit hooks exist.

## Goals / Non-Goals

**Goals:**
- Achieve >80% test coverage across all modules
- Add comprehensive async test coverage mirroring sync tests
- Add WithRawResponse tests for all resources
- Configure pre-commit hooks for automated quality enforcement
- Ensure mypy strict mode passes
- Ensure ruff check passes without warnings

**Non-Goals:**
- Integration tests with real API (tests MUST use mocks)
- Performance benchmarking
- Documentation generation
- CI/CD pipeline changes (pre-commit only)

## Decisions

### Decision 1: Test Structure - Mirror Pattern for Async

**Choice**: Create async test classes that mirror sync test classes within the same test files.

**Rationale**: Keeps related tests together, makes it easy to verify async/sync parity, follows existing pattern in test_retry.py.

**Alternatives considered**:
- Separate async test files: Rejected - harder to maintain parity
- Parameterized tests for sync/async: Rejected - too complex for different client types

### Decision 2: Pre-commit Hook Selection

**Choice**: Use ruff for linting/formatting, skip mypy in pre-commit (too slow).

**Rationale**:
- ruff is extremely fast and catches most issues
- mypy is slow and better suited for CI
- Pre-commit hooks should be fast to encourage frequent commits

**Alternatives considered**:
- Include mypy in pre-commit: Rejected - takes 10+ seconds, discourages commits
- Use only basic hooks: Rejected - misses linting benefits

### Decision 3: Coverage Target Strategy

**Choice**: Focus on async methods and WithRawResponse classes first, as they have lowest coverage.

**Rationale**: Maximum impact - these modules are at 18-38% and need the most work.

### Decision 4: respx Mocking Pattern

**Choice**: Use class-level mock_api fixtures from conftest.py for consistency.

**Rationale**: Already established pattern, works well with both sync and async clients.

## Risks / Trade-offs

**[Risk] Tests become flaky due to async timing** → Use pytest-asyncio auto mode which handles event loop management properly.

**[Risk] Pre-commit hooks slow down development** → Exclude mypy from pre-commit; run it only in CI.

**[Risk] Coverage percentage vs meaningful tests** → Focus on testing actual behavior and edge cases, not just line coverage.

**[Trade-off] Test file size increases** → Accepted - comprehensive coverage is more important than file size.

**[Trade-off] Some code may be intentionally uncovered** → Document any excluded code with `# pragma: no cover` comments.
