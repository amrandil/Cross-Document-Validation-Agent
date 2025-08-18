#!/usr/bin/env python3
"""
Test script for the new direct PDF processing implementation.
"""

from models.documents import DocumentType
from utils.vision_pdf_processor import VisionPDFProcessor
import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


async def test_direct_pdf_processing():
    """Test the new direct PDF processing implementation."""

    print("Testing Direct PDF Processing Implementation")
    print("=" * 50)

    # Get the processor instance
    processor = VisionPDFProcessor.get_instance()

    # Print processor info
    info = processor.get_processor_info()
    print(f"Processor Type: {info['processor_type']}")
    print(f"Vision Model: {info['vision_model']}")
    print(f"Summary Model: {info['summary_model']}")
    print(f"Capabilities: {', '.join(info['capabilities'])}")
    print()

    # Test file path
    pdf_path = "testCases/ABDOS/BL - ABDOS.pdf"

    if not os.path.exists(pdf_path):
        print(f"Error: Test file not found at {pdf_path}")
        return

    print(f"Testing with file: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path):,} bytes")
    print()

    try:
        # Read the PDF file
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()

        print("Starting PDF extraction...")

        # Test the async extraction
        result = await processor.extract_comprehensive_content_async(
            pdf_bytes=pdf_bytes,
            filename="BL - ABDOS.pdf",
            document_type=DocumentType.BILL_OF_LADING
        )

        print(f"\nExtraction completed successfully!")
        print(f"Result length: {len(result):,} characters")
        print(f"Result preview: {result[:500]}...")

        # Save the result to a file for inspection
        with open("test_direct_pdf_result.txt", "w", encoding="utf-8") as f:
            f.write(result)

        print(f"\nFull result saved to: test_direct_pdf_result.txt")

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


def test_sync_pdf_processing():
    """Test the synchronous PDF processing implementation."""

    print("\nTesting Synchronous PDF Processing")
    print("=" * 50)

    # Get the processor instance
    processor = VisionPDFProcessor.get_instance()

    # Test file path
    pdf_path = "testCases/ABDOS/BL - ABDOS.pdf"

    if not os.path.exists(pdf_path):
        print(f"Error: Test file not found at {pdf_path}")
        return

    try:
        # Read the PDF file
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()

        print("Starting synchronous PDF extraction...")

        # Test the sync extraction
        result = processor.extract_comprehensive_content(
            pdf_bytes=pdf_bytes,
            filename="BL - ABDOS.pdf",
            document_type=DocumentType.BILL_OF_LADING
        )

        print(f"\nSynchronous extraction completed successfully!")
        print(f"Result length: {len(result):,} characters")
        print(f"Result preview: {result[:500]}...")

        # Save the result to a file for inspection
        with open("test_sync_pdf_result.txt", "w", encoding="utf-8") as f:
            f.write(result)

        print(f"\nFull result saved to: test_sync_pdf_result.txt")

    except Exception as e:
        print(f"Error during synchronous testing: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Main test function."""
    print("Direct PDF Processing Test Suite")
    print("=" * 50)

    # Test async processing
    asyncio.run(test_direct_pdf_processing())

    # Test sync processing
    test_sync_pdf_processing()

    print("\n" + "=" * 50)
    print("Test completed!")


if __name__ == "__main__":
    main()
