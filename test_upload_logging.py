#!/usr/bin/env python3
"""Test script to demonstrate comprehensive logging for document upload and processing."""

import requests
import time
import os

def test_upload_logging():
    """Test document upload with comprehensive logging."""
    
    print("🧪 Testing Comprehensive Upload Logging")
    print("=" * 50)
    
    # Test file path (using a sample from testCases)
    test_file_path = "testCases/Ateco Farma/INVOICE Ateco.jpeg"
    
    if not os.path.exists(test_file_path):
        print(f"❌ Test file not found: {test_file_path}")
        print("Please ensure the test file exists or update the path.")
        return
    
    # API endpoint for file upload
    api_url = "http://localhost:8000/api/v1/analyze/upload"
    
    print(f"📤 Uploading file: {test_file_path}")
    print(f"🌐 Endpoint: {api_url}")
    print()
    
    try:
        # Prepare the upload
        with open(test_file_path, 'rb') as file:
            files = {'files': (os.path.basename(test_file_path), file, 'image/jpeg')}
            data = {
                'bundle_id': 'test_upload_bundle',
                'options': '{"confidence_threshold": 0.7}'
            }
            
            # Make the upload request
            start_time = time.time()
            response = requests.post(api_url, files=files, data=data, timeout=120)
            total_time = time.time() - start_time
            
            print(f"⏱️  Total upload time: {total_time:.2f}s")
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload and analysis completed successfully!")
                print(f"🆔 Bundle ID: {result.get('bundle_id', 'N/A')}")
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
                print(f"❌ Upload failed with status: {response.status_code}")
                print(f"📝 Response: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print()
    print("📋 Check the logs directory for comprehensive workflow logs:")
    print("   - Console: Colored, human-readable logs")
    print("   - File: logs/app.log (detailed logs)")
    print()
    print("🎯 Expected log entries:")
    print("   ✅ File upload request received")
    print("   ✅ File processing steps")
    print("   ✅ PDF/image conversion")
    print("   ✅ Vision LLM extraction")
    print("   ✅ Document type detection")
    print("   ✅ Agent execution phases")
    print("   ✅ Tool execution")
    print("   ✅ LLM interactions")
    print("   ✅ Performance metrics")
    print("   ✅ Fraud detection results")

if __name__ == "__main__":
    test_upload_logging()
