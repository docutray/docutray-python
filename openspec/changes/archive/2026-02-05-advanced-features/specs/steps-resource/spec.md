## ADDED Requirements

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
