"""
Daily Report Generator for DayLog
Creates beautiful markdown reports from collected activity data
"""

import os
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter

from processors.aggregator import ActivityEntry


class DailyReportGenerator:
    """Generates comprehensive daily activity reports"""
    
    def __init__(self, settings):
        """Initialize report generator with settings"""
        self.settings = settings
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_report(self, activities: List[ActivityEntry], target_date: date) -> str:
        """Generate a comprehensive daily report"""
        if not activities:
            return self._generate_empty_report(target_date)
        
        # Analyze the data
        stats = self._analyze_activities(activities)
        timeline = self._create_timeline(activities)
        categories = self._group_by_category(activities)
        insights = self._generate_insights(activities, stats)
        
        # Generate the report
        report_content = self._build_report(
            target_date=target_date,
            stats=stats,
            timeline=timeline,
            categories=categories,
            insights=insights,
            activities=activities
        )
        
        # Save the report
        report_path = self._save_report(report_content, target_date)
        
        return report_path
    
    def _analyze_activities(self, activities: List[ActivityEntry]) -> Dict[str, Any]:
        """Analyze activities and generate statistics"""
        stats = {
            'total_activities': len(activities),
            'time_span': {
                'start': min(activities, key=lambda x: x.timestamp).timestamp.timestamp(),
                'end': max(activities, key=lambda x: x.timestamp).timestamp.timestamp()
            },
            'categories': Counter(activity.category for activity in activities),
            'activity_types': Counter(activity.activity_type for activity in activities),
            'hourly_distribution': Counter(activity.timestamp.hour for activity in activities),
            'most_active_hour': None,
            'productivity_score': 0
        }
        
        # Find most active hour
        if stats['hourly_distribution']:
            stats['most_active_hour'] = stats['hourly_distribution'].most_common(1)[0][0]
        
        # Calculate simple productivity score (work + learning activities)
        productive_activities = sum(
            count for category, count in stats['categories'].items() 
            if category in ['work', 'learning']
        )
        stats['productivity_score'] = round(
            (productive_activities / stats['total_activities']) * 100, 1
        ) if stats['total_activities'] > 0 else 0
        
        return stats
    
    def _create_timeline(self, activities: List[ActivityEntry]) -> List[Dict]:
        """Create a chronological timeline of activities"""
        timeline = []
        
        # Group activities by hour for cleaner timeline
        hourly_groups = defaultdict(list)
        
        for activity in sorted(activities, key=lambda x: x.timestamp):
            hour_key = activity.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_groups[hour_key].append(activity)
        
        for hour, hour_activities in sorted(hourly_groups.items()):
            timeline.append({
                'time': hour,
                'activities': hour_activities,
                'summary': self._summarize_hour_activities(hour_activities)
            })
        
        return timeline
    
    def _summarize_hour_activities(self, activities: List[ActivityEntry]) -> str:
        """Create a summary for activities in a specific hour"""
        if not activities:
            return ""
        
        # Group by category
        categories = defaultdict(list)
        for activity in activities:
            categories[activity.category].append(activity)
        
        summaries = []
        for category, cat_activities in categories.items():
            if category == 'work':
                summaries.append(f"💼 {len(cat_activities)} work activities")
            elif category == 'learning':
                summaries.append(f"📚 {len(cat_activities)} learning activities")
            elif category == 'entertainment':  
                summaries.append(f"🎯 {len(cat_activities)} entertainment activities")
            else:
                summaries.append(f"🌐 {len(cat_activities)} general activities")
        
        return " • ".join(summaries)
    
    def _group_by_category(self, activities: List[ActivityEntry]) -> Dict[str, List[ActivityEntry]]:
        """Group activities by category"""
        categories = defaultdict(list)
        
        for activity in activities:
            categories[activity.category].append(activity)
        
        # Sort activities within each category by timestamp
        for category in categories:
            categories[category].sort(key=lambda x: x.timestamp, reverse=True)
        
        return dict(categories)
    
    def _generate_insights(self, activities: List[ActivityEntry], stats: Dict) -> List[str]:
        """Generate intelligent insights about the day"""
        insights = []
        
        # Activity volume insights
        total = stats['total_activities']
        if total > 50:
            insights.append(f"🔥 Very active day with {total} logged activities")
        elif total > 20:
            insights.append(f"📈 Productive day with {total} activities")
        elif total > 10:
            insights.append(f"📊 Moderate activity with {total} logged events")
        else:
            insights.append(f"🌱 Light day with {total} activities")
        
        # Productivity insights
        productivity = stats['productivity_score']
        if productivity >= 70:
            insights.append(f"🎯 High productivity focus ({productivity}% work/learning)")
        elif productivity >= 40:
            insights.append(f"⚖️ Balanced day ({productivity}% work/learning)")
        else:
            insights.append(f"🎨 Relaxed day ({productivity}% work/learning)")
        
        # Time span insights
        time_span = stats['time_span']['end'] - stats['time_span']['start']
        hours_active = time_span / 3600
        if hours_active > 12:
            insights.append(f"⏰ Long active period ({hours_active:.1f} hours)")
        elif hours_active > 8:
            insights.append(f"🕘 Full day of activity ({hours_active:.1f} hours)")
        else:
            insights.append(f"⚡ Focused session ({hours_active:.1f} hours)")
        
        # Category-specific insights
        categories = stats['categories']
        
        if 'ai_chat' in stats['activity_types'] and stats['activity_types']['ai_chat'] > 3:
            insights.append(f"🤖 Heavy AI assistance day ({stats['activity_types']['ai_chat']} conversations)")
        
        if categories.get('learning', 0) > categories.get('work', 0):
            insights.append("📚 Learning-focused day")
        
        if categories.get('work', 0) > 10:
            insights.append("💼 Work-intensive day")
        
        # Peak activity time
        if stats['most_active_hour'] is not None:
            hour = stats['most_active_hour']
            if hour < 12:
                insights.append(f"🌅 Morning person - peak activity at {hour}:00")
            elif hour < 17:
                insights.append(f"☀️ Afternoon focus - peak activity at {hour}:00")
            else:
                insights.append(f"🌙 Evening active - peak activity at {hour}:00")
        
        return insights
    
    def _build_report(self, target_date: date, stats: Dict, timeline: List, 
                     categories: Dict, insights: List, activities: List[ActivityEntry]) -> str:
        """Build the complete markdown report"""
        
        date_str = target_date.strftime("%B %d, %Y")
        weekday = target_date.strftime("%A")
        
        report = f"""# 📅 Daily Activity Report - {date_str}
*{weekday}*

---

## 🎯 Daily Overview

"""
        
        # Add insights
        if insights:
            report += "### 💡 Key Insights\n\n"
            for insight in insights:
                report += f"- {insight}\n"
            report += "\n"
        
        # Add statistics
        report += f"""### 📊 Activity Statistics

| Metric | Value |
|--------|-------|
| **Total Activities** | {stats['total_activities']} |
| **Productivity Score** | {stats['productivity_score']}% |
| **Most Active Hour** | {stats['most_active_hour']}:00 |
| **Time Span** | {datetime.fromtimestamp(stats['time_span']['start']).strftime('%H:%M')} - {datetime.fromtimestamp(stats['time_span']['end']).strftime('%H:%M')} |

"""
        
        # Add category breakdown
        if categories:
            report += "### 📈 Activity Breakdown\n\n"
            category_emojis = {
                'work': '💼',
                'learning': '📚', 
                'entertainment': '🎯',
                'general': '🌐'
            }
            
            for category, count in stats['categories'].most_common():
                emoji = category_emojis.get(category, '❓')
                percentage = round((count / stats['total_activities']) * 100, 1)
                report += f"- {emoji} **{category.title()}**: {count} activities ({percentage}%)\n"
            
            report += "\n"
        
        # Add timeline if enabled
        if self.settings.get('output.include_timeline', True) and timeline:
            report += "## ⏰ Timeline\n\n"
            
            for hour_data in timeline:
                time_str = hour_data['time'].strftime('%H:%M')
                summary = hour_data['summary']
                report += f"**{time_str}** - {summary}\n\n"
                
                # Show detailed activities for this hour
                max_per_hour = 3  # Limit to avoid clutter
                for i, activity in enumerate(hour_data['activities'][:max_per_hour]):
                    activity_time = activity.timestamp.strftime('%H:%M')
                    activity_emoji = '🤖' if activity.activity_type == 'ai_chat' else '🌐'
                    report += f"  {activity_emoji} `{activity_time}` {activity.title[:80]}...\n"
                
                if len(hour_data['activities']) > max_per_hour:
                    remaining = len(hour_data['activities']) - max_per_hour
                    report += f"  *... and {remaining} more activities*\n"
                
                report += "\n"
        
        # Add detailed categories
        max_entries = self.settings.get('output.max_entries_per_category', 10)
        
        for category, activities_list in categories.items():
            if not activities_list:
                continue
                
            category_emoji = {
                'work': '💼',
                'learning': '📚',
                'entertainment': '🎯', 
                'general': '🌐'
            }.get(category, '❓')
            
            report += f"## {category_emoji} {category.title()} Activities\n\n"
            
            for i, activity in enumerate(activities_list[:max_entries]):
                time_str = activity.timestamp.strftime('%H:%M')
                type_emoji = '🤖' if activity.activity_type == 'ai_chat' else '🌐'
                
                report += f"### {type_emoji} {activity.title}\n"
                report += f"*{time_str}*\n\n"
                
                # Add specific details based on activity type
                if activity.activity_type == 'browser':
                    domain = activity.details.get('domain', '')
                    browser = activity.details.get('browser', '')
                    report += f"- **Website**: {domain}\n"
                    report += f"- **Browser**: {browser.title()}\n"
                
                elif activity.activity_type == 'ai_chat':
                    ai_service = activity.details.get('ai_service', '').title()
                    topic = activity.details.get('topic', '')
                    message_count = activity.details.get('message_count', 0)
                    user_message = activity.details.get('user_message', '')[:200]
                    
                    report += f"- **AI Service**: {ai_service}\n"
                    report += f"- **Topic**: {topic}\n" 
                    report += f"- **Messages**: {message_count}\n"
                    if user_message:
                        report += f"- **Context**: {user_message}...\n"
                
                elif activity.activity_type == 'git':
                    repository = activity.details.get('repository', '')
                    branch = activity.details.get('branch', '')
                    commit_hash = activity.details.get('commit_hash', '')
                    git_activity_type = activity.details.get('activity_type', '')
                    files_changed = activity.details.get('files_changed', [])
                    insertions = activity.details.get('insertions', 0)
                    deletions = activity.details.get('deletions', 0)
                    commit_message = activity.details.get('commit_message', '')[:300]
                    
                    report += f"- **Repository**: {repository}\n"
                    report += f"- **Branch**: {branch}\n"
                    
                    if git_activity_type == 'commit':
                        report += f"- **Commit**: `{commit_hash[:8]}...`\n" if commit_hash else ""
                        report += f"- **Files Changed**: {len(files_changed)}\n"
                        if insertions or deletions:
                            report += f"- **Changes**: +{insertions}/-{deletions} lines\n"
                        if commit_message:
                            report += f"- **Message**: {commit_message}...\n"
                    elif git_activity_type == 'branch_switch':
                        report += f"- **Action**: Branch switch\n"
                
                report += "\n"
            
            if len(activities_list) > max_entries:
                remaining = len(activities_list) - max_entries
                report += f"*... and {remaining} more {category} activities*\n\n"
        
        # Add footer
        report += f"""---

*Report generated by DayLog on {datetime.now().strftime('%Y-%m-%d at %H:%M')}*  
*Total processing time: < 1 second*

🚀 **Next Steps**: Review your patterns and plan tomorrow's focus areas!
"""
        
        return report
    
    def _generate_empty_report(self, target_date: date) -> str:
        """Generate report when no activities were found"""
        date_str = target_date.strftime("%B %d, %Y")
        weekday = target_date.strftime("%A")
        
        return f"""# 📅 Daily Activity Report - {date_str}
*{weekday}*

---

## 🤔 No Activities Found

No activities were recorded for this date. This could mean:

- 📴 Browsers were closed during data collection
- 🔒 Database files were locked
- 📅 No activity occurred on this date
- ⚙️ Data sources need configuration

### 💡 Troubleshooting Tips

1. **Close all browsers** before running DayLog
2. **Check your ChatGPT export** file path in settings
3. **Verify the date** - try `--date {target_date.strftime('%Y-%m-%d')}`
4. **Test with sample data**: `python test_daylog.py`

---

*Report generated by DayLog on {datetime.now().strftime('%Y-%m-%d at %H:%M')}*
"""
    
    def _save_report(self, content: str, target_date: date) -> str:
        """Save the report to a file"""
        filename = f"DayLog_{target_date.strftime('%Y-%m-%d')}.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def generate_summary_stats(self, activities: List[ActivityEntry]) -> Dict[str, Any]:
        """Generate quick summary statistics for console output"""
        if not activities:
            return {'total': 0, 'categories': {}, 'timespan': '0 hours'}
        
        stats = self._analyze_activities(activities)
        
        return {
            'total': stats['total_activities'],
            'categories': dict(stats['categories']),
            'productivity': stats['productivity_score'],
            'timespan': f"{(stats['time_span']['end'] - stats['time_span']['start']) / 3600:.1f} hours",
            'most_active_hour': f"{stats['most_active_hour']}:00" if stats['most_active_hour'] else "N/A"
        }
