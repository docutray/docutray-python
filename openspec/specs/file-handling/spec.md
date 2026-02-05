## ADDED Requirements

### Requirement: Support Path file input
The SDK SHALL accept `pathlib.Path` objects as file input and read the file contents automatically.

#### Scenario: Upload file from Path
- **WHEN** user passes `file=Path("document.pdf")` to any resource method
- **THEN** the SDK reads the file, detects content type, and sends as multipart form data

### Requirement: Support bytes file input
The SDK SHALL accept raw `bytes` as file input.

#### Scenario: Upload file from bytes
- **WHEN** user passes `file=document_bytes` with optional `content_type="application/pdf"`
- **THEN** the SDK sends the bytes as multipart form data with specified content type

### Requirement: Support BinaryIO file input
The SDK SHALL accept file-like objects (BinaryIO) as file input.

#### Scenario: Upload file from file object
- **WHEN** user passes `file=open("document.pdf", "rb")` to any resource method
- **THEN** the SDK reads from the file object and sends as multipart form data

### Requirement: Support URL file input
The SDK SHALL accept URL strings for server-side file download.

#### Scenario: Process file from URL
- **WHEN** user passes `url="https://example.com/document.pdf"` to any resource method
- **THEN** the SDK sends the URL to the API for server-side download

### Requirement: Support base64 file input
The SDK SHALL accept base64-encoded file data.

#### Scenario: Upload base64 encoded file
- **WHEN** user passes `file_base64="data:application/pdf;base64,..."` to any resource method
- **THEN** the SDK sends the base64 data to the API

#### Scenario: Upload base64 without data URI prefix
- **WHEN** user passes `file_base64="JVBERi0..."` with `content_type="application/pdf"`
- **THEN** the SDK constructs proper request with content type

### Requirement: Content type detection
The SDK SHALL automatically detect content type from file extension when not explicitly provided.

#### Scenario: Detect PDF content type
- **WHEN** user passes `file=Path("document.pdf")` without content_type
- **THEN** the SDK detects and uses `application/pdf`

#### Scenario: Detect image content type
- **WHEN** user passes `file=Path("scan.jpg")` without content_type
- **THEN** the SDK detects and uses `image/jpeg`
