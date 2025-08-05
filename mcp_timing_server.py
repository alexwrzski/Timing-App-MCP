#!/usr/bin/env python3
"""
MCP Server for Timing App API

This server provides tools to interact with the Timing App API,
allowing AI assistants to manage projects, time entries, reports, and teams.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Timing API configuration
TIMING_API_BASE_URL = "https://web.timingapp.com/api/v1"
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


class TimingAPIClient:
    """Client for interacting with the Timing App API."""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {
            **DEFAULT_HEADERS,
            "Authorization": f"Bearer {api_token}"
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a request to the Timing API."""
        url = f"{TIMING_API_BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise Exception(f"Request failed: {e}")
    
    async def get_projects_hierarchy(self, team_id: Optional[str] = None) -> Dict[str, Any]:
        """Get the complete project hierarchy."""
        params = {"team_id": team_id} if team_id else None
        return await self._make_request("GET", "/projects/hierarchy", params=params)
    
    async def get_projects(
        self, 
        title: Optional[str] = None,
        hide_archived: Optional[bool] = None,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get a list of projects."""
        params = {}
        if title:
            params["title"] = title
        if hide_archived is not None:
            params["hide_archived"] = "1" if hide_archived else "0"
        if team_id:
            params["team_id"] = team_id
        
        return await self._make_request("GET", "/projects", params=params)
    
    async def create_project(
        self,
        title: str,
        parent: Optional[str] = None,
        color: Optional[str] = None,
        productivity_score: Optional[int] = None,
        is_archived: Optional[bool] = None,
        team_id: Optional[str] = None,
        notes: Optional[str] = None,
        custom_fields: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a new project."""
        data = {"title": title}
        
        if parent:
            data["parent"] = parent
        if color:
            data["color"] = color
        if productivity_score is not None:
            data["productivity_score"] = productivity_score
        if is_archived is not None:
            data["is_archived"] = is_archived
        if team_id:
            data["team_id"] = team_id
        if notes:
            data["notes"] = notes
        if custom_fields:
            data["custom_fields"] = custom_fields
        
        return await self._make_request("POST", "/projects", data=data)
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get a specific project."""
        return await self._make_request("GET", f"/projects/{project_id}")
    
    async def update_project(
        self,
        project_id: str,
        title: Optional[str] = None,
        color: Optional[str] = None,
        productivity_score: Optional[int] = None,
        is_archived: Optional[bool] = None,
        notes: Optional[str] = None,
        custom_fields: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Update a project."""
        data = {}
        
        if title:
            data["title"] = title
        if color:
            data["color"] = color
        if productivity_score is not None:
            data["productivity_score"] = productivity_score
        if is_archived is not None:
            data["is_archived"] = is_archived
        if notes:
            data["notes"] = notes
        if custom_fields:
            data["custom_fields"] = custom_fields
        
        return await self._make_request("PUT", f"/projects/{project_id}", data=data)
    
    async def delete_project(self, project_id: str) -> None:
        """Delete a project."""
        await self._make_request("DELETE", f"/projects/{project_id}")
    
    async def start_timer(
        self,
        title: Optional[str] = None,
        project: Optional[str] = None,
        notes: Optional[str] = None,
        start_date: Optional[str] = None,
        replace_existing: Optional[bool] = None,
        custom_fields: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Start a new timer."""
        data = {}
        
        if title:
            data["title"] = title
        if project:
            data["project"] = project
        if notes:
            data["notes"] = notes
        if start_date:
            data["start_date"] = start_date
        if replace_existing is not None:
            data["replace_existing"] = replace_existing
        if custom_fields:
            data["custom_fields"] = custom_fields
        
        return await self._make_request("POST", "/time-entries/start", data=data)
    
    async def stop_timer(self) -> Dict[str, Any]:
        """Stop the currently running timer."""
        return await self._make_request("PUT", "/time-entries/stop")
    
    async def get_running_timer(self) -> Dict[str, Any]:
        """Get the currently running timer."""
        return await self._make_request("GET", "/time-entries/running")
    
    async def get_latest_time_entry(self) -> Dict[str, Any]:
        """Get the latest time entry."""
        return await self._make_request("GET", "/time-entries/latest")
    
    async def get_time_entries(
        self,
        start_date_min: Optional[str] = None,
        start_date_max: Optional[str] = None,
        projects: Optional[List[str]] = None,
        include_child_projects: Optional[bool] = None,
        search_query: Optional[str] = None,
        is_running: Optional[bool] = None,
        include_project_data: Optional[bool] = None,
        include_team_members: Optional[bool] = None,
        team_members: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get a list of time entries."""
        params = {}
        
        if start_date_min:
            params["start_date_min"] = start_date_min
        if start_date_max:
            params["start_date_max"] = start_date_max
        if projects:
            params["projects[]"] = projects
        if include_child_projects is not None:
            params["include_child_projects"] = "1" if include_child_projects else "0"
        if search_query:
            params["search_query"] = search_query
        if is_running is not None:
            params["is_running"] = "1" if is_running else "0"
        if include_project_data is not None:
            params["include_project_data"] = "1" if include_project_data else "0"
        if include_team_members is not None:
            params["include_team_members"] = "1" if include_team_members else "0"
        if team_members:
            params["team_members[]"] = team_members
        
        return await self._make_request("GET", "/time-entries", params=params)
    
    async def create_time_entry(
        self,
        start_date: str,
        end_date: str,
        title: Optional[str] = None,
        project: Optional[str] = None,
        notes: Optional[str] = None,
        replace_existing: Optional[bool] = None,
        custom_fields: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a new time entry."""
        data = {
            "start_date": start_date,
            "end_date": end_date
        }
        
        if title:
            data["title"] = title
        if project:
            data["project"] = project
        if notes:
            data["notes"] = notes
        if replace_existing is not None:
            data["replace_existing"] = replace_existing
        if custom_fields:
            data["custom_fields"] = custom_fields
        
        return await self._make_request("POST", "/time-entries", data=data)
    
    async def get_time_entry(self, time_entry_id: str, other_user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific time entry."""
        params = {"other_user_id": other_user_id} if other_user_id else None
        return await self._make_request("GET", f"/time-entries/{time_entry_id}", params=params)
    
    async def update_time_entry(
        self,
        time_entry_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        title: Optional[str] = None,
        project: Optional[str] = None,
        notes: Optional[str] = None,
        replace_existing: Optional[bool] = None,
        custom_fields: Optional[Dict] = None,
        other_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a time entry."""
        data = {}
        
        if start_date:
            data["start_date"] = start_date
        if end_date:
            data["end_date"] = end_date
        if title:
            data["title"] = title
        if project:
            data["project"] = project
        if notes:
            data["notes"] = notes
        if replace_existing is not None:
            data["replace_existing"] = replace_existing
        if custom_fields:
            data["custom_fields"] = custom_fields
        
        params = {"other_user_id": other_user_id} if other_user_id else None
        return await self._make_request("PUT", f"/time-entries/{time_entry_id}", data=data, params=params)
    
    async def delete_time_entry(self, time_entry_id: str, other_user_id: Optional[str] = None) -> None:
        """Delete a time entry."""
        params = {"other_user_id": other_user_id} if other_user_id else None
        await self._make_request("DELETE", f"/time-entries/{time_entry_id}", params=params)
    
    async def generate_report(
        self,
        include_app_usage: Optional[bool] = None,
        include_team_members: Optional[bool] = None,
        team_members: Optional[List[str]] = None,
        start_date_min: Optional[str] = None,
        start_date_max: Optional[str] = None,
        projects: Optional[List[str]] = None,
        include_child_projects: Optional[bool] = None,
        search_query: Optional[str] = None,
        columns: Optional[List[str]] = None,
        project_grouping_level: Optional[int] = None,
        include_project_data: Optional[bool] = None,
        timespan_grouping_mode: Optional[str] = None,
        sort: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate a report."""
        params = {}
        
        if include_app_usage is not None:
            params["include_app_usage"] = "1" if include_app_usage else "0"
        if include_team_members is not None:
            params["include_team_members"] = "1" if include_team_members else "0"
        if team_members:
            params["team_members[]"] = team_members
        if start_date_min:
            params["start_date_min"] = start_date_min
        if start_date_max:
            params["start_date_max"] = start_date_max
        if projects:
            params["projects[]"] = projects
        if include_child_projects is not None:
            params["include_child_projects"] = "1" if include_child_projects else "0"
        if search_query:
            params["search_query"] = search_query
        if columns:
            params["columns[]"] = columns
        if project_grouping_level is not None:
            params["project_grouping_level"] = str(project_grouping_level)
        if include_project_data is not None:
            params["include_project_data"] = "1" if include_project_data else "0"
        if timespan_grouping_mode:
            params["timespan_grouping_mode"] = timespan_grouping_mode
        if sort:
            params["sort[]"] = sort
        
        return await self._make_request("GET", "/report", params=params)
    
    async def get_teams(self) -> Dict[str, Any]:
        """Get a list of teams."""
        return await self._make_request("GET", "/teams")
    
    async def get_team_members(self, team_id: str) -> Dict[str, Any]:
        """Get team members."""
        return await self._make_request("GET", f"/teams/{team_id}/members")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class TimingMCPServer:
    """MCP Server for Timing App API."""
    
    def __init__(self):
        self.server = Server("timing-app")
        self.api_client: Optional[TimingAPIClient] = None
        self.setup_tools()
    
    def setup_tools(self):
        """Setup all the tools for the MCP server."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            return ListToolsResult(
                tools=[
                    Tool(
                        name="configure_api",
                        description="Configure the Timing API with your authentication token",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "api_token": {
                                    "type": "string",
                                    "description": "Your Timing API token"
                                }
                            },
                            "required": ["api_token"]
                        }
                    ),
                    Tool(
                        name="get_projects_hierarchy",
                        description="Get the complete project hierarchy",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "team_id": {
                                    "type": "string",
                                    "description": "The ID of the team to list projects for"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="get_projects",
                        description="Get a list of projects",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Filter for projects whose title contains all words in this parameter"
                                },
                                "hide_archived": {
                                    "type": "boolean",
                                    "description": "If true, archived projects and their children will not be included"
                                },
                                "team_id": {
                                    "type": "string",
                                    "description": "The ID of the team to list projects for"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="create_project",
                        description="Create a new project",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "The project's title"
                                },
                                "parent": {
                                    "type": "string",
                                    "description": "A reference to an existing project"
                                },
                                "color": {
                                    "type": "string",
                                    "description": "The project's color in hexadecimal format (#RRGGBB)"
                                },
                                "productivity_score": {
                                    "type": "integer",
                                    "description": "The project's productivity rating (-1 to 1)"
                                },
                                "is_archived": {
                                    "type": "boolean",
                                    "description": "Whether the project has been archived"
                                },
                                "team_id": {
                                    "type": "string",
                                    "description": "The ID of the team to add the project to"
                                },
                                "notes": {
                                    "type": "string",
                                    "description": "The project's notes"
                                },
                                "custom_fields": {
                                    "type": "object",
                                    "description": "Custom field name/value pairs"
                                }
                            },
                            "required": ["title"]
                        }
                    ),
                    Tool(
                        name="get_project",
                        description="Get a specific project",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "The ID of the project"
                                }
                            },
                            "required": ["project_id"]
                        }
                    ),
                    Tool(
                        name="update_project",
                        description="Update a project",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "The ID of the project"
                                },
                                "title": {
                                    "type": "string",
                                    "description": "The project's title"
                                },
                                "color": {
                                    "type": "string",
                                    "description": "The project's color in hexadecimal format (#RRGGBB)"
                                },
                                "productivity_score": {
                                    "type": "integer",
                                    "description": "The project's productivity rating (-1 to 1)"
                                },
                                "is_archived": {
                                    "type": "boolean",
                                    "description": "Whether the project has been archived"
                                },
                                "notes": {
                                    "type": "string",
                                    "description": "The project's notes"
                                },
                                "custom_fields": {
                                    "type": "object",
                                    "description": "Custom field name/value pairs"
                                }
                            },
                            "required": ["project_id"]
                        }
                    ),
                    Tool(
                        name="delete_project",
                        description="Delete a project and all of its children",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "The ID of the project to delete"
                                }
                            },
                            "required": ["project_id"]
                        }
                    ),
                    Tool(
                        name="start_timer",
                        description="Start a new timer",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "The timer's title"
                                },
                                "project": {
                                    "type": "string",
                                    "description": "The project this timer is associated with"
                                },
                                "notes": {
                                    "type": "string",
                                    "description": "The timer's notes"
                                },
                                "start_date": {
                                    "type": "string",
                                    "description": "The date this timer should have started at (ISO8601 format)"
                                },
                                "replace_existing": {
                                    "type": "boolean",
                                    "description": "If true, any existing time entries that overlap will be adjusted"
                                },
                                "custom_fields": {
                                    "type": "object",
                                    "description": "Custom field name/value pairs"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="stop_timer",
                        description="Stop the currently running timer",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="get_running_timer",
                        description="Get the currently running timer",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="get_latest_time_entry",
                        description="Get the latest time entry",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="get_time_entries",
                        description="Get a list of time entries",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "start_date_min": {
                                    "type": "string",
                                    "description": "Filter by start date (minimum)"
                                },
                                "start_date_max": {
                                    "type": "string",
                                    "description": "Filter by start date (maximum)"
                                },
                                "projects": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Filter by projects"
                                },
                                "include_child_projects": {
                                    "type": "boolean",
                                    "description": "Include time entries from child projects"
                                },
                                "search_query": {
                                    "type": "string",
                                    "description": "Search in title and notes"
                                },
                                "is_running": {
                                    "type": "boolean",
                                    "description": "Filter by running status"
                                },
                                "include_project_data": {
                                    "type": "boolean",
                                    "description": "Include project data in response"
                                },
                                "include_team_members": {
                                    "type": "boolean",
                                    "description": "Include team members' time entries"
                                },
                                "team_members": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Filter by specific team members"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="create_time_entry",
                        description="Create a new time entry",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "start_date": {
                                    "type": "string",
                                    "description": "The time entry's start date and time (ISO8601 format)"
                                },
                                "end_date": {
                                    "type": "string",
                                    "description": "The time entry's end date and time (ISO8601 format)"
                                },
                                "title": {
                                    "type": "string",
                                    "description": "The time entry's title"
                                },
                                "project": {
                                    "type": "string",
                                    "description": "The project this time entry is associated with"
                                },
                                "notes": {
                                    "type": "string",
                                    "description": "The time entry's notes"
                                },
                                "replace_existing": {
                                    "type": "boolean",
                                    "description": "If true, any existing time entries that overlap will be adjusted"
                                },
                                "custom_fields": {
                                    "type": "object",
                                    "description": "Custom field name/value pairs"
                                }
                            },
                            "required": ["start_date", "end_date"]
                        }
                    ),
                    Tool(
                        name="get_time_entry",
                        description="Get a specific time entry",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "time_entry_id": {
                                    "type": "string",
                                    "description": "The ID of the time entry"
                                },
                                "other_user_id": {
                                    "type": "string",
                                    "description": "The ID of the other user (for team members)"
                                }
                            },
                            "required": ["time_entry_id"]
                        }
                    ),
                    Tool(
                        name="update_time_entry",
                        description="Update a time entry",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "time_entry_id": {
                                    "type": "string",
                                    "description": "The ID of the time entry"
                                },
                                "start_date": {
                                    "type": "string",
                                    "description": "The time entry's start date and time (ISO8601 format)"
                                },
                                "end_date": {
                                    "type": "string",
                                    "description": "The time entry's end date and time (ISO8601 format)"
                                },
                                "title": {
                                    "type": "string",
                                    "description": "The time entry's title"
                                },
                                "project": {
                                    "type": "string",
                                    "description": "The project this time entry is associated with"
                                },
                                "notes": {
                                    "type": "string",
                                    "description": "The time entry's notes"
                                },
                                "replace_existing": {
                                    "type": "boolean",
                                    "description": "If true, any existing time entries that overlap will be adjusted"
                                },
                                "custom_fields": {
                                    "type": "object",
                                    "description": "Custom field name/value pairs"
                                },
                                "other_user_id": {
                                    "type": "string",
                                    "description": "The ID of the other user (for team members)"
                                }
                            },
                            "required": ["time_entry_id"]
                        }
                    ),
                    Tool(
                        name="delete_time_entry",
                        description="Delete a time entry",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "time_entry_id": {
                                    "type": "string",
                                    "description": "The ID of the time entry to delete"
                                },
                                "other_user_id": {
                                    "type": "string",
                                    "description": "The ID of the other user (for team members)"
                                }
                            },
                            "required": ["time_entry_id"]
                        }
                    ),
                    Tool(
                        name="generate_report",
                        description="Generate a report with time entries and optionally app usage",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "include_app_usage": {
                                    "type": "boolean",
                                    "description": "Whether to include app usage in the report"
                                },
                                "include_team_members": {
                                    "type": "boolean",
                                    "description": "Include time entries from other team members"
                                },
                                "team_members": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Filter by specific team members"
                                },
                                "start_date_min": {
                                    "type": "string",
                                    "description": "Filter by start date (minimum)"
                                },
                                "start_date_max": {
                                    "type": "string",
                                    "description": "Filter by start date (maximum)"
                                },
                                "projects": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Filter by projects"
                                },
                                "include_child_projects": {
                                    "type": "boolean",
                                    "description": "Include time entries from child projects"
                                },
                                "search_query": {
                                    "type": "string",
                                    "description": "Search in title and notes"
                                },
                                "columns": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Which columns to show (project, title, notes, timespan, user)"
                                },
                                "project_grouping_level": {
                                    "type": "integer",
                                    "description": "Group projects by level in hierarchy"
                                },
                                "include_project_data": {
                                    "type": "boolean",
                                    "description": "Include project data in response"
                                },
                                "timespan_grouping_mode": {
                                    "type": "string",
                                    "description": "Group by time span (exact, day, week, month, year)"
                                },
                                "sort": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Sort columns (prefix with - for descending)"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="get_teams",
                        description="Get a list of teams you are a member of",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="get_team_members",
                        description="Get team members for a specific team",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "team_id": {
                                    "type": "string",
                                    "description": "The ID of the team"
                                }
                            },
                            "required": ["team_id"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            if not self.api_client and name != "configure_api":
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Please configure the API first using the 'configure_api' tool with your Timing API token."
                        )
                    ]
                )
            
            try:
                if name == "configure_api":
                    api_token = arguments["api_token"]
                    self.api_client = TimingAPIClient(api_token)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text="✅ Timing API configured successfully! You can now use all the available tools."
                            )
                        ]
                    )
                
                elif name == "get_projects_hierarchy":
                    result = await self.api_client.get_projects_hierarchy(
                        team_id=arguments.get("team_id")
                    )
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Project Hierarchy:\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "get_projects":
                    result = await self.api_client.get_projects(
                        title=arguments.get("title"),
                        hide_archived=arguments.get("hide_archived"),
                        team_id=arguments.get("team_id")
                    )
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Projects:\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "create_project":
                    result = await self.api_client.create_project(**arguments)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"✅ Project created successfully!\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "get_project":
                    result = await self.api_client.get_project(arguments["project_id"])
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Project Details:\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "update_project":
                    project_id = arguments.pop("project_id")
                    result = await self.api_client.update_project(project_id, **arguments)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"✅ Project updated successfully!\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "delete_project":
                    await self.api_client.delete_project(arguments["project_id"])
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"✅ Project {arguments['project_id']} deleted successfully!"
                            )
                        ]
                    )
                
                elif name == "start_timer":
                    result = await self.api_client.start_timer(**arguments)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"✅ Timer started successfully!\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "stop_timer":
                    result = await self.api_client.stop_timer()
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"✅ Timer stopped successfully!\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "get_running_timer":
                    result = await self.api_client.get_running_timer()
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Currently Running Timer:\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "get_latest_time_entry":
                    result = await self.api_client.get_latest_time_entry()
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Latest Time Entry:\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "get_time_entries":
                    result = await self.api_client.get_time_entries(**arguments)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Time Entries:\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "create_time_entry":
                    result = await self.api_client.create_time_entry(**arguments)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"✅ Time entry created successfully!\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "get_time_entry":
                    result = await self.api_client.get_time_entry(
                        arguments["time_entry_id"],
                        arguments.get("other_user_id")
                    )
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Time Entry Details:\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "update_time_entry":
                    time_entry_id = arguments.pop("time_entry_id")
                    result = await self.api_client.update_time_entry(time_entry_id, **arguments)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"✅ Time entry updated successfully!\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "delete_time_entry":
                    await self.api_client.delete_time_entry(
                        arguments["time_entry_id"],
                        arguments.get("other_user_id")
                    )
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"✅ Time entry {arguments['time_entry_id']} deleted successfully!"
                            )
                        ]
                    )
                
                elif name == "generate_report":
                    result = await self.api_client.generate_report(**arguments)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Report Generated:\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "get_teams":
                    result = await self.api_client.get_teams()
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Teams:\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                elif name == "get_team_members":
                    result = await self.api_client.get_team_members(arguments["team_id"])
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Team Members:\n```json\n{json.dumps(result, indent=2)}\n```"
                            )
                        ]
                    )
                
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Unknown tool: {name}"
                            )
                        ]
                    )
            
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"❌ Error: {str(e)}"
                        )
                    ]
                )
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="timing-app",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )


async def main():
    """Main entry point."""
    server = TimingMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 