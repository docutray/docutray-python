# Exceptions

## Purpose

Provides a hierarchy of exception classes for handling errors from the DocuTray API and SDK operations.

## Requirements

### Requirement: Base exception class

The SDK SHALL provide a base `DocuTrayError` exception class for all SDK errors.

#### Scenario: All SDK errors inherit from base
- **WHEN** any SDK error is raised
- **THEN** it is an instance of `DocuTrayError`
- **AND** it is catchable with `except DocuTrayError:`

### Requirement: Exception message

The `DocuTrayError` class SHALL accept and store an error message.

#### Scenario: Exception with message
- **WHEN** `DocuTrayError("Something went wrong")` is raised
- **THEN** `str(exception)` returns "Something went wrong"

### Requirement: AuthenticationError subclass

The SDK SHALL provide `AuthenticationError` for authentication failures.

#### Scenario: Missing API key error
- **WHEN** no API key is provided and environment variable is not set
- **THEN** `AuthenticationError` is raised
- **AND** it is an instance of `DocuTrayError`

### Requirement: APIConnectionError subclass

The SDK SHALL provide `APIConnectionError` for network/connection issues.

#### Scenario: Connection failure
- **WHEN** the SDK cannot connect to the API server
- **THEN** `APIConnectionError` is raised
- **AND** it is an instance of `DocuTrayError`

### Requirement: APITimeoutError subclass

The SDK SHALL provide `APITimeoutError` for timeout scenarios.

#### Scenario: Request timeout
- **WHEN** a request exceeds the configured timeout
- **THEN** `APITimeoutError` is raised
- **AND** it is an instance of `DocuTrayError`
- **AND** it is an instance of `APIConnectionError`
