"""Convert a document and extract structured data using the DocuTray SDK.

NOTE: Running this script makes an API call that consumes credits
from your DocuTray account.

Usage:
    python convert_document.py
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

client = docutray.Client(api_key=api_key)


def convert_from_file():
    """Convert a document from a local file."""
    document_path = Path("sample_invoice.pdf")
    if not document_path.exists():
        print(f"Error: File not found: {document_path}")
        sys.exit(1)

    result = client.convert.run(
        file=document_path,
        document_type_code="invoice",
    )

    print("Conversion successful!")
    print("\nExtracted data:")
    print(json.dumps(result.data, indent=2, ensure_ascii=False))


# --- Additional usage examples (each call consumes API credits) ---


def convert_from_url():
    """Convert a document from a URL."""
    url = "https://storage.googleapis.com/public.docutray.com/api-examples/sample_invoice.pdf"

    result = client.convert.run(
        url=url,
        document_type_code="invoice",
    )

    print("Conversion successful!")
    print("\nExtracted data:")
    print(json.dumps(result.data, indent=2, ensure_ascii=False))


def convert_async_with_polling():
    """Convert a document asynchronously with progress polling."""
    result = client.convert.run_async(
        file=Path("sample_invoice.pdf"),
        document_type_code="invoice",
    )
    print(f"Conversion started: {result.conversion_id}")

    final = result.wait(on_status=lambda s: print(f"  Status: {s.status}"))

    if final.is_success():
        print(json.dumps(final.data, indent=2, ensure_ascii=False))
    elif final.is_error():
        print(f"Conversion failed: {final.error}")


if __name__ == "__main__":
    convert_from_file()
