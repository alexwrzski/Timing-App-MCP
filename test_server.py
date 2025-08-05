#!/usr/bin/env python3
"""
Test script for the Timing App MCP Server

This script tests the basic functionality of the MCP server.
"""

import asyncio
import json
from mcp_timing_server import TimingMCPServer


async def test_server():
    """Test the MCP server functionality."""
    
    server = TimingMCPServer()
    
    # Test 1: List tools
    print("Testing tool listing...")
    tools = await server.server.list_tools()
    print(f"Available tools: {len(tools.tools)}")
    for tool in tools.tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Test 2: Test configuration (without real token)
    print("\nTesting configuration...")
    try:
        result = await server.server.call_tool(
            "configure_api",
            {"api_token": "test_token"}
        )
        print(f"Configuration test result: {result}")
    except Exception as e:
        print(f"Expected error (no real token): {e}")
    
    # Test 3: Test tool schema
    print("\nTesting tool schemas...")
    for tool in tools.tools:
        if tool.name == "start_timer":
            print(f"start_timer schema: {tool.inputSchema}")
            break
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    print("Timing App MCP Server Test")
    print("=" * 30)
    
    asyncio.run(test_server()) 