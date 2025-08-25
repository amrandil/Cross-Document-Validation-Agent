#!/usr/bin/env python3
"""
Test script to verify ReAct agent streaming updates.
"""

import sys
import os
import asyncio
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))


async def test_react_streaming():
    """Test ReAct agent streaming functionality."""

    print("=" * 80)
    print("REACT AGENT STREAMING TEST")
    print("=" * 80)

    # Sample extracted content
    extracted_content = {
        "invoice.pdf": "This is a sample invoice with product details and pricing information.",
        "packing_list.pdf": "This is a packing list showing quantities and weights of shipped items."
    }

    try:
        from src.agent.executor import FraudDetectionExecutor

        executor = FraudDetectionExecutor()

        # Create a queue to capture streaming updates
        stream_queue = asyncio.Queue()

        print("✅ Starting ReAct streaming test...")

        # Start streaming analysis in background
        analysis_task = asyncio.create_task(
            executor.execute_react_fraud_analysis_stream(
                extracted_content, {}, stream_queue)
        )

        # Consume streaming updates
        updates_received = []
        while True:
            try:
                # Wait for updates with timeout
                update = await asyncio.wait_for(stream_queue.get(), timeout=30.0)
                updates_received.append(update)

                # Print update details
                update_type = update.get("type", "unknown")
                message = update.get("message", "")
                print(f"📡 {update_type}: {message}")

                # Show detailed info for key updates
                if update_type == "observation_completed":
                    observation = update.get("observation", "")
                    print(f"   👁️  Observation: {observation[:100]}...")

                elif update_type == "reasoning_completed":
                    reasoning = update.get("reasoning", "")
                    confidence = update.get("confidence", 0)
                    recommended_action = update.get("recommended_action", "")
                    print(f"   🧠 Reasoning: {reasoning[:100]}...")
                    print(f"   📊 Confidence: {confidence}")
                    print(f"   🎯 Recommended Action: {recommended_action}")

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

            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for updates")
                break

        # Wait for analysis task to complete
        try:
            await analysis_task
        except Exception as e:
            print(f"❌ Analysis task failed: {str(e)}")

        print(f"\n📊 Summary:")
        print(f"   Total updates received: {len(updates_received)}")
        print(f"   Update types: {[u.get('type') for u in updates_received]}")

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
            print("✅ Streaming test completed successfully!")
        else:
            print("❌ No streaming updates received")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Testing ReAct Agent Streaming")
    print("=" * 80)

    asyncio.run(test_react_streaming())
