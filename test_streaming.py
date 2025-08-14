#!/usr/bin/env python3
"""
Test script for the streaming endpoint
"""

import asyncio
import aiohttp
import json
from pathlib import Path


async def test_streaming():
    """Test the streaming endpoint with sample data"""

    # Create sample text files for testing
    sample_dir = Path("test_samples")
    sample_dir.mkdir(exist_ok=True)

    # Create sample invoice
    invoice_content = """
    COMMERCIAL INVOICE
    
    Invoice No: INV-001
    Date: 2024-01-15
    
    Seller: ABC Company
    Buyer: XYZ Corporation
    
    Items:
    1. Electronics - 100 units - $50 each - Total: $5000
    2. Components - 200 units - $25 each - Total: $5000
    
    Total Amount: $10,000
    """

    with open(sample_dir / "invoice.txt", "w") as f:
        f.write(invoice_content)

    # Create sample packing list
    packing_content = """
    PACKING LIST
    
    Invoice No: INV-001
    
    Items:
    1. Electronics - 100 units - Weight: 50kg
    2. Components - 200 units - Weight: 30kg
    
    Total Weight: 80kg
    """

    with open(sample_dir / "packing_list.txt", "w") as f:
        f.write(packing_content)

    # Test streaming endpoint
    url = "http://localhost:8000/api/v1/analyze/stream"

    data = aiohttp.FormData()
    data.add_field('files', open(sample_dir / "invoice.txt",
                   'rb'), filename='invoice.txt')
    data.add_field('files', open(sample_dir / "packing_list.txt",
                   'rb'), filename='packing_list.txt')
    data.add_field('options', json.dumps(
        {"confidence_threshold": 0.7, "detailed_analysis": True}))

    print("Testing streaming endpoint...")
    print(f"URL: {url}")

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            print(f"Response status: {response.status}")

            if response.status == 200:
                print("Streaming response received. Reading updates...")

                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            print(
                                f"Update: {data.get('type', 'unknown')} - {data.get('message', '')}")

                            if data.get('type') == 'step_completed':
                                print(
                                    f"  Step {data.get('step_number')}: {data.get('step_type')}")
                                print(
                                    f"  Content: {data.get('content', '')[:100]}...")

                            if data.get('type') in ['analysis_completed', 'analysis_error']:
                                print("Analysis finished!")
                                break

                        except json.JSONDecodeError as e:
                            print(f"Failed to parse JSON: {e}")
                            print(f"Raw line: {line_str}")
            else:
                print(f"Error: {response.status}")
                text = await response.text()
                print(f"Response: {text}")

if __name__ == "__main__":
    asyncio.run(test_streaming())
