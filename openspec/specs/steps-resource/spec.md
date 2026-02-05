# Steps Resource

## Purpose

Provides access to custom document processing steps for executing user-defined workflows.

## Requirements

### Requirement: Execute step asynchronously
The SDK SHALL provide a `steps.run_async()` method that executes a document processing step via `/api/steps-async/{stepId}`.

#### Scenario: Execute step with file
- **WHEN** user calls `client.steps.run_async(step_id="step_123", file=Path("document.pdf"))`
- **THEN** the SDK returns `StepExecutionStatus` with `execution_id` and status `ENQUEUED`

#### Scenario: Execute step with URL
- **WHEN** user calls `client.steps.run_async(step_id="step_123", url="https://example.com/doc.pdf")`
- **THEN** the SDK sends URL to API and returns execution status

### Requirement: Step execution status polling
The SDK SHALL provide a `steps.get_status()` method to check step execution status via `/api/steps-async/status/{executionId}`.

#### Scenario: Check completed step execution
- **WHEN** user calls `client.steps.get_status(execution_id="exec_123")` after completion
- **THEN** the SDK returns `StepExecutionStatus` with status `SUCCESS` and result data

#### Scenario: Check failed step execution
- **WHEN** user calls `client.steps.get_status(execution_id="exec_123")` after failure
- **THEN** the SDK returns `StepExecutionStatus` with status `ERROR` and error message

### Requirement: Async client steps methods
The SDK SHALL provide `AsyncSteps` class with async versions accessible via `AsyncClient.steps`.

#### Scenario: Async execute step
- **WHEN** user calls `await async_client.steps.run_async(step_id="step_123", file=path)`
- **THEN** the SDK performs async HTTP request and returns `StepExecutionStatus`

### Requirement: Raw response access for steps
The SDK SHALL provide `with_raw_response` property on `Steps` and `AsyncSteps` resource classes.

#### Scenario: Get raw response from run_async
- **WHEN** user calls `client.steps.with_raw_response.run_async(step_id="step_123", file=path)`
- **THEN** SDK returns `RawResponse` with status_code, headers, and http_response

#### Scenario: Get raw response from get_status
- **WHEN** user calls `client.steps.with_raw_response.get_status(execution_id="exec_123")`
- **THEN** SDK returns `RawResponse` with step execution status details

#### Scenario: Parse raw response
- **WHEN** user has `RawResponse` from steps operation and calls `response.parse()`
- **THEN** SDK returns `StepExecutionStatus` typed model

### Requirement: Async raw response for steps
The SDK SHALL provide `with_raw_response` property on `AsyncSteps` class.

#### Scenario: Async raw response from run_async
- **WHEN** user calls `await client.steps.with_raw_response.run_async(step_id="step_123", file=path)` on AsyncClient
- **THEN** SDK returns `RawResponse` from async HTTP request
