## ADDED Requirements

### Requirement: Pre-commit configuration file
The project SHALL have a .pre-commit-config.yaml file at the repository root.

#### Scenario: Configuration file exists
- **WHEN** checking the repository root
- **THEN** .pre-commit-config.yaml exists and is valid YAML

### Requirement: Ruff linting hook
The pre-commit configuration SHALL include ruff for linting with auto-fix.

#### Scenario: Ruff lint runs on commit
- **WHEN** staging Python files and running pre-commit
- **THEN** ruff check runs with --fix flag to auto-correct issues

#### Scenario: Ruff format runs on commit
- **WHEN** staging Python files and running pre-commit
- **THEN** ruff format runs to ensure consistent formatting

### Requirement: Standard pre-commit hooks
The pre-commit configuration SHALL include standard quality hooks.

#### Scenario: Trailing whitespace removal
- **WHEN** staging files with trailing whitespace
- **THEN** pre-commit removes trailing whitespace automatically

#### Scenario: End-of-file fixer
- **WHEN** staging files without final newline
- **THEN** pre-commit adds a final newline

#### Scenario: YAML validation
- **WHEN** staging YAML files
- **THEN** pre-commit validates YAML syntax

#### Scenario: Large file detection
- **WHEN** staging files larger than threshold
- **THEN** pre-commit warns about large files

### Requirement: Mypy excluded from pre-commit
The pre-commit configuration SHALL NOT include mypy to maintain fast commit times.

#### Scenario: Mypy not in pre-commit
- **WHEN** examining .pre-commit-config.yaml
- **THEN** there is no mypy hook configured

### Requirement: Type checking passes
The codebase SHALL pass mypy strict mode when run manually.

#### Scenario: Mypy strict succeeds
- **WHEN** running uv run mypy --strict src/
- **THEN** the command completes with no errors

### Requirement: Linting passes
The codebase SHALL pass ruff check with no warnings.

#### Scenario: Ruff check succeeds
- **WHEN** running uv run ruff check src/
- **THEN** the command completes with no errors or warnings

#### Scenario: Ruff format check succeeds
- **WHEN** running uv run ruff format --check src/
- **THEN** the command completes indicating all files are formatted correctly
