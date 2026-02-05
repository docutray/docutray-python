## Purpose

Automated generation of API reference documentation from source code docstrings, producing Markdown files for the SDK public API.

## Requirements

### Requirement: Generator script exists
The system SHALL provide a script at `scripts/gen_api_ref.py` that generates API reference documentation from source code.

#### Scenario: Script is executable
- **WHEN** developer runs `python scripts/gen_api_ref.py`
- **THEN** the script executes without import errors

### Requirement: Uses griffe for parsing
The generator SHALL use the griffe library to parse Python source files and extract documentation.

#### Scenario: Parses module with Google-style docstrings
- **WHEN** generator processes a module containing Google-style docstrings
- **THEN** it extracts the docstring text, Args, Returns, Raises, and Example sections

### Requirement: Generates Markdown output
The generator SHALL output Markdown files to the `docs/api/` directory.

#### Scenario: Directory structure created
- **WHEN** generator runs successfully
- **THEN** it creates `docs/api/index.md`, `docs/api/client.md`, `docs/api/exceptions.md`

#### Scenario: Resource documentation generated
- **WHEN** generator processes resource modules
- **THEN** it creates `docs/api/resources/` directory with one file per resource

#### Scenario: Types documentation generated
- **WHEN** generator processes type definition modules
- **THEN** it creates `docs/api/types/` directory with organized type documentation

### Requirement: Documents public API only
The generator SHALL only document public classes, methods, and functions (not prefixed with underscore).

#### Scenario: Private members excluded
- **WHEN** generator encounters a method named `_internal_method`
- **THEN** it does not include that method in the output

#### Scenario: Public methods included
- **WHEN** generator encounters a method named `create`
- **THEN** it includes that method with its full docstring

### Requirement: Includes code examples
The generated documentation SHALL include code examples from docstring Example sections.

#### Scenario: Example section rendered
- **WHEN** a method has an Example section in its docstring
- **THEN** the generated Markdown includes the example in a Python code block

### Requirement: Cross-references types
The generator SHALL link type annotations to their documentation where available.

#### Scenario: Return type linked
- **WHEN** a method returns `ConvertResponse`
- **THEN** the documentation links to the ConvertResponse type definition

### Requirement: Dependency is optional
The griffe library SHALL be listed in optional dependencies, not core dependencies.

#### Scenario: Install without griffe
- **WHEN** user runs `pip install docutray`
- **THEN** griffe is not installed

#### Scenario: Install with docs extra
- **WHEN** user runs `pip install docutray[docs]`
- **THEN** griffe is installed
