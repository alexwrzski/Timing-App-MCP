# Continuous Work Detection for Task Switching

## 🎯 The Challenge

You're dealing with a common productivity pattern where people:
- Switch between tasks frequently (1 minute to 2 hours)
- Have background work that continues across multiple time entries
- Need to aggregate related activities into meaningful Jira updates

## ✅ Yes, Both LLMs and n8n Can Detect Continuous Work!

### How the Work Pattern Analyzer Works

The `WorkPatternAnalyzer` I created uses several intelligent techniques to detect continuous work despite task switching:

#### 1. **Time Gap Analysis**
```python
max_gap_minutes = 15  # Consider work continuous if gaps < 15 min
```
- Groups time entries with gaps ≤ 15 minutes into the same work session
- Accounts for natural breaks (bathroom, coffee, quick distractions)

#### 2. **Project Relationship Detection**
- Analyzes project hierarchies and relationships
- Identifies when multiple tasks belong to the same larger project
- Groups related work even if individual tasks are different

#### 3. **Keyword-Based Correlation**
```python
related_keywords = [
    'bug', 'fix', 'issue', 'feature', 'implement', 'develop',
    'test', 'debug', 'refactor', 'optimize', 'review', 'document',
    'meeting', 'call', 'discussion', 'planning', 'research'
]
```
- Identifies semantically related work across different time entries
- Detects when tasks are part of the same logical workflow

#### 4. **Jira Ticket Extraction**
```python
jira_project_patterns = {
    'PROJ': r'PROJ-\d+',
    'DEV': r'DEV-\d+',
    'BUG': r'BUG-\d+',
    'FEAT': r'FEAT-\d+'
}
```
- Automatically extracts Jira ticket numbers from time entries
- Links related work to the same ticket

## 🔍 Example Scenarios

### Scenario 1: Bug Fixing Session
```
9:00-9:15  "Investigate login bug" (PROJ-123)
9:15-9:45  "Coffee break"
9:45-10:30 "Debug authentication issue" (PROJ-123)
10:30-11:00 "Test fix" (PROJ-123)
11:00-11:30 "Document changes" (PROJ-123)
```
**Detection:** All entries grouped as one 2.5-hour session on PROJ-123

### Scenario 2: Multi-Project Development
```
9:00-9:30  "Frontend development" (FEAT-456)
9:30-10:00 "API integration" (FEAT-456)
10:00-10:15 "Quick meeting"
10:15-11:00 "Backend optimization" (FEAT-456)
```
**Detection:** 2.5-hour session primarily focused on FEAT-456

### Scenario 3: Context Switching
```
9:00-9:10  "Email review"
9:10-9:45  "Code review" (DEV-789)
9:45-10:00 "Slack messages"
10:00-10:30 "Implement feedback" (DEV-789)
```
**Detection:** 1.5-hour session with primary focus on DEV-789

## 🛠️ n8n Integration

### Workflow Structure
1. **Cron Trigger** (every 30 minutes)
2. **Python Script** (runs work pattern analyzer)
3. **Condition Check** (has activity?)
4. **Jira Update** (if activity detected)
5. **Comment Addition** (detailed work summary)

### Key Benefits for n8n
- **Intelligent Grouping**: Automatically groups related work
- **Context Preservation**: Maintains work context across task switches
- **Jira Integration**: Direct ticket updates with meaningful summaries
- **Configurable**: Adjustable parameters for different work patterns

## 🤖 LLM Integration

### How LLMs Can Help
1. **Natural Language Summaries**: Convert technical work into readable updates
2. **Context Understanding**: Better interpretation of work relationships
3. **Smart Categorization**: Identify work types and priorities
4. **Jira Comment Generation**: Create professional, detailed comments

### Example LLM Processing
```python
# Input: Raw work session data
work_session = {
    "duration": 5400,  # 1.5 hours
    "projects": ["Frontend", "API", "Testing"],
    "activities": ["Code review", "Bug fix", "Testing"]
}

# LLM Output: Professional summary
summary = "Completed 1.5 hours of development work including code review, 
bug fixes, and testing across frontend and API components. 
Primary focus was on PROJ-123 with related work on DEV-456."
```

## 📊 Detection Accuracy

### What It Detects Well
- ✅ **Continuous work sessions** (gaps ≤ 15 minutes)
- ✅ **Related projects** (same parent project)
- ✅ **Jira ticket patterns** (PROJ-123, DEV-456, etc.)
- ✅ **Semantic relationships** (bug → fix → test)
- ✅ **Time-based patterns** (morning vs afternoon work)

### What It Might Miss
- ❌ **Very short tasks** (< 5 minutes)
- ❌ **Unrelated context switches** (work → personal)
- ❌ **Non-standard Jira patterns** (custom ticket formats)
- ❌ **Complex multi-project work** (requires manual review)

## 🎛️ Configuration Options

### Adjustable Parameters
```python
# Time-based grouping
max_gap_minutes = 15        # Increase for more relaxed grouping
min_session_duration = 300   # 5 minutes minimum
max_session_duration = 14400 # 4 hours maximum

# Work pattern detection
related_keywords = [...]     # Add your domain-specific keywords
jira_patterns = {...}        # Customize Jira ticket patterns
```

### Customization for Your Work Style
1. **Frequent Switcher**: Increase `max_gap_minutes` to 20-30
2. **Deep Focus**: Decrease `max_gap_minutes` to 10-15
3. **Long Sessions**: Increase `max_session_duration` to 6-8 hours
4. **Short Tasks**: Decrease `min_session_duration` to 60-180 seconds

## 🚀 Implementation Steps

### 1. Set Up the Analyzer
```bash
# Install dependencies
pip install -r requirements.txt

# Configure your API token
export TIMING_API_TOKEN="your_token_here"
```

### 2. Test the Detection
```python
from work_pattern_analyzer import WorkPatternAnalyzer
from mcp_timing_server import TimingAPIClient

client = TimingAPIClient("your_token")
analyzer = WorkPatternAnalyzer(client)

# Test with your data
summary = await analyzer.get_continuous_work_summary(hours_back=2)
print(json.dumps(summary, indent=2))
```

### 3. Integrate with n8n
1. Import the workflow JSON
2. Configure Jira credentials
3. Set up the Python script node
4. Test with your Timing App data

### 4. Fine-tune Parameters
- Adjust gap detection based on your work style
- Add custom keywords for your domain
- Configure Jira ticket patterns for your organization

## 📈 Expected Results

### Typical Detection Patterns
- **2-4 hour work sessions** from multiple short tasks
- **Project-focused summaries** despite task switching
- **Automatic Jira updates** with meaningful context
- **Professional work logs** suitable for reporting

### Example Output
```json
{
  "status": "has_activity",
  "total_work_time_minutes": 135,
  "sessions_count": 3,
  "primary_focus": {
    "primary_project": "Frontend Development",
    "time_spent": 5400,
    "confidence": 0.85
  },
  "jira_updates": [
    {
      "ticket": "PROJ-123",
      "time_spent": 5400,
      "summary": "Worked on frontend features and bug fixes"
    }
  ],
  "work_summary": "Worked for 135 minutes across 3 sessions on Frontend Development"
}
```

## 🎯 Conclusion

**Yes, both LLMs and n8n automation can effectively detect continuous work despite task switching!** The key is using intelligent pattern recognition that goes beyond simple time aggregation to understand work relationships, project hierarchies, and semantic connections between tasks.

The `WorkPatternAnalyzer` provides a solid foundation that you can customize for your specific work patterns and integrate seamlessly with your n8n → Jira workflow. 