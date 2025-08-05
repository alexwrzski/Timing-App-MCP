#!/usr/bin/env python3
"""
Work Pattern Analyzer for Timing App

This module provides intelligent analysis of work patterns to detect continuous
work despite frequent task switching. It's designed for n8n automation and
Jira integration.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import re


@dataclass
class WorkSession:
    """Represents a continuous work session across multiple time entries."""
    start_time: datetime
    end_time: datetime
    total_duration: int  # in seconds
    primary_project: str
    primary_title: str
    all_entries: List[Dict]
    related_projects: List[str]
    work_summary: str
    jira_ticket: Optional[str] = None


class WorkPatternAnalyzer:
    """Analyzes work patterns to detect continuous work sessions."""
    
    def __init__(self, timing_client):
        self.client = timing_client
        
        # Configuration for pattern detection
        self.max_gap_minutes = 15  # Consider work continuous if gaps < 15 min
        self.min_session_duration = 300  # 5 minutes minimum for a session
        self.max_session_duration = 14400  # 4 hours maximum for a session
        
        # Keywords to identify related work
        self.related_keywords = [
            'bug', 'fix', 'issue', 'feature', 'implement', 'develop',
            'test', 'debug', 'refactor', 'optimize', 'review', 'document',
            'meeting', 'call', 'discussion', 'planning', 'research'
        ]
        
        # Project patterns for Jira integration
        self.jira_project_patterns = {
            'PROJ': r'PROJ-\d+',
            'DEV': r'DEV-\d+',
            'BUG': r'BUG-\d+',
            'FEAT': r'FEAT-\d+'
        }
    
    async def analyze_recent_activity(self, hours_back: int = 2) -> Dict[str, Any]:
        """Analyze recent activity and detect work patterns."""
        
        # Get time entries from the last N hours
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        time_entries = await self.client.get_time_entries(
            start_date_min=start_time.isoformat(),
            start_date_max=end_time.isoformat(),
            include_project_data=True
        )
        
        if not time_entries.get('data'):
            return {
                'has_activity': False,
                'message': 'No recent activity found'
            }
        
        # Group entries into work sessions
        sessions = self._group_into_sessions(time_entries['data'])
        
        # Analyze each session
        analyzed_sessions = []
        for session in sessions:
            analyzed_session = self._analyze_session(session)
            if analyzed_session:
                analyzed_sessions.append(analyzed_session)
        
        return {
            'has_activity': len(analyzed_sessions) > 0,
            'sessions': analyzed_sessions,
            'total_work_time': sum(s.total_duration for s in analyzed_sessions),
            'primary_focus': self._get_primary_focus(analyzed_sessions),
            'jira_updates': self._generate_jira_updates(analyzed_sessions)
        }
    
    def _group_into_sessions(self, time_entries: List[Dict]) -> List[List[Dict]]:
        """Group time entries into continuous work sessions."""
        
        if not time_entries:
            return []
        
        # Sort entries by start time
        sorted_entries = sorted(time_entries, key=lambda x: x['start_date'])
        
        sessions = []
        current_session = [sorted_entries[0]]
        
        for entry in sorted_entries[1:]:
            current_end = datetime.fromisoformat(current_session[-1]['end_date'].replace('Z', '+00:00'))
            next_start = datetime.fromisoformat(entry['start_date'].replace('Z', '+00:00'))
            
            gap_minutes = (next_start - current_end).total_seconds() / 60
            
            # If gap is small, consider it continuous work
            if gap_minutes <= self.max_gap_minutes:
                current_session.append(entry)
            else:
                # Start a new session
                if current_session:
                    sessions.append(current_session)
                current_session = [entry]
        
        # Add the last session
        if current_session:
            sessions.append(current_session)
        
        return sessions
    
    def _analyze_session(self, session_entries: List[Dict]) -> Optional[WorkSession]:
        """Analyze a work session and extract meaningful information."""
        
        if not session_entries:
            return None
        
        # Calculate session duration
        session_start = datetime.fromisoformat(session_entries[0]['start_date'].replace('Z', '+00:00'))
        session_end = datetime.fromisoformat(session_entries[-1]['end_date'].replace('Z', '+00:00'))
        total_duration = (session_end - session_start).total_seconds()
        
        # Filter out very short sessions
        if total_duration < self.min_session_duration:
            return None
        
        # Get project and title information
        projects = [entry.get('project', {}).get('title', 'Unknown') for entry in session_entries]
        titles = [entry.get('title', '') for entry in session_entries]
        notes = [entry.get('notes', '') for entry in session_entries]
        
        # Find primary project (most time spent)
        project_durations = defaultdict(int)
        for entry in session_entries:
            project = entry.get('project', {}).get('title', 'Unknown')
            duration = entry.get('duration', 0)
            project_durations[project] += duration
        
        primary_project = max(project_durations.items(), key=lambda x: x[1])[0]
        
        # Find primary title (most common or longest)
        title_durations = defaultdict(int)
        for entry in session_entries:
            title = entry.get('title', '')
            if title:
                duration = entry.get('duration', 0)
                title_durations[title] += duration
        
        primary_title = max(title_durations.items(), key=lambda x: x[1])[0] if title_durations else 'Work Session'
        
        # Generate work summary
        work_summary = self._generate_work_summary(session_entries, primary_project, primary_title)
        
        # Extract Jira ticket if present
        jira_ticket = self._extract_jira_ticket(session_entries)
        
        return WorkSession(
            start_time=session_start,
            end_time=session_end,
            total_duration=int(total_duration),
            primary_project=primary_project,
            primary_title=primary_title,
            all_entries=session_entries,
            related_projects=list(set(projects)),
            work_summary=work_summary,
            jira_ticket=jira_ticket
        )
    
    def _generate_work_summary(self, entries: List[Dict], primary_project: str, primary_title: str) -> str:
        """Generate a human-readable summary of the work session."""
        
        # Collect all unique activities
        activities = []
        for entry in entries:
            title = entry.get('title', '')
            notes = entry.get('notes', '')
            project = entry.get('project', {}).get('title', '')
            
            if title and title not in activities:
                activities.append(title)
            
            # Extract meaningful notes
            if notes and len(notes) > 10:
                # Clean up notes
                clean_notes = re.sub(r'\s+', ' ', notes.strip())
                if clean_notes not in activities:
                    activities.append(clean_notes)
        
        # Create summary
        if len(activities) == 1:
            return f"Focused on: {activities[0]}"
        elif len(activities) <= 3:
            return f"Worked on: {', '.join(activities)}"
        else:
            return f"Multi-tasked across {len(activities)} activities, primarily: {primary_title}"
    
    def _extract_jira_ticket(self, entries: List[Dict]) -> Optional[str]:
        """Extract Jira ticket numbers from time entries."""
        
        # Check titles, notes, and project names for Jira ticket patterns
        all_text = []
        for entry in entries:
            all_text.extend([
                entry.get('title', ''),
                entry.get('notes', ''),
                entry.get('project', {}).get('title', '')
            ])
        
        # Look for Jira ticket patterns
        for text in all_text:
            for pattern in self.jira_project_patterns.values():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(0)
        
        return None
    
    def _get_primary_focus(self, sessions: List[WorkSession]) -> Dict[str, Any]:
        """Determine the primary focus area from work sessions."""
        
        if not sessions:
            return {'focus': 'No recent activity', 'confidence': 0}
        
        # Analyze project distribution
        project_durations = defaultdict(int)
        for session in sessions:
            project_durations[session.primary_project] += session.total_duration
        
        total_time = sum(project_durations.values())
        primary_project = max(project_durations.items(), key=lambda x: x[1])
        
        confidence = primary_project[1] / total_time if total_time > 0 else 0
        
        return {
            'primary_project': primary_project[0],
            'time_spent': primary_project[1],
            'total_time': total_time,
            'confidence': confidence,
            'session_count': len(sessions)
        }
    
    def _generate_jira_updates(self, sessions: List[WorkSession]) -> List[Dict[str, Any]]:
        """Generate Jira update suggestions for work sessions."""
        
        updates = []
        
        for session in sessions:
            if session.jira_ticket:
                update = {
                    'ticket': session.jira_ticket,
                    'time_spent': session.total_duration,
                    'summary': session.work_summary,
                    'start_time': session.start_time.isoformat(),
                    'end_time': session.end_time.isoformat(),
                    'projects_involved': session.related_projects
                }
                updates.append(update)
        
        return updates
    
    async def get_continuous_work_summary(self, hours_back: int = 2) -> Dict[str, Any]:
        """Get a summary of continuous work for Jira updates."""
        
        analysis = await self.analyze_recent_activity(hours_back)
        
        if not analysis['has_activity']:
            return {
                'status': 'no_activity',
                'message': 'No recent work activity detected'
            }
        
        # Format for n8n/Jira integration
        return {
            'status': 'has_activity',
            'total_work_time_minutes': analysis['total_work_time'] // 60,
            'sessions_count': len(analysis['sessions']),
            'primary_focus': analysis['primary_focus'],
            'jira_updates': analysis['jira_updates'],
            'work_summary': self._format_work_summary(analysis['sessions']),
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_work_summary(self, sessions: List[WorkSession]) -> str:
        """Format a human-readable work summary."""
        
        if not sessions:
            return "No work sessions detected"
        
        total_minutes = sum(s.total_duration for s in sessions) // 60
        
        if len(sessions) == 1:
            session = sessions[0]
            return f"Worked for {total_minutes} minutes on {session.primary_title} ({session.primary_project})"
        
        # Multiple sessions
        projects = list(set(s.primary_project for s in sessions))
        if len(projects) == 1:
            return f"Worked for {total_minutes} minutes across {len(sessions)} sessions on {projects[0]}"
        else:
            return f"Worked for {total_minutes} minutes across {len(sessions)} sessions on {len(projects)} different projects"


# Example usage function
async def example_analysis():
    """Example of how to use the work pattern analyzer."""
    
    # This would be used in your n8n workflow
    from mcp_timing_server import TimingAPIClient
    
    # Initialize client (you'd get the token from environment or config)
    client = TimingAPIClient("your_api_token_here")
    
    # Create analyzer
    analyzer = WorkPatternAnalyzer(client)
    
    # Analyze recent activity
    summary = await analyzer.get_continuous_work_summary(hours_back=2)
    
    print("Work Analysis Results:")
    print(json.dumps(summary, indent=2, default=str))
    
    # Close client
    await client.close()


if __name__ == "__main__":
    asyncio.run(example_analysis()) 