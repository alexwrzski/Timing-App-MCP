# Timing App MCP Server

This is a Model Context Protocol (MCP) server for the Timing App API, allowing AI assistants to interact with your Timing App data programmatically.

## Features

The MCP server provides tools for:

### Projects
- List projects hierarchically
- Get all projects with filtering
- Create new projects
- Get, update, and delete specific projects

### Time Entries
- Start and stop timers
- Get running timer and latest time entry
- List time entries with various filters
- Create, read, update, and delete time entries

### Reports
- Generate comprehensive reports with time entries and app usage
- Filter by date ranges, projects, team members
- Group by time spans and project levels

### Teams
- Get list of teams
- Get team members for specific teams

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your API Token

1. Go to [Timing App Web Dashboard](https://web.timingapp.com/integrations/tokens)
2. Click "Generate API token"
3. Copy your token

### 3. Run the MCP Server

```bash
python mcp_timing_server.py
```

## Usage

### Configuration

First, you need to configure the API with your token using the `configure_api` tool:

```json
{
  "api_token": "your_timing_api_token_here"
}
```

### Example Usage

#### Start a Timer
```json
{
  "title": "Client Meeting",
  "project": "Work/Client A",
  "notes": "Discuss project requirements"
}
```

#### Get Projects
```json
{
  "hide_archived": true
}
```

#### Generate a Report
```json
{
  "start_date_min": "2024-01-01",
  "start_date_max": "2024-01-31",
  "columns": ["project", "title", "duration"],
  "include_project_data": true
}
```

## Available Tools

### Configuration
- `configure_api` - Set up your API token

### Projects
- `get_projects_hierarchy` - Get complete project hierarchy
- `get_projects` - List projects with filtering
- `create_project` - Create a new project
- `get_project` - Get specific project details
- `update_project` - Update a project
- `delete_project` - Delete a project

### Time Entries
- `start_timer` - Start a new timer
- `stop_timer` - Stop the currently running timer
- `get_running_timer` - Get the currently running timer
- `get_latest_time_entry` - Get the latest time entry
- `get_time_entries` - List time entries with filters
- `create_time_entry` - Create a new time entry
- `get_time_entry` - Get specific time entry details
- `update_time_entry` - Update a time entry
- `delete_time_entry` - Delete a time entry

### Reports
- `generate_report` - Generate comprehensive reports

### Teams
- `get_teams` - Get list of teams
- `get_team_members` - Get team members for a team

## API Reference

The server implements all major endpoints from the Timing App API:

- **Base URL**: `https://web.timingapp.com/api/v1`
- **Authentication**: Bearer token
- **Rate Limit**: 500 requests per hour

### Date Format

Dates should be provided in ISO8601 format:
- For exact times: `2019-01-01T00:00:00+00:00`
- For date-only: `2019-01-01`

### Project References

Projects can be referenced in several ways:
- Project ID: `"/projects/1"`
- Project title: `"Project Name"`
- Title chain: `["Parent", "Child"]`

## Error Handling

The server includes comprehensive error handling:
- HTTP errors are caught and returned with details
- Invalid parameters are validated
- Network timeouts are handled gracefully

## Rate Limiting

The Timing API enforces a rate limit of 500 requests per hour. The server will return rate limit information in response headers.

## Custom Fields

Both projects and time entries support custom fields for additional metadata. Custom fields are only available via the API and not visible in the Timing app UI.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License. 