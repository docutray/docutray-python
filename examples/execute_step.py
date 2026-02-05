"""Example: Execute a predefined step using the docutray SDK."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

import docutray

load_dotenv()

client = docutray.Client()

# Step ID from environment variable
STEP_ID = os.getenv("DOCUTRAY_STEP_ID")

if not STEP_ID:
    print("Error: DOCUTRAY_STEP_ID not set in .env")
    print("Add DOCUTRAY_STEP_ID=your_step_id to your .env file")
    exit(1)

print(f"Using step: {STEP_ID}")


def on_status(status):
    """Callback to track step execution progress."""
    print(f"  Status: {status.status}")


# Test 1: Execute step with local file
print("\n" + "=" * 50)
print("Test 1: Execute step with local file")
print("=" * 50)

document_path = Path("sample_invoice.pdf")

if document_path.exists():
    status = client.steps.run_async(
        STEP_ID,
        file=document_path,
    )
    print(f"Started execution: {status.execution_id}")

    # Wait for completion with progress callback
    final_status = status.wait(on_status=on_status)

    if final_status.is_success():
        print("\nStep executed successfully!")
        print("\nResult data:")
        print(json.dumps(final_status.data, indent=2, ensure_ascii=False))
    elif final_status.is_error():
        print(f"\nStep execution failed: {final_status.error}")
else:
    print(f"File not found: {document_path}")

# Test 2: Execute step with URL
print("\n" + "=" * 50)
print("Test 2: Execute step with URL")
print("=" * 50)

url = "https://storage.googleapis.com/public.docutray.com/api-examples/sample_invoice.pdf"
print(f"URL: {url}")

status = client.steps.run_async(
    STEP_ID,
    url=url,
)
print(f"Started execution: {status.execution_id}")

# Wait for completion with progress callback
final_status = status.wait(on_status=on_status)

if final_status.is_success():
    print("\nStep executed successfully!")
    print("\nResult data:")
    print(json.dumps(final_status.data, indent=2, ensure_ascii=False))
elif final_status.is_error():
    print(f"\nStep execution failed: {final_status.error}")

# Test 3: Execute step with document metadata
print("\n" + "=" * 50)
print("Test 3: Execute step with document metadata")
print("=" * 50)

status = client.steps.run_async(
    STEP_ID,
    url=url,
    document_metadata={
        "source": "sdk_example",
        "custom_field": "test_value",
    },
)
print(f"Started execution: {status.execution_id}")
print("Document metadata: {'source': 'sdk_example', 'custom_field': 'test_value'}")

final_status = status.wait(on_status=on_status)

if final_status.is_success():
    print("\nStep executed successfully!")
    print("\nResult data:")
    print(json.dumps(final_status.data, indent=2, ensure_ascii=False))
elif final_status.is_error():
    print(f"\nStep execution failed: {final_status.error}")
