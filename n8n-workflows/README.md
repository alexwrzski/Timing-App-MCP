# n8n Workflows for Timing App Integration

This folder contains various n8n workflows for integrating with the Timing App API and updating Jira tickets.

## 📁 **Workflow Files**

### **✅ Recommended Workflows (Correctly Formatted)**

#### **1. `correct_n8n_workflow.json`** - Basic Work Detection
- **Purpose**: Simple workflow that detects work activity
- **Features**: 
  - Runs every 30 minutes
  - Executes `work_pattern_analyzer.py`
  - Logs work activity
- **Use Case**: Testing basic functionality
- **Import Status**: ✅ Should import successfully

#### **2. `correct_enhanced_n8n_workflow.json`** - Full Jira Integration
- **Purpose**: Complete automation with Jira ticket updates
- **Features**:
  - Runs every 30 minutes
  - Executes `enhanced_jira_matcher.py`
  - Fetches your Jira tickets
  - Matches work to tickets
  - Updates Jira with work progress
- **Use Case**: Production automation
- **Import Status**: ✅ Should import successfully

### **⚠️ Legacy Workflows (May Have Import Issues)**

#### **3. `enhanced_n8n_workflow.json`** - Original Enhanced Version
- **Purpose**: Full Jira integration (original version)
- **Features**: Complete automation with intelligent matching
- **Import Status**: ⚠️ May have import issues

#### **4. `enhanced_n8n_workflow_fixed.json`** - Fixed Version
- **Purpose**: Attempted fix of the enhanced workflow
- **Features**: Same as enhanced but with fixes
- **Import Status**: ⚠️ May still have issues

#### **5. `n8n_workflow_example.json`** - Basic Example
- **Purpose**: Simple example workflow
- **Features**: Basic work detection
- **Import Status**: ⚠️ May have import issues

#### **6. `simple_n8n_workflow.json`** - Simplified Version
- **Purpose**: Simplified workflow for troubleshooting
- **Features**: Basic functionality
- **Import Status**: ⚠️ May have import issues

#### **7. `minimal_n8n_workflow.json`** - Minimal Version
- **Purpose**: Most basic workflow possible
- **Features**: Just cron trigger and command execution
- **Import Status**: ⚠️ May have import issues

## 🚀 **Getting Started**

### **Step 1: Choose Your Workflow**
- **For testing**: Use `correct_n8n_workflow.json`
- **For production**: Use `correct_enhanced_n8n_workflow.json`

### **Step 2: Import into n8n**
1. Open n8n
2. Click the three dots menu (⋮)
3. Select "Import from File"
4. Choose your workflow file

### **Step 3: Configure Credentials**
- **Timing API**: Set your Timing App API token
- **Jira API**: Configure Jira credentials (for enhanced workflows)

### **Step 4: Test the Workflow**
1. Activate the workflow
2. Test manually first
3. Monitor execution logs

## 🔧 **Configuration Requirements**

### **Environment Variables**
```bash
export TIMING_API_TOKEN="your_timing_token"
export JIRA_BASE_URL="https://your-domain.atlassian.net"
export JIRA_USERNAME="your-email@domain.com"
export JIRA_API_TOKEN="your_jira_api_token"
```

### **Python Scripts**
Ensure these scripts are available:
- `work_pattern_analyzer.py` (for basic workflows)
- `enhanced_jira_matcher.py` (for enhanced workflows)

### **n8n Credentials**
1. Go to n8n Settings → Credentials
2. Add Jira API credentials
3. Configure with your Jira details

## 📊 **Expected Outputs**

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

### **If Import Fails**
1. **Try the corrected workflows** first
2. **Validate JSON** using online tools
3. **Check n8n version** - update if needed
4. **Use standalone script** as alternative

### **Common Issues**
- **Missing credentials** - Configure all required APIs
- **Python path issues** - Use full paths to scripts
- **Permission issues** - Ensure n8n can execute Python
- **Environment variables** - Set all required tokens

## 🚀 **Alternative: Standalone Solution**

If n8n continues to have issues, use the standalone Python workflow:

```bash
# Test the standalone workflow
python3 quick_test.py

# Run once
python3 standalone_workflow.py --once

# Run continuously
python3 standalone_workflow.py
```

## 📝 **Workflow Comparison**

| Workflow | Complexity | Jira Integration | Import Status | Recommended |
|----------|------------|------------------|---------------|-------------|
| `correct_n8n_workflow.json` | Low | ❌ | ✅ | ✅ Yes |
| `correct_enhanced_n8n_workflow.json` | High | ✅ | ✅ | ✅ Yes |
| `enhanced_n8n_workflow.json` | High | ✅ | ⚠️ | ❌ No |
| `simple_n8n_workflow.json` | Low | ❌ | ⚠️ | ❌ No |
| `minimal_n8n_workflow.json` | Very Low | ❌ | ⚠️ | ❌ No |

## 📚 **Additional Resources**

- **Main Guide**: `../N8N_CORRECT_FORMAT_GUIDE.md`
- **Troubleshooting**: `../N8N_IMPORT_TROUBLESHOOTING.md`
- **Jira Matching**: `../JIRA_MATCHING_GUIDE.md`
- **Work Detection**: `../CONTINUOUS_WORK_DETECTION.md` 