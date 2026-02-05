## Why

The SDK currently has 63% test coverage (212 tests), below the >80% target required for production readiness. Critical modules like `_polling.py` (38%), `_response.py` (18%), and async resource methods are significantly under-tested. Additionally, pre-commit hooks are not configured, allowing quality issues to slip through.

## What Changes

- Add comprehensive test suites for all async resource methods (convert, identify, document_types, knowledge_bases, steps)
- Add tests for `WithRawResponse` classes across all resources
- Add async polling tests including timeout handling and `on_status` callbacks
- Add edge case and error condition tests
- Configure pre-commit hooks for automated quality enforcement (ruff, mypy, trailing whitespace)
- Ensure mypy strict mode passes without errors
- Ensure ruff check passes without warnings

## Capabilities

### New Capabilities
- `test-coverage`: Comprehensive test suite achieving >80% coverage with tests for sync methods, async methods, raw responses, polling, and error handling
- `pre-commit-hooks`: Pre-commit configuration with ruff (linting/formatting), mypy (type checking), and standard hooks (trailing whitespace, end-of-file fixer, yaml check)

### Modified Capabilities
<!-- No spec-level behavior changes - this is testing/quality infrastructure -->

## Impact

- **Tests**: New test files and expanded existing tests in `tests/` directory
- **Configuration**: New `.pre-commit-config.yaml` file
- **Dependencies**: Pre-commit added to dev dependencies
- **CI/CD**: Pre-commit hooks will run automatically on git commit
- **Code Quality**: All code must pass mypy strict and ruff checks
