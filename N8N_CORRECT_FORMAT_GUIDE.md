# n8n Correct Format Guide

Based on the official n8n documentation, here's how to create properly formatted workflows that will import without issues.

## 🔍 **Key Issues Found**

After examining the official n8n documentation, I identified several issues with our previous workflow JSON files:

### **1. Missing Required Fields**
- `versionId` field was missing
- `meta` section was incomplete
- Node structure didn't match official examples

### **2. Incorrect Node Structure**
- Node IDs should be unique strings
- Position arrays should be `[x, y]` format
- Credentials should be properly structured

### **3. Connection Format**
- Connections should reference node names, not IDs
- Proper indexing for multiple connections

## ✅ **Correct Workflow Structure**

Based on the official n8n examples, here's the correct format:

```json
{
  "name": "Workflow Name",
  "nodes": [
    {
      "parameters": {
        // Node-specific parameters
      },
      "id": "unique-node-id",
      "name": "Node Display Name",
      "type": "n8n-nodes-base.nodeType",
      "typeVersion": 1,
      "position": [x, y]
    }
  ],
  "connections": {
    "Node Display Name": {
      "main": [
        [
          {
            "node": "Next Node Name",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": false,
  "settings": {
    "executionOrder": "v1"
  },
  "versionId": "1",
  "meta": {
    "templateCredsSetupCompleted": true
  },
  "id": "workflow-id",
  "tags": []
}
```

## 🛠️ **Fixed Workflow Files**

I've created two correctly formatted workflows:

### **1. Basic Workflow** (`correct_n8n_workflow.json`)
- Simple workflow with work detection
- No Jira integration
- Minimal complexity for testing

### **2. Enhanced Workflow** (`correct_enhanced_n8n_workflow.json`)
- Full Jira integration
- Intelligent work matching
- Complete automation

## 📋 **Import Steps**

### **Method 1: Import from File**
1. Open n8n
2. Click the three dots menu (⋮)
3. Select "Import from File"
4. Choose `correct_n8n_workflow.json` or `correct_enhanced_n8n_workflow.json`

### **Method 2: Copy-Paste**
1. Open the JSON file in a text editor
2. Copy the entire content
3. In n8n, create new workflow
4. Click the three dots menu (⋮)
5. Select "Import from URL"
6. Paste the JSON content

### **Method 3: Manual Creation**
If import still fails, create manually:

1. **Create new workflow**
2. **Add Cron Trigger node**
   - Set interval to 30 minutes
3. **Add Execute Command node**
   - Command: `python3`
   - Arguments: `work_pattern_analyzer.py`
4. **Add IF node**
   - Condition: `$json.status equals "has_activity"`
5. **Add Jira nodes** (for enhanced version)
   - Configure with your Jira credentials

## 🔧 **Configuration Required**

### **Environment Setup**
```bash
# Set your API tokens
export TIMING_API_TOKEN="your_timing_token"
export JIRA_BASE_URL="https://your-domain.atlassian.net"
export JIRA_USERNAME="your-email@domain.com"
export JIRA_API_TOKEN="your_jira_api_token"
```

### **n8n Credentials**
1. Go to n8n Settings → Credentials
2. Add Jira API credentials
3. Configure with your Jira details

### **Python Script Location**
Ensure the Python scripts are in the same directory as n8n or provide full paths:
- `work_pattern_analyzer.py` (for basic workflow)
- `enhanced_jira_matcher.py` (for enhanced workflow)

## 🎯 **Testing the Workflow**

### **Step 1: Test Basic Functionality**
1. Import `correct_n8n_workflow.json`
2. Configure your Timing API token
3. Test the workflow manually
4. Check if work detection works

### **Step 2: Test Jira Integration**
1. Import `correct_enhanced_n8n_workflow.json`
2. Configure Jira credentials
3. Test with your Jira tickets
4. Verify ticket updates

## 📊 **Expected Results**

### **Basic Workflow Output**
```json
{
  "status": "has_activity",
  "work_summary": "Worked for 135 minutes across 3 sessions",
  "total_work_time_minutes": 135
}
```

### **Enhanced Workflow Output**
```json
{
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
```

## 🔍 **Troubleshooting**

### **If Import Still Fails**
1. **Check n8n version** - Update if needed
2. **Validate JSON** - Use online JSON validator
3. **Try manual creation** - Build workflow step by step
4. **Use standalone script** - `python3 standalone_workflow.py`

### **Common Issues**
- **Missing credentials** - Configure Jira API credentials
- **Python path issues** - Use full paths to scripts
- **Permission issues** - Ensure n8n can execute Python
- **Environment variables** - Set all required tokens

## 🚀 **Alternative: Standalone Solution**

If n8n continues to have import issues, use the standalone Python workflow:

```bash
# Test the standalone workflow
python3 quick_test.py

# Run once
python3 standalone_workflow.py --once

# Run continuously
python3 standalone_workflow.py
```

The standalone solution provides the same functionality without n8n dependency.

## ✅ **Key Differences from Previous Versions**

1. **Proper JSON structure** - Following official n8n format
2. **Correct node references** - Using node names in connections
3. **Required fields** - Including `versionId` and `meta`
4. **Simplified expressions** - Avoiding complex template syntax
5. **Proper credentials structure** - Following n8n credential format

The corrected workflows should now import successfully into n8n! 