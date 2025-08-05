# n8n Workflow Import Troubleshooting

## 🚨 **"propertyValues[itemName] is not iterable" Error**

This error typically occurs when there's an issue with the n8n workflow JSON structure. Here are several solutions:

## 🔧 **Solution 1: Use the Fixed Workflow**

I've created a fixed version of the workflow that should import without issues:

**File:** `enhanced_n8n_workflow_fixed.json`

### Key Fixes Made:
- Removed problematic `webhookId` properties
- Simplified node connections
- Ensured proper JSON structure
- Removed complex expressions that might cause parsing issues

## 🔧 **Solution 2: Use the Simple Workflow**

If the enhanced workflow still has issues, try the simple version:

**File:** `simple_n8n_workflow.json`

This is a basic workflow that:
- Runs every 30 minutes
- Calls the work pattern analyzer
- Logs activity (no Jira integration yet)
- Should import without any issues

## 🔧 **Solution 3: Manual Workflow Creation**

If JSON import continues to fail, create the workflow manually in n8n:

### Step 1: Create Basic Workflow
1. Create new workflow in n8n
2. Add **Cron Trigger** node
3. Set interval to 30 minutes

### Step 2: Add Python Script Node
1. Add **Execute Command** node
2. Set command: `python3`
3. Set arguments: `work_pattern_analyzer.py`

### Step 3: Add Condition Node
1. Add **IF** node
2. Set condition: `$json.status equals "has_activity"`

### Step 4: Add Jira Nodes (Optional)
1. Add **Jira** node for getting tickets
2. Add **Jira** node for updating tickets
3. Configure with your Jira credentials

## 🔧 **Solution 4: Validate JSON Structure**

If you want to fix the original workflow, check for these common issues:

### Common Problems:
1. **Invalid node IDs**: Ensure all node IDs are unique strings
2. **Missing connections**: Check that all referenced nodes exist
3. **Invalid expressions**: Simplify complex expressions
4. **Version compatibility**: Ensure workflow version matches your n8n version

### JSON Validation:
```bash
# Validate JSON syntax
python -m json.tool enhanced_n8n_workflow.json

# Check for common issues
grep -n "webhookId\|itemName" enhanced_n8n_workflow.json
```

## 🔧 **Solution 5: Step-by-Step Import**

### Method 1: Import Node by Node
1. Create empty workflow
2. Import individual nodes from the JSON
3. Manually recreate connections

### Method 2: Copy-Paste Method
1. Open the JSON file in a text editor
2. Copy the content
3. In n8n, create new workflow
4. Use "Import from JSON" feature
5. Paste the content

### Method 3: Template Method
1. Create a basic workflow template
2. Export it to JSON
3. Compare structure with our workflow
4. Adapt our workflow to match the template structure

## 🛠️ **Alternative: Use the Python Script Directly**

If n8n import continues to fail, you can run the Python script directly:

### Option 1: Cron Job
```bash
# Add to crontab
*/30 * * * * cd /path/to/timing-app-mcp && python3 work_pattern_analyzer.py
```

### Option 2: Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/timing-analyzer.service

[Unit]
Description=Timing App Work Analyzer
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /path/to/timing-app-mcp/work_pattern_analyzer.py
User=your-username
Environment=TIMING_API_TOKEN=your_token

[Install]
WantedBy=multi-user.target
```

### Option 3: Docker Container
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "work_pattern_analyzer.py"]
```

## 🔍 **Debugging Steps**

### 1. Check n8n Version
```bash
# Check your n8n version
n8n --version

# Update if needed
npm update -g n8n
```

### 2. Validate Workflow JSON
```bash
# Install jq for JSON validation
brew install jq  # macOS
sudo apt install jq  # Ubuntu

# Validate JSON
jq '.' enhanced_n8n_workflow_fixed.json
```

### 3. Test with Minimal Workflow
Create a minimal workflow with just:
- Cron Trigger
- Execute Command
- NoOp (for logging)

### 4. Check n8n Logs
```bash
# Check n8n logs for errors
n8n start --tunnel
# Look for import-related errors in the console
```

## 📋 **Recommended Approach**

1. **Start with the simple workflow** (`simple_n8n_workflow.json`)
2. **Test basic functionality** (work detection)
3. **Add Jira integration manually** if needed
4. **Gradually enhance** the workflow

## 🎯 **Quick Test**

Try this minimal workflow to test basic functionality:

```json
{
  "name": "Test Workflow",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "minutes",
              "minutesInterval": 30
            }
          ]
        }
      },
      "id": "trigger",
      "name": "Cron Trigger",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "command": "python3",
        "arguments": "work_pattern_analyzer.py"
      },
      "id": "analyzer",
      "name": "Work Analyzer",
      "type": "n8n-nodes-base.executeCommand",
      "typeVersion": 1,
      "position": [460, 300]
    }
  ],
  "connections": {
    "Cron Trigger": {
      "main": [
        [
          {
            "node": "Work Analyzer",
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
  "id": "test-workflow",
  "tags": []
}
```

This should import without any issues and can serve as a foundation for building the full workflow. 