import base64
import os
from openai import OpenAI
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI()


def test_file_upload_method(pdf_path: str, model: str) -> Dict[str, Any]:
    """
    Test the file upload method for PDF processing
    """
    print(f"\n=== Testing File Upload Method with {model} ===")

    try:
        # Upload the PDF file
        print(f"Uploading file: {pdf_path}")
        file = client.files.create(
            file=open(pdf_path, "rb"),
            purpose="assistants"
        )
        print(f"File uploaded successfully. File ID: {file.id}")

        # Create a response using the uploaded file
        response = client.chat.completions.create(
            model=model,
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
                            "text": "Please analyze this PDF document and provide a summary of its key contents, including any important details like dates, amounts, parties involved, and document type.",
                        },
                    ]
                }
            ]
        )

        print("Response received successfully!")
        return {
            "method": "file_upload",
            "model": model,
            "success": True,
            "response": response.choices[0].message.content,
            "file_id": file.id
        }

    except Exception as e:
        print(f"Error in file upload method: {str(e)}")
        return {
            "method": "file_upload",
            "model": model,
            "success": False,
            "error": str(e)
        }


def test_base64_method(pdf_path: str, model: str) -> Dict[str, Any]:
    """
    Test the base64 encoding method for PDF processing
    """
    print(f"\n=== Testing Base64 Method with {model} ===")

    try:
        # Read and encode the PDF file
        print(f"Reading and encoding file: {pdf_path}")
        with open(pdf_path, "rb") as f:
            data = f.read()

        base64_string = base64.b64encode(data).decode("utf-8")
        print(
            f"File encoded successfully. Size: {len(base64_string)} characters")

        # Create a response using the Base64-encoded file
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "file",
                            "file": {
                                "filename": os.path.basename(pdf_path),
                                "file_data": f"data:application/pdf;base64,{base64_string}",
                            },
                        },
                        {
                            "type": "text",
                            "text": "Please analyze this PDF document and provide a summary of its key contents, including any important details like dates, amounts, parties involved, and document type.",
                        },
                    ],
                },
            ]
        )

        print("Response received successfully!")
        return {
            "method": "base64",
            "model": model,
            "success": True,
            "response": response.choices[0].message.content
        }

    except Exception as e:
        print(f"Error in base64 method: {str(e)}")
        return {
            "method": "base64",
            "model": model,
            "success": False,
            "error": str(e)
        }


def main():
    """
    Main function to test both methods with both models
    """
    pdf_path = "testCases/ABDOS/BL - ABDOS.pdf"

    # Check if the PDF file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return

    print(f"Testing PDF processing methods with file: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path)} bytes")

    models = ["gpt-5", "gpt-4o"]
    results = []

    # Test both methods with both models
    for model in models:
        # Test file upload method
        result1 = test_file_upload_method(pdf_path, model)
        results.append(result1)

        # Test base64 method
        result2 = test_base64_method(pdf_path, model)
        results.append(result2)

    # Print summary of results
    print("\n" + "="*80)
    print("SUMMARY OF RESULTS")
    print("="*80)

    for result in results:
        print(f"\nMethod: {result['method']}")
        print(f"Model: {result['model']}")
        print(f"Success: {result['success']}")

        if result['success']:
            if result['method'] == 'file_upload':
                print(f"File ID: {result.get('file_id', 'N/A')}")
            print(f"Response length: {len(result['response'])} characters")
            print(f"Response preview: {result['response'][:200]}...")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")

    # Save detailed results to file
    with open("pdf_vision_test_results.txt", "w") as f:
        f.write("PDF Vision Model Test Results\n")
        f.write("="*50 + "\n\n")

        for result in results:
            f.write(f"Method: {result['method']}\n")
            f.write(f"Model: {result['model']}\n")
            f.write(f"Success: {result['success']}\n")

            if result['success']:
                if result['method'] == 'file_upload':
                    f.write(f"File ID: {result.get('file_id', 'N/A')}\n")
                f.write(f"Response:\n{result['response']}\n")
            else:
                f.write(f"Error: {result.get('error', 'Unknown error')}\n")

            f.write("-"*50 + "\n\n")

    print(f"\nDetailed results saved to: pdf_vision_test_results.txt")


if __name__ == "__main__":
    main()
