## ADDED Requirements

### Requirement: Wait for async operation completion
The SDK SHALL provide a `wait()` method on async status objects that polls until completion or timeout.

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

### Requirement: Default polling configuration
The SDK SHALL use sensible defaults for polling: `poll_interval=2.0` seconds, `timeout=300.0` seconds.

#### Scenario: Default poll interval
- **WHEN** user calls `status.wait()` without arguments
- **THEN** the SDK polls every 2 seconds

#### Scenario: Default timeout
- **WHEN** user calls `status.wait()` without timeout argument
- **THEN** the SDK times out after 300 seconds (5 minutes)

### Requirement: Async wait method
The SDK SHALL provide async `wait()` method for use with `AsyncClient`.

#### Scenario: Async wait for completion
- **WHEN** user calls `await status.wait()` on async status object
- **THEN** the SDK performs async polling and returns final result
