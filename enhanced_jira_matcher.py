#!/usr/bin/env python3
"""
Enhanced Jira Matcher for Timing App Integration

This module provides intelligent matching between Timing App work sessions
and Jira tickets where the user is the assignee.
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import httpx


@dataclass
class JiraTicket:
    """Represents a Jira ticket with matching information."""
    key: str
    summary: str
    description: str
    assignee: str
    status: str
    project: str
    issue_type: str
    priority: str
    labels: List[str]
    components: List[str]
    match_confidence: float = 0.0
    matched_keywords: List[str] = None


class JiraMatcher:
    """Matches work sessions to Jira tickets where user is assignee."""
    
    def __init__(self, jira_base_url: str, jira_username: str, jira_api_token: str):
        self.jira_base_url = jira_base_url.rstrip('/')
        self.jira_username = jira_username
        self.jira_api_token = jira_api_token
        self.client = httpx.AsyncClient(
            auth=(jira_username, jira_api_token),
            timeout=30.0
        )
        
        # Keywords for different work types
        self.work_type_keywords = {
            'bug': ['bug', 'fix', 'issue', 'error', 'crash', 'broken', 'debug'],
            'feature': ['feature', 'implement', 'develop', 'build', 'create', 'add'],
            'test': ['test', 'testing', 'qa', 'quality', 'verify', 'validate'],
            'documentation': ['doc', 'document', 'write', 'update', 'create'],
            'review': ['review', 'code review', 'pr', 'pull request', 'feedback'],
            'meeting': ['meeting', 'call', 'discussion', 'planning', 'sync'],
            'research': ['research', 'investigate', 'explore', 'analyze', 'study']
        }
        
        # Priority keywords
        self.priority_keywords = {
            'high': ['urgent', 'critical', 'blocker', 'high priority', 'asap'],
            'medium': ['normal', 'medium', 'standard'],
            'low': ['low priority', 'nice to have', 'enhancement']
        }
    
    async def get_my_jira_tickets(self, status_filter: Optional[List[str]] = None) -> List[JiraTicket]:
        """Get all Jira tickets assigned to the current user."""
        
        # Build JQL query
        jql_parts = [
            f"assignee = {self.jira_username}",
            "ORDER BY updated DESC"
        ]
        
        if status_filter:
            status_conditions = [f'status = "{status}"' for status in status_filter]
            jql_parts.insert(1, f"AND ({' OR '.join(status_conditions)})")
        
        jql = " ".join(jql_parts)
        
        # Get tickets from Jira API
        url = f"{self.jira_base_url}/rest/api/3/search"
        params = {
            "jql": jql,
            "maxResults": 100,
            "fields": "summary,description,assignee,status,project,issuetype,priority,labels,components"
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            tickets = []
            for issue in data.get('issues', []):
                fields = issue['fields']
                ticket = JiraTicket(
                    key=issue['key'],
                    summary=fields.get('summary', ''),
                    description=fields.get('description', ''),
                    assignee=fields.get('assignee', {}).get('displayName', ''),
                    status=fields.get('status', {}).get('name', ''),
                    project=fields.get('project', {}).get('name', ''),
                    issue_type=fields.get('issuetype', {}).get('name', ''),
                    priority=fields.get('priority', {}).get('name', ''),
                    labels=fields.get('labels', []),
                    components=[comp.get('name', '') for comp in fields.get('components', [])]
                )
                tickets.append(ticket)
            
            return tickets
            
        except Exception as e:
            print(f"Error fetching Jira tickets: {e}")
            return []
    
    def match_work_to_tickets(self, work_sessions: List[Dict], jira_tickets: List[JiraTicket]) -> List[Dict]:
        """Match work sessions to appropriate Jira tickets."""
        
        matches = []
        
        for session in work_sessions:
            best_match = None
            best_confidence = 0.0
            
            # Extract work information
            work_text = self._extract_work_text(session)
            work_keywords = self._extract_keywords(work_text)
            
            for ticket in jira_tickets:
                # Calculate match confidence
                confidence = self._calculate_match_confidence(session, ticket, work_keywords)
                
                if confidence > best_confidence and confidence > 0.3:  # Minimum threshold
                    best_confidence = confidence
                    best_match = ticket
            
            if best_match:
                match_result = {
                    'work_session': session,
                    'jira_ticket': best_match.key,
                    'confidence': best_confidence,
                    'matched_keywords': best_match.matched_keywords,
                    'ticket_summary': best_match.summary,
                    'ticket_status': best_match.status
                }
                matches.append(match_result)
        
        return matches
    
    def _extract_work_text(self, session: Dict) -> str:
        """Extract all text from a work session for keyword matching."""
        
        text_parts = []
        
        # Add session title and summary
        text_parts.append(session.get('primary_title', ''))
        text_parts.append(session.get('work_summary', ''))
        
        # Add all entry titles and notes
        for entry in session.get('all_entries', []):
            text_parts.append(entry.get('title', ''))
            text_parts.append(entry.get('notes', ''))
        
        return ' '.join(text_parts).lower()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from work text."""
        
        # Remove common words and extract keywords
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        # Split into words and filter
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in common_words and len(word) > 2]
        
        return keywords
    
    def _calculate_match_confidence(self, session: Dict, ticket: JiraTicket, work_keywords: List[str]) -> float:
        """Calculate confidence score for matching work to a Jira ticket."""
        
        confidence = 0.0
        matched_keywords = []
        
        # Combine all ticket text for matching
        ticket_text = f"{ticket.summary} {ticket.description} {' '.join(ticket.labels)} {' '.join(ticket.components)}"
        ticket_text = ticket_text.lower()
        
        # 1. Direct keyword matching (highest weight)
        for keyword in work_keywords:
            if keyword in ticket_text:
                confidence += 0.3
                matched_keywords.append(keyword)
        
        # 2. Work type matching
        work_type = self._determine_work_type(session)
        if work_type and work_type in ticket.issue_type.lower():
            confidence += 0.2
        
        # 3. Project name matching
        session_projects = [p.lower() for p in session.get('related_projects', [])]
        if ticket.project.lower() in session_projects:
            confidence += 0.25
        
        # 4. Priority matching
        work_priority = self._determine_work_priority(session)
        if work_priority and work_priority in ticket.priority.lower():
            confidence += 0.1
        
        # 5. Recent activity bonus (if ticket was recently updated)
        # This would require additional Jira API calls for update timestamps
        
        # Store matched keywords for debugging
        ticket.matched_keywords = matched_keywords
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _determine_work_type(self, session: Dict) -> Optional[str]:
        """Determine the type of work from the session."""
        
        work_text = self._extract_work_text(session).lower()
        
        for work_type, keywords in self.work_type_keywords.items():
            if any(keyword in work_text for keyword in keywords):
                return work_type
        
        return None
    
    def _determine_work_priority(self, session: Dict) -> Optional[str]:
        """Determine the priority of work from the session."""
        
        work_text = self._extract_work_text(session).lower()
        
        for priority, keywords in self.priority_keywords.items():
            if any(keyword in work_text for keyword in keywords):
                return priority
        
        return None
    
    async def update_jira_ticket(self, ticket_key: str, work_summary: str, time_spent: int) -> bool:
        """Update a Jira ticket with work information."""
        
        # Format time spent
        hours = time_spent // 3600
        minutes = (time_spent % 3600) // 60
        
        if hours > 0:
            time_text = f"{hours}h {minutes}m"
        else:
            time_text = f"{minutes}m"
        
        # Create comment
        comment_body = f"""
Work completed: {work_summary}

**Time spent:** {time_text}
**Completed at:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

{work_summary}
        """.strip()
        
        url = f"{self.jira_base_url}/rest/api/3/issue/{ticket_key}/comment"
        data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment_body
                            }
                        ]
                    }
                ]
            }
        }
        
        try:
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error updating Jira ticket {ticket_key}: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Enhanced workflow integration
class EnhancedWorkflow:
    """Enhanced workflow that matches work to Jira tickets."""
    
    def __init__(self, timing_client, jira_matcher):
        self.timing_client = timing_client
        self.jira_matcher = jira_matcher
    
    async def process_work_and_update_jira(self, hours_back: int = 2) -> Dict[str, Any]:
        """Process recent work and update matching Jira tickets."""
        
        # Get recent work sessions
        from work_pattern_analyzer import WorkPatternAnalyzer
        analyzer = WorkPatternAnalyzer(self.timing_client)
        work_analysis = await analyzer.analyze_recent_activity(hours_back)
        
        if not work_analysis['has_activity']:
            return {
                'status': 'no_activity',
                'message': 'No recent work activity detected'
            }
        
        # Get user's Jira tickets
        jira_tickets = await self.jira_matcher.get_my_jira_tickets(
            status_filter=['In Progress', 'To Do', 'In Review']
        )
        
        # Match work to tickets
        matches = self.jira_matcher.match_work_to_tickets(
            work_analysis['sessions'], 
            jira_tickets
        )
        
        # Update matched tickets
        updates_made = []
        for match in matches:
            session = match['work_session']
            ticket_key = match['jira_ticket']
            
            success = await self.jira_matcher.update_jira_ticket(
                ticket_key,
                session.work_summary,
                session.total_duration
            )
            
            if success:
                updates_made.append({
                    'ticket': ticket_key,
                    'confidence': match['confidence'],
                    'time_spent': session.total_duration,
                    'summary': session.work_summary
                })
        
        return {
            'status': 'processed',
            'total_sessions': len(work_analysis['sessions']),
            'total_work_time': work_analysis['total_work_time'],
            'matches_found': len(matches),
            'updates_made': len(updates_made),
            'updates': updates_made,
            'unmatched_sessions': len(work_analysis['sessions']) - len(matches)
        }


# Example usage
async def example_enhanced_workflow():
    """Example of the enhanced workflow."""
    
    from mcp_timing_server import TimingAPIClient
    
    # Initialize clients
    timing_client = TimingAPIClient("your_timing_token")
    jira_matcher = JiraMatcher(
        jira_base_url="https://your-domain.atlassian.net",
        jira_username="your-email@domain.com",
        jira_api_token="your_jira_api_token"
    )
    
    # Create enhanced workflow
    workflow = EnhancedWorkflow(timing_client, jira_matcher)
    
    # Process work and update Jira
    result = await workflow.process_work_and_update_jira(hours_back=2)
    
    print("Enhanced Workflow Results:")
    print(json.dumps(result, indent=2, default=str))
    
    # Close clients
    await timing_client.close()
    await jira_matcher.close()


if __name__ == "__main__":
    asyncio.run(example_enhanced_workflow()) 