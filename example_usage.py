#!/usr/bin/env python3
"""
Example usage of the Timing App MCP Server

This script demonstrates how to use the MCP server to interact with the Timing App API.
"""

import asyncio
import json
from mcp_timing_server import TimingMCPServer


async def example_usage():
    """Example usage of the Timing App MCP server."""
    
    # Create the server instance
    server = TimingMCPServer()
    
    # Example: Configure the API
    print("1. Configuring API...")
    config_result = await server.server.call_tool(
        "configure_api",
        {"api_token": "your_token_here"}
    )
    print(f"Configuration result: {config_result}")
    
    # Example: Get projects
    print("\n2. Getting projects...")
    projects_result = await server.server.call_tool(
        "get_projects",
        {"hide_archived": True}
    )
    print(f"Projects result: {projects_result}")
    
    # Example: Start a timer
    print("\n3. Starting a timer...")
    timer_result = await server.server.call_tool(
        "start_timer",
        {
            "title": "Example Task",
            "project": "Work/Development",
            "notes": "Working on MCP server"
        }
    )
    print(f"Timer result: {timer_result}")
    
    # Example: Generate a report
    print("\n4. Generating a report...")
    report_result = await server.server.call_tool(
        "generate_report",
        {
            "start_date_min": "2024-01-01",
            "start_date_max": "2024-12-31",
            "columns": ["project", "title", "duration"],
            "include_project_data": True
        }
    )
    print(f"Report result: {report_result}")


if __name__ == "__main__":
    print("Timing App MCP Server Example")
    print("=" * 40)
    print("Note: Replace 'your_token_here' with your actual API token")
    print()
    
    # Run the example
    asyncio.run(example_usage()) 