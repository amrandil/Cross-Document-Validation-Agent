#!/usr/bin/env python3
"""
Test script to simulate frontend streaming connection.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any


async def test_frontend_streaming():
    """Test the streaming endpoint as the frontend would."""

    print("=" * 80)
    print("FRONTEND STREAMING TEST")
    print("=" * 80)

    # Create a simple test file content
    test_content = "This is a test invoice with sample data."

    # Create form data as the frontend would
    data = aiohttp.FormData()
    data.add_field('files', test_content,
                   filename='test_invoice.pdf', content_type='application/pdf')
    data.add_field('options', json.dumps({}))

    print("✅ Connecting to streaming endpoint...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:8000/api/v1/analyze/stream',
                data=data,
                headers={'Accept': 'text/event-stream'}
            ) as response:

                print(f"📡 Response status: {response.status}")
                print(f"📡 Response headers: {dict(response.headers)}")

                if response.status != 200:
                    print(f"❌ Error: {response.status}")
                    error_text = await response.text()
                    print(f"❌ Error details: {error_text}")
                    return

                # Read streaming response
                updates_received = []
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()

                    if not line_str:
                        continue

                    print(f"📡 Raw line: {line_str}")

                    if line_str.startswith('data: '):
                        try:
                            json_str = line_str[6:]  # Remove 'data: ' prefix
                            update = json.loads(json_str)
                            updates_received.append(update)

                            update_type = update.get('type', 'unknown')
                            message = update.get('message', '')

                            print(f"✅ {update_type}: {message}")

                            # Show detailed info for key updates
                            if update_type == "observation_completed":
                                observation = update.get("observation", "")
                                print(
                                    f"   👁️  Observation: {observation[:100]}...")

                            elif update_type == "reasoning_completed":
                                reasoning = update.get("reasoning", "")
                                confidence = update.get("confidence", 0)
                                recommended_action = update.get(
                                    "recommended_action", "")
                                print(f"   🧠 Reasoning: {reasoning[:100]}...")
                                print(f"   📊 Confidence: {confidence}")
                                print(
                                    f"   🎯 Recommended Action: {recommended_action}")

                            elif update_type == "action_completed":
                                tool_used = update.get("tool_used", "")
                                action_result = update.get("action_result", "")
                                print(f"   ⚡ Tool Used: {tool_used}")
                                print(f"   📝 Result: {action_result[:100]}...")

                            elif update_type == "analysis_completed":
                                print(f"   ✅ Analysis completed!")
                                print(
                                    f"   📊 Final confidence: {update.get('final_confidence', 0)}")
                                print(
                                    f"   🚨 Fraud detected: {update.get('fraud_detected', False)}")
                                print(
                                    f"   ⚠️  Risk level: {update.get('risk_level', 'UNKNOWN')}")
                                break

                            elif update_type == "analysis_error":
                                error = update.get("error", "")
                                print(f"   ❌ Error: {error}")
                                break

                        except json.JSONDecodeError as e:
                            print(f"❌ JSON decode error: {e}")
                            print(f"❌ Raw JSON: {json_str}")

                    elif line_str.startswith(': keepalive'):
                        print("💓 Keepalive received")

                print(f"\n📊 Summary:")
                print(f"   Total updates received: {len(updates_received)}")
                print(
                    f"   Update types: {[u.get('type') for u in updates_received]}")

                # Check for key update types
                observation_updates = [u for u in updates_received if u.get(
                    'type') == 'observation_completed']
                reasoning_updates = [u for u in updates_received if u.get(
                    'type') == 'reasoning_completed']
                action_updates = [u for u in updates_received if u.get(
                    'type') == 'action_completed']

                print(f"   Observations: {len(observation_updates)}")
                print(f"   Reasoning steps: {len(reasoning_updates)}")
                print(f"   Actions: {len(action_updates)}")

                if len(updates_received) > 0:
                    print("✅ Frontend streaming test completed successfully!")
                else:
                    print("❌ No streaming updates received")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Testing Frontend Streaming Connection")
    print("=" * 80)

    asyncio.run(test_frontend_streaming())
