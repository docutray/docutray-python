"""Execute a predefined processing step using the DocuTray SDK.

The step ID must be configured in your .env file.

NOTE: Running this script makes an API call that consumes credits
from your DocuTray account.

Usage:
    python execute_steps.py
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

import docutray

load_dotenv()

api_key = os.getenv("DOCUTRAY_API_KEY")
if not api_key:
    print("Error: DOCUTRAY_API_KEY not set.")
    print("Copy .env.example to .env and add your API key.")
    sys.exit(1)

step_id = os.getenv("DOCUTRAY_STEP_ID")
if not step_id:
    print("Error: DOCUTRAY_STEP_ID not set.")
    print("Add DOCUTRAY_STEP_ID=your_step_id to your .env file.")
    sys.exit(1)

client = docutray.Client(api_key=api_key)


def execute_from_file():
    """Execute a step with a local file."""
    document_path = Path("sample_invoice.pdf")
    if not document_path.exists():
        print(f"Error: File not found: {document_path}")
        sys.exit(1)

    status = client.steps.run_async(step_id, file=document_path)
    print(f"Execution started: {status.execution_id}")

    result = status.wait(on_status=lambda s: print(f"  Status: {s.status}"))

    if result.is_success():
        print("\nStep executed successfully!")
        print("\nResult data:")
        print(json.dumps(result.data, indent=2, ensure_ascii=False))
    elif result.is_error():
        print(f"\nStep execution failed: {result.error}")


# --- Additional usage examples (each call consumes API credits) ---


def execute_from_url():
    """Execute a step with a document URL."""
    url = "https://storage.googleapis.com/public.docutray.com/api-examples/sample_invoice.pdf"

    status = client.steps.run_async(step_id, url=url)
    print(f"Execution started: {status.execution_id}")

    result = status.wait(on_status=lambda s: print(f"  Status: {s.status}"))

    if result.is_success():
        print(json.dumps(result.data, indent=2, ensure_ascii=False))
    elif result.is_error():
        print(f"Step execution failed: {result.error}")


def execute_with_metadata():
    """Execute a step with additional document metadata."""
    status = client.steps.run_async(
        step_id,
        file=Path("sample_invoice.pdf"),
        document_metadata={"source": "sdk_example"},
    )

    result = status.wait()

    if result.is_success():
        print(json.dumps(result.data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    execute_from_file()
