"""
Data aggregation and processing module
Combines data from multiple collectors and removes duplicates
"""

from datetime import datetime
from typing import List, Dict, Any, Union
from dataclasses import dataclass, asdict
from collectors.browser import BrowserActivity
from collectors.ai_chats import AIChatActivity


@dataclass
class ActivityEntry:
    """Generic activity entry combining all data sources"""
    timestamp: datetime
    activity_type: str  # 'browser', 'file', 'git', 'ai_chat'
    title: str
    details: Dict[str, Any]
    category: str = "uncategorized"


class DataAggregator:
    """Aggregates and processes data from multiple collectors"""
    
    def __init__(self, settings):
        """Initialize aggregator with settings"""
        self.settings = settings
    
    def combine(self, data_collections: List[List[Any]]) -> List[ActivityEntry]:
        """Combine data from multiple collectors into unified format"""
        all_activities = []
        
        for collection in data_collections:
            if not collection:
                continue
            
            # Process based on data type
            if isinstance(collection[0], BrowserActivity):
                all_activities.extend(self._process_browser_activities(collection))
            elif isinstance(collection[0], AIChatActivity):
                all_activities.extend(self._process_ai_chat_activities(collection))
            # TODO: Add processors for other activity types
        
        # Remove duplicates and sort by timestamp
        unique_activities = self._remove_duplicates(all_activities)
        return sorted(unique_activities, key=lambda x: x.timestamp)
    
    def _process_browser_activities(self, browser_activities: List[BrowserActivity]) -> List[ActivityEntry]:
        """Convert browser activities to generic activity entries"""
        activities = []
        
        for browser_activity in browser_activities:
            # Categorize the activity
            category = self._categorize_browser_activity(browser_activity)
            
            activity = ActivityEntry(
                timestamp=browser_activity.timestamp,
                activity_type="browser",
                title=browser_activity.title,
                details={
                    "url": browser_activity.url,
                    "domain": browser_activity.domain,
                    "browser": browser_activity.browser,
                    "visit_count": browser_activity.visit_count
                },
                category=category
            )
            
            activities.append(activity)
        
        return activities
    
    def _process_ai_chat_activities(self, ai_chat_activities: List[AIChatActivity]) -> List[ActivityEntry]:
        """Convert AI chat activities to generic activity entries"""
        activities = []
        
        for chat_activity in ai_chat_activities:
            # Categorize the AI chat based on topic and content
            category = self._categorize_ai_chat_activity(chat_activity)
            
            # Create a descriptive title
            title = f"{chat_activity.ai_service.title()} Chat: {chat_activity.topic}"
            
            activity = ActivityEntry(
                timestamp=chat_activity.timestamp,
                activity_type="ai_chat",
                title=title,
                details={
                    "ai_service": chat_activity.ai_service,
                    "topic": chat_activity.topic,
                    "conversation_id": chat_activity.conversation_id,
                    "user_message": chat_activity.user_message,
                    "ai_response": chat_activity.ai_response,
                    "message_count": chat_activity.message_count
                },
                category=category
            )
            
            activities.append(activity)
        
        return activities
    
    def _categorize_browser_activity(self, activity: BrowserActivity) -> str:
        """Categorize browser activity based on URL and title"""
        url_lower = activity.url.lower()
        title_lower = activity.title.lower()
        domain_lower = activity.domain.lower()
        
        # Get categorization keywords from settings
        work_keywords = self.settings.get('processing.categorization.work_keywords', [])
        learning_keywords = self.settings.get('processing.categorization.learning_keywords', [])
        entertainment_keywords = self.settings.get('processing.categorization.entertainment_keywords', [])
        
        # Check for work-related activity
        for keyword in work_keywords:
            if keyword.lower() in url_lower or keyword.lower() in title_lower or keyword.lower() in domain_lower:
                return "work"
        
        # Check for learning activity
        for keyword in learning_keywords:
            if keyword.lower() in url_lower or keyword.lower() in title_lower or keyword.lower() in domain_lower:
                return "learning"
        
        # Check for entertainment
        for keyword in entertainment_keywords:
            if keyword.lower() in url_lower or keyword.lower() in title_lower or keyword.lower() in domain_lower:
                return "entertainment"
        
        # Special domain-based categorization
        if any(domain in domain_lower for domain in ['github.com', 'stackoverflow.com', 'docs.microsoft.com']):
            return "work"
        elif any(domain in domain_lower for domain in ['youtube.com', 'netflix.com', 'twitch.tv']):
            return "entertainment"
        elif any(domain in domain_lower for domain in ['wikipedia.org', 'coursera.org', 'udemy.com']):
            return "learning"
        
        return "general"
    
    def _categorize_ai_chat_activity(self, activity: AIChatActivity) -> str:
        """Categorize AI chat activity based on topic and content"""
        topic_lower = activity.topic.lower()
        user_message_lower = activity.user_message.lower()
        
        # Programming and development related
        programming_keywords = ['programming', 'code', 'debug', 'function', 'python', 'javascript', 'git', 'api']
        if any(kw in topic_lower or kw in user_message_lower for kw in programming_keywords):
            return "work"
        
        # Learning and education
        learning_keywords = ['learning', 'explain', 'what is', 'how to', 'tutorial', 'understand']
        if any(kw in topic_lower or kw in user_message_lower for kw in learning_keywords):
            return "learning"
        
        # Problem solving and troubleshooting
        problem_keywords = ['problem solving', 'fix', 'error', 'issue', 'help', 'troubleshoot']
        if any(kw in topic_lower or kw in user_message_lower for kw in problem_keywords):
            return "work"
        
        # Creative and content generation
        creative_keywords = ['creation', 'write', 'generate', 'create', 'design', 'plan']
        if any(kw in topic_lower or kw in user_message_lower for kw in creative_keywords):
            return "work"
        
        # Default to learning for AI interactions
        return "learning"
    
    def _remove_duplicates(self, activities: List[ActivityEntry]) -> List[ActivityEntry]:
        """Remove duplicate activities based on timestamp and title"""
        seen = set()
        unique_activities = []
        
        for activity in activities:
            # Create a key for duplicate detection
            key = (
                activity.timestamp.replace(second=0, microsecond=0),  # Round to minute
                activity.activity_type,
                activity.title[:100]  # First 100 chars of title
            )
            
            if key not in seen:
                seen.add(key)
                unique_activities.append(activity)
        
        return unique_activities
    
    def get_statistics(self, activities: List[ActivityEntry]) -> Dict[str, Any]:
        """Generate statistics from activities"""
        if not activities:
            return {}
        
        stats = {
            "total_activities": len(activities),
            "time_range": {
                "start": min(activities, key=lambda x: x.timestamp).timestamp,
                "end": max(activities, key=lambda x: x.timestamp).timestamp
            },
            "by_category": {},
            "by_type": {},
            "by_hour": {}
        }
        
        # Count by category
        for activity in activities:
            category = activity.category
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        
        # Count by activity type
        for activity in activities:
            activity_type = activity.activity_type
            stats["by_type"][activity_type] = stats["by_type"].get(activity_type, 0) + 1
        
        # Count by hour of day
        for activity in activities:
            hour = activity.timestamp.hour
            stats["by_hour"][hour] = stats["by_hour"].get(hour, 0) + 1
        
        return stats
