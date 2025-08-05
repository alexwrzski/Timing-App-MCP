#!/usr/bin/env python3
"""
Quick Test for Timing App Workflow

This script tests the workflow components without n8n.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from work_pattern_analyzer import WorkPatternAnalyzer
from mcp_timing_server import TimingAPIClient


async def test_workflow():
    """Test the workflow components."""
    
    print("🧪 Testing Timing App Workflow Components")
    print("=" * 50)
    
    # Check environment variables
    timing_token = os.getenv('TIMING_API_TOKEN')
    if not timing_token:
        print("❌ TIMING_API_TOKEN not set")
        print("Please set it: export TIMING_API_TOKEN='your_token_here'")
        return False
    
    print("✅ TIMING_API_TOKEN found")
    
    try:
        # Test Timing API connection
        print("\n🔗 Testing Timing API connection...")
        timing_client = TimingAPIClient(timing_token)
        
        # Test getting time entries
        print("📊 Getting recent time entries...")
        time_entries = await timing_client.get_time_entries(
            start_date_min=(datetime.now() - timedelta(hours=2)).isoformat(),
            include_project_data=True
        )
        
        if time_entries.get('data'):
            print(f"✅ Found {len(time_entries['data'])} time entries")
        else:
            print("ℹ️  No recent time entries found")
        
        # Test work pattern analyzer
        print("\n🔍 Testing work pattern analyzer...")
        analyzer = WorkPatternAnalyzer(timing_client)
        result = await analyzer.get_continuous_work_summary(hours_back=2)
        
        print("📊 Analysis Results:")
        print(json.dumps(result, indent=2, default=str))
        
        await timing_client.close()
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    from datetime import datetime, timedelta
    
    success = asyncio.run(test_workflow())
    
    if success:
        print("\n🎉 Workflow is ready to use!")
        print("You can now run: python3 standalone_workflow.py --once")
    else:
        print("\n🔧 Please fix the issues above before proceeding.")
        sys.exit(1) 