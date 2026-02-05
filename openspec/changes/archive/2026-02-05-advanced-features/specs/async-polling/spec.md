## MODIFIED Requirements

### Requirement: Wait for async operation completion
The SDK SHALL provide a `wait()` method on async status objects that polls until completion or timeout. The method SHALL support an optional progress callback.

#### Scenario: Wait for successful completion
- **WHEN** user calls `status.wait()` on a `ConversionStatus` or `IdentificationStatus`
- **THEN** the SDK polls `get_status()` until status is `SUCCESS` and returns final result

#### Scenario: Wait with custom poll interval
- **WHEN** user calls `status.wait(poll_interval=5.0)`
- **THEN** the SDK waits 5 seconds between each status check

#### Scenario: Wait with timeout
- **WHEN** user calls `status.wait(timeout=60.0)` and operation takes longer
- **THEN** the SDK raises `APITimeoutError` after 60 seconds

#### Scenario: Wait for failed operation
- **WHEN** user calls `status.wait()` and operation fails
- **THEN** the SDK returns status with `ERROR` and error message (does not raise)

#### Scenario: Wait with progress callback
- **WHEN** user calls `status.wait(on_status=lambda s: print(s.status))`
- **THEN** the SDK invokes callback with current status after each poll

## ADDED Requirements

### Requirement: Direct wait method on status models
The SDK SHALL provide `wait()` method directly on `ConversionStatus`, `IdentificationStatus`, and `StepExecutionStatus` Pydantic models.

#### Scenario: Call wait on ConversionStatus
- **WHEN** user receives `ConversionStatus` from `convert.run_async()` and calls `status.wait()`
- **THEN** the SDK polls for completion using stored resource reference

#### Scenario: Call wait on IdentificationStatus
- **WHEN** user receives `IdentificationStatus` from `identify.run_async()` and calls `status.wait()`
- **THEN** the SDK polls for completion using stored resource reference

#### Scenario: Call wait on StepExecutionStatus
- **WHEN** user receives `StepExecutionStatus` from `steps.run_async()` and calls `status.wait()`
- **THEN** the SDK polls for completion using stored resource reference

### Requirement: Async wait method on status models
The SDK SHALL provide async `wait()` method on status models for use with `AsyncClient`.

#### Scenario: Async wait on status
- **WHEN** user calls `await status.wait()` on status from async client
- **THEN** the SDK performs async polling and returns final result

### Requirement: Progress callback type
The SDK SHALL accept `on_status` callback parameter with signature `Callable[[StatusType], None]`.

#### Scenario: Callback receives status updates
- **WHEN** user provides `on_status` callback to `wait()`
- **THEN** callback is invoked with current status after each successful poll (not on initial status)
