## Purpose

Comprehensive SDK documentation including README with usage examples, CHANGELOG for version tracking, Google-style docstrings for all public APIs, and PyPI metadata for release.

## Requirements

### Requirement: README has installation section
The README SHALL include installation instructions with pip and optional dependencies.

#### Scenario: Basic installation shown
- **WHEN** developer reads the installation section
- **THEN** they see `pip install docutray` command

#### Scenario: Optional dependencies documented
- **WHEN** developer needs docs generation
- **THEN** they see `pip install docutray[docs]` option

### Requirement: README has quick start examples
The README SHALL include minimal working examples for both sync and async usage.

#### Scenario: Sync quick start
- **WHEN** developer reads quick start section
- **THEN** they see a complete sync example with Client initialization and a convert call

#### Scenario: Async quick start
- **WHEN** developer reads quick start section
- **THEN** they see a complete async example with AsyncClient and await syntax

### Requirement: README has configuration section
The README SHALL document all client configuration options.

#### Scenario: API key configuration shown
- **WHEN** developer reads configuration section
- **THEN** they see how to set API key via constructor and environment variable

#### Scenario: Timeout configuration shown
- **WHEN** developer reads configuration section
- **THEN** they see how to customize timeout settings

#### Scenario: Retry configuration shown
- **WHEN** developer reads configuration section
- **THEN** they see how to configure retry behavior

### Requirement: README has error handling section
The README SHALL document all exception types with examples.

#### Scenario: Exception hierarchy shown
- **WHEN** developer reads error handling section
- **THEN** they see the complete exception class hierarchy

#### Scenario: Exception catching example
- **WHEN** developer reads error handling section
- **THEN** they see how to catch and handle specific exception types

#### Scenario: Rate limit handling shown
- **WHEN** developer reads error handling section
- **THEN** they see how to handle RateLimitError with retry_after

### Requirement: README has resource examples
The README SHALL include examples for each API resource.

#### Scenario: Convert resource documented
- **WHEN** developer reads resources section
- **THEN** they see convert.create() example with file handling

#### Scenario: Identify resource documented
- **WHEN** developer reads resources section
- **THEN** they see identify.create() example

#### Scenario: Document types resource documented
- **WHEN** developer reads resources section
- **THEN** they see document_types.list() and retrieve() examples

#### Scenario: Steps resource documented
- **WHEN** developer reads resources section
- **THEN** they see steps.list() and retrieve() examples

#### Scenario: Knowledge bases resource documented
- **WHEN** developer reads resources section
- **THEN** they see knowledge_bases create, search, and document operations

### Requirement: README has pagination examples
The README SHALL document pagination patterns.

#### Scenario: Manual pagination shown
- **WHEN** developer reads pagination section
- **THEN** they see iter_pages() usage example

#### Scenario: Auto pagination shown
- **WHEN** developer reads pagination section
- **THEN** they see auto_paging_iter() usage example

### Requirement: README has raw response section
The README SHALL document how to access raw HTTP response data.

#### Scenario: Raw response access shown
- **WHEN** developer reads raw response section
- **THEN** they see with_raw_response usage and RawResponse properties

### Requirement: README has async operations section
The README SHALL document async patterns including polling.

#### Scenario: Polling callback shown
- **WHEN** developer reads async section
- **THEN** they see on_status callback usage for progress tracking

### Requirement: README has contributing section
The README SHALL include contribution guidelines.

#### Scenario: Development setup documented
- **WHEN** developer reads contributing section
- **THEN** they see how to set up development environment

#### Scenario: Testing instructions provided
- **WHEN** developer reads contributing section
- **THEN** they see how to run tests

### Requirement: CHANGELOG exists
The project SHALL have a CHANGELOG.md following Keep a Changelog format.

#### Scenario: Initial version documented
- **WHEN** developer reads CHANGELOG
- **THEN** they see 0.1.0 release with all implemented features

#### Scenario: Format is standard
- **WHEN** developer reads CHANGELOG
- **THEN** they see Added/Changed/Fixed/Removed sections as applicable

### Requirement: Docstrings follow Google format
All public classes and methods SHALL have Google-style docstrings.

#### Scenario: Client class documented
- **WHEN** developer inspects Client class
- **THEN** they see module docstring explaining the class purpose

#### Scenario: Methods have Args section
- **WHEN** developer inspects a public method
- **THEN** they see Args section with parameter descriptions

#### Scenario: Methods have Returns section
- **WHEN** developer inspects a method returning a value
- **THEN** they see Returns section describing the return value

#### Scenario: Methods have Raises section
- **WHEN** developer inspects a method that raises exceptions
- **THEN** they see Raises section listing possible exceptions

#### Scenario: Methods have Example section
- **WHEN** developer inspects a public method
- **THEN** they see Example section with usage code

### Requirement: PyPI metadata is complete
The pyproject.toml SHALL have all required metadata for PyPI.

#### Scenario: Bug tracker URL present
- **WHEN** checking project URLs
- **THEN** Bug Tracker URL points to GitHub issues

#### Scenario: Docs optional dependency group exists
- **WHEN** checking optional dependencies
- **THEN** docs group includes griffe
