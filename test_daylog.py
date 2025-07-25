#!/usr/bin/env python3
"""
Quick test script for DayLog functionality
This creates some test data to verify the system works
"""

import sys
from datetime import datetime, date, timedelta
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from collectors.browser import BrowserActivity
from collectors.ai_chats import AIChatActivity
from collectors.git import GitActivity
from processors.aggregator import DataAggregator
from processors.report_generator import DailyReportGenerator
from config.settings import Settings


def create_test_data() -> tuple:
    """Create some test browser, AI chat, and Git activities for demonstration"""
    now = datetime.now()
    
    test_browser_activities = [
        BrowserActivity(
            timestamp=now - timedelta(hours=2),
            url="https://github.com/GitcrackerUK/Work_Log",
            title="GitHub - Work Log Repository",
            visit_count=5,
            browser="chrome",
            domain="github.com"
        ),
        BrowserActivity(
            timestamp=now - timedelta(hours=1, minutes=30),
            url="https://stackoverflow.com/questions/python-sqlite",
            title="Python SQLite Tutorial - Stack Overflow",
            visit_count=2,
            browser="chrome",
            domain="stackoverflow.com"
        ),
        BrowserActivity(
            timestamp=now - timedelta(hours=1),
            url="https://chat.openai.com/chat",
            title="ChatGPT - AI Assistant",
            visit_count=8,
            browser="edge",
            domain="chat.openai.com"
        ),
        BrowserActivity(
            timestamp=now - timedelta(minutes=45),
            url="https://www.youtube.com/watch?v=python-tutorial",
            title="Python Programming Tutorial - YouTube",
            visit_count=1,
            browser="firefox",
            domain="youtube.com"
        ),
        BrowserActivity(
            timestamp=now - timedelta(minutes=30),
            url="https://docs.python.org/3/library/sqlite3.html",
            title="sqlite3 — DB-API 2.0 interface for SQLite databases",
            visit_count=3,
            browser="chrome",
            domain="docs.python.org"
        )
    ]
    
    test_ai_chat_activities = [
        AIChatActivity(
            timestamp=now - timedelta(hours=3),
            ai_service="chatgpt",
            conversation_id="conv_001",
            user_message="Help me create a Python application for tracking daily activities",
            ai_response="I'd be happy to help you create a daily activity tracking application in Python...",
            topic="Programming",
            message_count=12
        ),
        AIChatActivity(
            timestamp=now - timedelta(hours=1, minutes=15),
            ai_service="copilot",
            conversation_id="copilot_001",
            user_message="How do I parse JSON files in Python safely?",
            ai_response="Here are several safe ways to parse JSON files in Python...",
            topic="Programming",
            message_count=6
        ),
        AIChatActivity(
            timestamp=now - timedelta(minutes=20),
            ai_service="chatgpt",
            conversation_id="conv_002",
            user_message="Explain how SQLite databases work and their advantages",
            ai_response="SQLite is a lightweight, serverless database engine...",
            topic="Learning",
            message_count=8
        )
    ]
    
    test_git_activities = [
        GitActivity(
            timestamp=now - timedelta(hours=2, minutes=30),
            activity_type="commit",
            repository="DayLog",
            branch="main",
            commit_hash="a1b2c3d4",
            commit_message="Add browser history collection feature\n\nImplemented SQLite database reading for Chrome, Edge, and Firefox browsers with proper error handling and temporary file management.",
            author="Pawel",
            files_changed=["collectors/browser.py", "main.py", "README.md"],
            insertions=145,
            deletions=12,
            repository_path="C:\\Users\\Pawel\\Desktop\\Projects\\DayLog"
        ),
        GitActivity(
            timestamp=now - timedelta(hours=1, minutes=45),
            activity_type="commit",
            repository="Work_Log",
            branch="feature/git-integration",
            commit_hash="e5f6g7h8",
            commit_message="Implement Git activity tracking",
            author="Pawel",
            files_changed=["collectors/git.py", "processors/aggregator.py"],
            insertions=78,
            deletions=5,
            repository_path="C:\\Users\\Pawel\\Desktop\\Projects\\Work_Log"
        ),
        GitActivity(
            timestamp=now - timedelta(minutes=40),
            activity_type="branch_switch",
            repository="DayLog",
            branch="main",
            commit_hash=None,
            commit_message="Switched from feature/reports to main",
            author="Pawel", 
            files_changed=[],
            insertions=0,
            deletions=0,
            repository_path="C:\\Users\\Pawel\\Desktop\\Projects\\DayLog"
        )
    ]
    
    return test_browser_activities, test_ai_chat_activities, test_git_activities


def main():
    """Test the DayLog system with sample data"""
    print("🧪 DayLog Test Mode")
    print("=" * 50)
    
    # Load settings
    settings = Settings("config/settings.json")
    
    # Create test data
    print("📊 Creating test browser, AI chat, and Git activities...")
    test_browser_activities, test_ai_chat_activities, test_git_activities = create_test_data()
    
    print(f"   ✅ Created {len(test_browser_activities)} browser activities")
    print(f"   ✅ Created {len(test_ai_chat_activities)} AI chat activities")
    print(f"   ✅ Created {len(test_git_activities)} Git activities")
    
    # Test data aggregation
    print("\n🔄 Testing data aggregation...")
    aggregator = DataAggregator(settings)
    all_activities = aggregator.combine([test_browser_activities, test_ai_chat_activities, test_git_activities])
    
    print(f"   ✅ Processed {len(all_activities)} activities")
    
    # Generate statistics
    print("\n📈 Generating statistics...")
    stats = aggregator.get_statistics(all_activities)
    
    print(f"   📊 Statistics Summary:")
    print(f"      • Total activities: {stats['total_activities']}")
    print(f"      • Categories: {', '.join(stats['by_category'].keys())}")
    print(f"      • Activity types: {', '.join(stats['by_type'].keys())}")
    
    # Show categorized activities
    print("\n📋 Activities by Category:")
    for activity in all_activities:
        time_str = activity.timestamp.strftime("%H:%M")
        category_emoji = {
            "work": "💼",
            "learning": "📚", 
            "entertainment": "🎯",
            "general": "🌐"
        }.get(activity.category, "❓")
        
        activity_emoji = {
            "browser": "🌐",
            "ai_chat": "🤖",
            "git": "⚙️"
        }.get(activity.activity_type, "❓")
        
        print(f"   {category_emoji}{activity_emoji} {time_str} - {activity.title[:60]}...")
        
        if activity.activity_type == "browser":
            print(f"      └─ {activity.details['domain']} ({activity.details['browser']})")
        elif activity.activity_type == "ai_chat":
            service = activity.details['ai_service'].title()
            topic = activity.details['topic']
            message_count = activity.details['message_count']
            print(f"      └─ {service} • {topic} • {message_count} messages")
        elif activity.activity_type == "git":
            repository = activity.details['repository']
            branch = activity.details['branch']
            git_type = activity.details['activity_type']
            if git_type == 'commit':
                lines_changed = activity.details['lines_changed']
                files_count = len(activity.details['files_changed'])
                print(f"      └─ {repository} • {branch} • {files_count} files • ±{lines_changed} lines")
            else:
                print(f"      └─ {repository} • {branch} • {git_type}")
    
    # Test report generation
    print("\n📋 Testing report generation...")
    report_generator = DailyReportGenerator(settings)
    
    # Generate summary stats
    summary = report_generator.generate_summary_stats(all_activities)
    print(f"   📊 Summary Stats:")
    print(f"      • Total: {summary['total']} activities")
    print(f"      • Productivity: {summary['productivity']}%")
    print(f"      • Time span: {summary['timespan']}")
    print(f"      • Peak hour: {summary['most_active_hour']}")
    
    # Generate full report
    target_date = datetime.now().date()
    report_path = report_generator.generate_report(all_activities, target_date)
    print(f"   ✅ Full report saved to: {report_path}")
    
    print("\n✨ Test completed successfully!")
    print("\n💡 To test with real browser data:")
    print("   1. Close all browsers (Chrome, Edge, Firefox)")
    print("   2. Run: python main.py --scan-today")


if __name__ == "__main__":
    main()
