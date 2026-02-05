## ADDED Requirements

### Requirement: Single API call per example
Each example script SHALL make exactly one API call to avoid unnecessary charges on the user's account.

#### Scenario: Identify example makes one call
- **WHEN** `identify_document.py` is executed
- **THEN** it SHALL make exactly one call to `client.identify.run()`

#### Scenario: Convert example makes one call
- **WHEN** `convert_document.py` is executed
- **THEN** it SHALL make exactly one call to `client.convert.run()`

#### Scenario: Execute step example makes one call
- **WHEN** `execute_steps.py` is executed
- **THEN** it SHALL make exactly one call to `client.steps.run_async()` followed by `status.wait()`

### Requirement: Billing awareness
Each example script SHALL include a clear warning that execution consumes API credits from the user's associated account.

#### Scenario: Script header warns about API usage
- **WHEN** a user reads any example script
- **THEN** the module docstring SHALL contain a notice about API credit consumption

#### Scenario: README warns about billing
- **WHEN** a user reads the examples README
- **THEN** it SHALL include a visible warning that running examples uses API credits

### Requirement: Simple installation
Examples SHALL use `pip install docutray python-dotenv` for setup, with no project scaffold (no pyproject.toml, uv.lock, or virtual environment).

#### Scenario: README documents pip install
- **WHEN** a user reads the README setup section
- **THEN** the instructions SHALL use `pip install docutray python-dotenv`

### Requirement: Environment-based configuration
Examples SHALL load API credentials from a `.env` file using python-dotenv, with a `.env.example` template.

#### Scenario: Missing API key shows clear error
- **WHEN** an example is run without DOCUTRAY_API_KEY configured
- **THEN** the script SHALL exit with a clear error message

### Requirement: Consistent script structure
Each example script SHALL follow a consistent structure: docstring with billing notice, imports, env loading, API key validation, single API call, result display.

#### Scenario: Script follows standard pattern
- **WHEN** a user opens any example script
- **THEN** it SHALL follow the order: docstring, imports, load_dotenv, key check, API call, output

### Requirement: File and URL input modes
Identify and convert examples SHALL demonstrate file-based input using the included sample document. Step execution SHALL demonstrate URL-based input.

#### Scenario: Identify uses local file
- **WHEN** `identify_document.py` is executed
- **THEN** it SHALL use `sample_invoice.pdf` as file input

#### Scenario: Convert uses local file
- **WHEN** `convert_document.py` is executed
- **THEN** it SHALL use `sample_invoice.pdf` as file input

#### Scenario: Execute step uses URL
- **WHEN** `execute_step.py` is executed
- **THEN** it SHALL use a URL as input
