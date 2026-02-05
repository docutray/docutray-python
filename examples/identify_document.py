"""Identify the type of a document using the DocuTray SDK.

NOTE: Running this script makes an API call that consumes credits
from your DocuTray account.

Usage:
    python identify_document.py
"""

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


def identify_from_file():
    """Identify a document from a local file."""
    document_path = Path("sample_invoice.pdf")
    if not document_path.exists():
        print(f"Error: File not found: {document_path}")
        sys.exit(1)

    result = client.identify.run(
        file=document_path,
        document_type_code_options=["invoice"],
    )

    print(f"Document type: {result.document_type.name}")
    print(f"Code:          {result.document_type.code}")
    print(f"Confidence:    {result.document_type.confidence:.2%}")

    if result.alternatives:
        print("\nAlternatives:")
        for alt in result.alternatives:
            print(f"  - {alt.name}: {alt.confidence:.2%}")


# --- Additional usage examples (each call consumes API credits) ---


def identify_from_url():
    """Identify a document from a URL."""
    url = "https://storage.googleapis.com/public.docutray.com/api-examples/sample_invoice.pdf"
    result = client.identify.run(
        url=url,
        document_type_code_options=["invoice"],
    )

    print(f"Document type: {result.document_type.name}")
    print(f"Code:          {result.document_type.code}")
    print(f"Confidence:    {result.document_type.confidence:.2%}")


def identify_with_options():
    """Identify a document limiting to specific document types."""
    result = client.identify.run(
        file=Path("sample_invoice.pdf"),
        document_type_code_options=["invoice", "receipt"],
    )

    print(f"Document type: {result.document_type.name}")
    print(f"Confidence:    {result.document_type.confidence:.2%}")


if __name__ == "__main__":
    identify_from_file()
