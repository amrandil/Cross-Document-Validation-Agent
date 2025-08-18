#!/usr/bin/env python3
"""Test script to demonstrate the comprehensive logging system."""

import time
import requests
import json
from typing import Dict, Any

# Test data
test_documents = [
    {
        "document_type": "commercial_invoice",
        "filename": "test_invoice.pdf",
        "content": """
        COMMERCIAL INVOICE
        
        Invoice Number: INV-2024-001
        Date: 2024-01-15
        Supplier: ABC Trading Co.
        Buyer: XYZ Import Ltd.
        
        Items:
        1. Electronic Components - Qty: 1000, Unit Price: $5.00, Total: $5,000.00
        2. Circuit Boards - Qty: 500, Unit Price: $10.00, Total: $5,000.00
        
        Total Invoice Value: $10,000.00
        Currency: USD
        """,
        "metadata": {"pages": 1}
    },
    {
        "document_type": "packing_list",
        "filename": "test_packing.pdf",
        "content": """
        PACKING LIST
        
        Packing List Number: PL-2024-001
        Date: 2024-01-15
        
        Items:
        1. Electronic Components - Qty: 1000, Weight: 50kg
        2. Circuit Boards - Qty: 500, Weight: 25kg
        
        Total Weight: 75kg
        Total Packages: 2
        """,
        "metadata": {"pages": 1}
    }
]

def test_logging_workflow():
    """Test the complete logging workflow."""
    
    print("🧪 Testing Comprehensive Logging System")
    print("=" * 50)
    
    # Test API endpoint
    api_url = "http://localhost:8000/api/v1/analyze"
    
    request_data = {
        "bundle_id": "test_bundle_001",
        "documents": test_documents,
        "options": {
            "confidence_threshold": 0.7,
            "max_iterations": 5
        }
    }
    
    print(f"📤 Sending request to: {api_url}")
    print(f"📄 Documents: {len(test_documents)}")
    print(f"🆔 Bundle ID: {request_data['bundle_id']}")
    print()
    
    try:
        # Make the request
        start_time = time.time()
        response = requests.post(api_url, json=request_data, timeout=60)
        total_time = time.time() - start_time
        
        print(f"⏱️  Total request time: {total_time:.2f}s")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis completed successfully!")
            print(f"🆔 Execution ID: {result.get('execution_id', 'N/A')}")
            print(f"📈 Processing time: {result.get('processing_time_ms', 0)}ms")
            print(f"📄 Documents processed: {result.get('documents_processed', 0)}")
            
            # Check fraud analysis results
            fraud_analysis = result.get('fraud_analysis')
            if fraud_analysis:
                confidence = fraud_analysis.get('confidence', 0)
                indicators = fraud_analysis.get('indicators', [])
                print(f"🎯 Fraud confidence: {confidence:.1%}")
                print(f"🔍 Fraud indicators: {len(indicators)}")
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            print(f"📝 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print()
    print("📋 Check the logs directory for detailed workflow logs:")
    print("   - Console: Colored, human-readable logs")
    print("   - File: logs/app.log (detailed logs with rotation)")
    print()
    print("🎯 Log features implemented:")
    print("   ✅ Application startup logging")
    print("   ✅ API request/response logging")
    print("   ✅ Document processing logging")
    print("   ✅ ReAct agent phase logging")
    print("   ✅ Tool execution logging")
    print("   ✅ LLM request/response logging")
    print("   ✅ Performance timing logging")
    print("   ✅ Error handling logging")
    print("   ✅ Fraud detection result logging")

if __name__ == "__main__":
    test_logging_workflow()
