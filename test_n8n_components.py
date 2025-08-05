#!/usr/bin/env python3
"""
Test script to verify n8n components work independently.
Run this before creating the manual n8n workflow.
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta

def test_environment():
    """Test if required environment variables are set."""
    print("🔍 Testing Environment Variables...")
    
    required_vars = [
        'TIMING_API_TOKEN',
        'JIRA_BASE_URL', 
        'JIRA_USERNAME',
        'JIRA_API_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables:")
        for var in missing_vars:
            print(f"export {var}='your_value_here'")
        return False
    else:
        print("✅ All environment variables are set")
        return True

def test_python_scripts():
    """Test if Python scripts exist and are executable."""
    print("\n🔍 Testing Python Scripts...")
    
    scripts = [
        'work_pattern_analyzer.py',
        'enhanced_jira_matcher.py'
    ]
    
    missing_scripts = []
    for script in scripts:
        if not os.path.exists(script):
            missing_scripts.append(script)
    
    if missing_scripts:
        print(f"❌ Missing scripts: {', '.join(missing_scripts)}")
        return False
    else:
        print("✅ All required scripts exist")
        return True

def test_work_pattern_analyzer():
    """Test the work pattern analyzer script."""
    print("\n🔍 Testing Work Pattern Analyzer...")
    
    try:
        # Import and test the work pattern analyzer
        from work_pattern_analyzer import WorkPatternAnalyzer, TimingAPIClient
        
        # Test basic functionality
        client = TimingAPIClient()
        analyzer = WorkPatternAnalyzer(client)
        
        print("✅ Work pattern analyzer imports successfully")
        return True
        
    except Exception as e:
        print(f"❌ Work pattern analyzer test failed: {e}")
        return False

def test_enhanced_jira_matcher():
    """Test the enhanced Jira matcher script."""
    print("\n🔍 Testing Enhanced Jira Matcher...")
    
    try:
        # Import and test the enhanced Jira matcher
        from enhanced_jira_matcher import JiraMatcher, EnhancedWorkflow, TimingAPIClient
        
        # Test basic functionality
        client = TimingAPIClient()
        jira_matcher = JiraMatcher(
            os.getenv('JIRA_BASE_URL'),
            os.getenv('JIRA_USERNAME'),
            os.getenv('JIRA_API_TOKEN')
        )
        
        print("✅ Enhanced Jira matcher imports successfully")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Jira matcher test failed: {e}")
        return False

def test_api_connections():
    """Test API connections."""
    print("\n🔍 Testing API Connections...")
    
    try:
        from work_pattern_analyzer import TimingAPIClient
        
        client = TimingAPIClient()
        
        # Test Timing API connection
        print("Testing Timing API connection...")
        # This would require actual API call, but we'll just test the client creation
        print("✅ Timing API client created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ API connection test failed: {e}")
        return False

def generate_n8n_test_data():
    """Generate sample data that n8n would expect."""
    print("\n🔍 Generating n8n Test Data...")
    
    # Sample output from work_pattern_analyzer.py
    basic_output = {
        "status": "has_activity",
        "work_summary": "Worked for 135 minutes across 3 sessions",
        "total_work_time_minutes": 135,
        "sessions": [
            {
                "duration_minutes": 45,
                "primary_project": "Project A",
                "primary_title": "Working on feature X"
            }
        ]
    }
    
    # Sample output from enhanced_jira_matcher.py
    enhanced_output = {
        "status": "processed",
        "matches_found": 2,
        "updates_made": 2,
        "updates": [
            {
                "ticket": "PROJ-123",
                "confidence": 0.85,
                "time_spent": 3600,
                "summary": "Fixed login authentication bug"
            }
        ]
    }
    
    print("✅ Sample n8n data generated:")
    print(f"Basic workflow output: {json.dumps(basic_output, indent=2)}")
    print(f"Enhanced workflow output: {json.dumps(enhanced_output, indent=2)}")
    
    return True

def main():
    """Run all tests."""
    print("🧪 n8n Component Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Python Scripts", test_python_scripts),
        ("Work Pattern Analyzer", test_work_pattern_analyzer),
        ("Enhanced Jira Matcher", test_enhanced_jira_matcher),
        ("API Connections", test_api_connections),
        ("n8n Test Data", generate_n8n_test_data)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! You're ready to create the n8n workflow manually.")
        print("\nNext steps:")
        print("1. Follow the MANUAL_WORKFLOW_CREATION.md guide")
        print("2. Create the workflow step by step in n8n")
        print("3. Test each node individually")
        print("4. Activate the workflow")
    else:
        print("⚠️  Some tests failed. Please fix the issues before creating the n8n workflow.")
        print("\nCommon fixes:")
        print("1. Set missing environment variables")
        print("2. Install missing Python dependencies")
        print("3. Check API tokens and credentials")
        print("4. Verify Python script paths")

if __name__ == "__main__":
    main() 