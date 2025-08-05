#!/usr/bin/env python3
"""
Standalone Timing App to Jira Workflow

This script runs independently without n8n and provides the same functionality:
- Checks for recent work activity every 30 minutes
- Matches work to Jira tickets where you're the assignee
- Updates Jira tickets with work progress
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from work_pattern_analyzer import WorkPatternAnalyzer
from enhanced_jira_matcher import JiraMatcher, EnhancedWorkflow
from mcp_timing_server import TimingAPIClient


class StandaloneWorkflow:
    """Standalone workflow that runs without n8n."""
    
    def __init__(self):
        self.timing_token = os.getenv('TIMING_API_TOKEN')
        self.jira_url = os.getenv('JIRA_BASE_URL')
        self.jira_username = os.getenv('JIRA_USERNAME')
        self.jira_token = os.getenv('JIRA_API_TOKEN')
        
        if not self.timing_token:
            print("❌ TIMING_API_TOKEN environment variable not set")
            sys.exit(1)
    
    async def run_single_check(self):
        """Run a single check for work activity and update Jira."""
        
        print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Starting work check...")
        
        try:
            # Initialize clients
            timing_client = TimingAPIClient(self.timing_token)
            
            if self.jira_url and self.jira_username and self.jira_token:
                jira_matcher = JiraMatcher(self.jira_url, self.jira_username, self.jira_token)
                workflow = EnhancedWorkflow(timing_client, jira_matcher)
                
                # Process work and update Jira
                result = await workflow.process_work_and_update_jira(hours_back=2)
                
                print("📊 Workflow Results:")
                print(json.dumps(result, indent=2, default=str))
                
                await jira_matcher.close()
            else:
                # Just analyze work without Jira integration
                analyzer = WorkPatternAnalyzer(timing_client)
                result = await analyzer.get_continuous_work_summary(hours_back=2)
                
                print("📊 Work Analysis Results:")
                print(json.dumps(result, indent=2, default=str))
            
            await timing_client.close()
            
        except Exception as e:
            print(f"❌ Error during work check: {e}")
    
    async def run_continuous(self, interval_minutes=30):
        """Run the workflow continuously with the specified interval."""
        
        print(f"🚀 Starting standalone workflow (checking every {interval_minutes} minutes)")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                await self.run_single_check()
                
                # Wait for next check
                print(f"⏳ Waiting {interval_minutes} minutes until next check...")
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n🛑 Workflow stopped by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("⏳ Retrying in 5 minutes...")
                await asyncio.sleep(300)


async def main():
    """Main entry point."""
    
    # Check if running in single check mode or continuous mode
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Single check mode
        workflow = StandaloneWorkflow()
        await workflow.run_single_check()
    else:
        # Continuous mode
        workflow = StandaloneWorkflow()
        await workflow.run_continuous()


if __name__ == "__main__":
    asyncio.run(main()) 