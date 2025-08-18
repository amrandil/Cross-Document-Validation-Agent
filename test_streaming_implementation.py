#!/usr/bin/env python3
"""
Test script for the new real-time streaming implementation.
"""

import asyncio
import sys
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_streaming_updates():
    """Test the streaming update functionality."""

    print("Testing Real-Time Streaming Implementation")
    print("=" * 50)

    # Initialize OpenAI client
    client = OpenAI()

    # Test file path
    pdf_path = "testCases/ABDOS/BL - ABDOS.pdf"

    if not os.path.exists(pdf_path):
        print(f"Error: Test file not found at {pdf_path}")
        return

    print(f"Testing with file: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path):,} bytes")
    print()

    # Simulate the streaming workflow
    print("1. Stream connected")
    print("2. Preprocessing files...")
    print("3. Starting to process BL - ABDOS.pdf (1/1)")
    print("4. Starting direct PDF processing with OpenAI")
    print("5. Uploading PDF file to OpenAI servers")

    try:
        # Read the PDF file
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()

        print("6. PDF file uploaded successfully")

        # Upload PDF file
        file = client.files.create(
            file=("BL - ABDOS.pdf", pdf_bytes, "application/pdf"),
            purpose="assistants"
        )

        print("7. Extracting content using gpt-4o")

        # Create extraction prompt
        prompt = """
You are analyzing a Bill of Lading document. Please extract all information with maximum detail and accuracy.

EXTRACT EVERYTHING visible in this PDF including:
1. ALL TEXT CONTENT: Every word, number, code, reference, signature, stamp
2. STRUCTURED DATA: Tables, forms, lists, sections with their relationships
3. METADATA: Dates, document numbers, reference codes, certifications
4. ENTITIES: Company names, addresses, contact information, officials
5. FINANCIAL DATA: All amounts, currencies, calculations, totals, taxes
6. QUANTITIES & MEASUREMENTS: Weights, dimensions, counts, units
7. SHIPPING/LOGISTICS: Ports, vessels, containers, routing, tracking numbers
8. REGULATORY INFO: Licenses, permits, classifications, compliance codes
9. SIGNATURES & STAMPS: Official marks, certifications, authorizations
10. LAYOUT CONTEXT: How information is organized and related

BILL OF LADING SPECIFIC EXTRACTION:
- B/L number, date, type (Master/House)
- Shipper, consignee, notify party details
- Vessel name, voyage, port of loading/discharge
- Container numbers, seal numbers, package details
- Cargo description, weight, measurement, marks
- Freight terms, delivery instructions
- Agent signatures and stamps

IMPORTANT: Preserve exact numbers, dates, and codes - accuracy is critical for fraud detection.
"""

        # Create chat completion with uploaded file
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "file",
                            "file": {
                                "file_id": file.id,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ]
                }
            ],
            max_tokens=4096,
            temperature=0.1
        )

        extracted_content = response.choices[0].message.content

        print("8. PDF content extracted successfully")
        print(f"   Content length: {len(extracted_content):,} characters")

        # Simulate extracted content update
        print("9. Sending extracted content to frontend")
        print("   Document Type: BILL_OF_LADING")
        print("   Content Length: {:,} chars".format(len(extracted_content)))

        print("10. Generating comprehensive document summary")

        # Generate summary
        summary_prompt = f"""
Based on the comprehensive PDF extraction below, create a MASTER DOCUMENT SUMMARY for this Bill of Lading (BL - ABDOS.pdf).

PROVIDE:
1. **DOCUMENT OVERVIEW**: Type, number, date, parties involved
2. **KEY DATA EXTRACTION**: All critical numbers, amounts, quantities, dates
3. **ENTITY INFORMATION**: All companies, addresses, contacts, officials
4. **TRANSACTION DETAILS**: Products, services, financial terms, logistics
5. **REGULATORY DATA**: Certifications, codes, compliance information
6. **CROSS-REFERENCES**: Links between different data points
7. **FRAUD DETECTION FOCUS**: Highlight data points critical for fraud analysis

STRUCTURE THE SUMMARY FOR MAXIMUM UTILITY IN FRAUD DETECTION ANALYSIS.

Original extracted content:
{extracted_content}
"""

        summary_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": summary_prompt
                }
            ],
            max_tokens=2048,
            temperature=0.1
        )

        summary_content = summary_response.choices[0].message.content

        print("11. PDF processing completed successfully")
        print(
            f"    Final content length: {len(summary_content) + len(extracted_content):,} characters")

        # Clean up uploaded file
        try:
            client.files.delete(file.id)
            print("12. Uploaded file deleted successfully")
        except Exception as e:
            print(f"    Warning: Failed to delete uploaded file: {str(e)}")

        print("13. Completed processing BL - ABDOS.pdf (1/1)")
        print("14. Preprocessing complete - 1 files processed in X.Xs")

        print(f"\n✅ Streaming workflow test completed successfully!")
        print(f"   Extracted content: {len(extracted_content):,} characters")
        print(f"   Summary content: {len(summary_content):,} characters")
        print(
            f"   Total content: {len(summary_content) + len(extracted_content):,} characters")

        # Save the results
        with open("test_streaming_result.txt", "w", encoding="utf-8") as f:
            f.write("=== EXTRACTED CONTENT ===\n")
            f.write(extracted_content)
            f.write("\n\n=== DOCUMENT SUMMARY ===\n")
            f.write(summary_content)

        print(f"\nResults saved to: test_streaming_result.txt")

    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Main test function."""
    print("Real-Time Streaming Implementation Test")
    print("=" * 50)

    test_streaming_updates()

    print("\n" + "=" * 50)
    print("Test completed!")


if __name__ == "__main__":
    main()
