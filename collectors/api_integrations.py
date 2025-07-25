"""
API Integration module for DayLog
Handles external API connections for real-time data collection
"""

import requests
import json
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class APICredentials:
    """Store API credentials securely"""
    service_name: str
    api_key: str
    base_url: str
    headers: Dict[str, str]


class APIIntegrationsCollector:
    """Collects data from external APIs"""
    
    def __init__(self, settings):
        """Initialize API collector with settings"""
        self.settings = settings
        self.credentials = self._load_api_credentials()
    
    def _load_api_credentials(self) -> Dict[str, APICredentials]:
        """Load API credentials from environment variables or config"""
        credentials = {}
        
        # OpenAI API for ChatGPT (if available in future)
        openai_key = os.getenv('OPENAI_API_KEY') or self.settings.get('ai_integration.openai_api_key', '')
        if openai_key:
            credentials['openai'] = APICredentials(
                service_name='openai',
                api_key=openai_key,
                base_url='https://api.openai.com/v1',
                headers={
                    'Authorization': f'Bearer {openai_key}',
                    'Content-Type': 'application/json'
                }
            )
        
        # GitHub API for repository activity
        github_token = os.getenv('GITHUB_TOKEN') or self.settings.get('integrations.github.token', '')
        if github_token:
            credentials['github'] = APICredentials(
                service_name='github',
                api_key=github_token,
                base_url='https://api.github.com',
                headers={
                    'Authorization': f'Bearer {github_token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
        
        # Google Calendar API (if configured)
        google_key = os.getenv('GOOGLE_API_KEY') or self.settings.get('integrations.google.api_key', '')
        if google_key:
            credentials['google'] = APICredentials(
                service_name='google',
                api_key=google_key,
                base_url='https://www.googleapis.com/calendar/v3',
                headers={
                    'Authorization': f'Bearer {google_key}',
                    'Content-Type': 'application/json'
                }
            )
        
        return credentials
    
    def collect_github_activity(self, target_date: date, username: str) -> List[Dict]:
        """Collect GitHub activity via API"""
        activities = []
        
        if 'github' not in self.credentials:
            print("   ⚠️  GitHub API token not configured")
            return activities
        
        try:
            github_creds = self.credentials['github']
            
            # Get events for the user
            events_url = f"{github_creds.base_url}/users/{username}/events"
            response = requests.get(events_url, headers=github_creds.headers, timeout=10)
            
            if response.status_code == 200:
                events = response.json()
                
                for event in events:
                    event_date = datetime.fromisoformat(
                        event['created_at'].replace('Z', '+00:00')
                    ).date()
                    
                    if event_date == target_date:
                        activities.append({
                            'timestamp': datetime.fromisoformat(event['created_at'].replace('Z', '+00:00')),
                            'type': event['type'],
                            'repo': event['repo']['name'],
                            'details': event['payload']
                        })
            else:
                print(f"   ❌ GitHub API error: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ GitHub API error: {str(e)}")
        
        return activities
    
    def collect_calendar_events(self, target_date: date) -> List[Dict]:
        """Collect calendar events via Google Calendar API"""
        events = []
        
        if 'google' not in self.credentials:
            print("   ⚠️  Google Calendar API not configured")
            return events
        
        try:
            google_creds = self.credentials['google']
            
            # Calculate time range for the day
            start_time = datetime.combine(target_date, datetime.min.time()).isoformat() + 'Z'
            end_time = datetime.combine(target_date + timedelta(days=1), datetime.min.time()).isoformat() + 'Z'
            
            # Get calendar events
            calendar_url = f"{google_creds.base_url}/calendars/primary/events"
            params = {
                'timeMin': start_time,
                'timeMax': end_time,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            response = requests.get(calendar_url, headers=google_creds.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                calendar_data = response.json()
                events = calendar_data.get('items', [])
            else:
                print(f"   ❌ Google Calendar API error: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Google Calendar API error: {str(e)}")
        
        return events
    
    def test_api_connections(self) -> Dict[str, bool]:
        """Test all configured API connections"""
        results = {}
        
        for service_name, creds in self.credentials.items():
            try:
                if service_name == 'github':
                    # Test GitHub API
                    response = requests.get(f"{creds.base_url}/user", headers=creds.headers, timeout=5)
                    results[service_name] = response.status_code == 200
                
                elif service_name == 'google':
                    # Test Google Calendar API
                    response = requests.get(f"{creds.base_url}/calendars", headers=creds.headers, timeout=5)
                    results[service_name] = response.status_code == 200
                
                elif service_name == 'openai':
                    # Test OpenAI API
                    response = requests.get(f"{creds.base_url}/models", headers=creds.headers, timeout=5)
                    results[service_name] = response.status_code == 200
                
                else:
                    results[service_name] = False
            
            except Exception as e:
                print(f"   ❌ {service_name} API test failed: {str(e)}")
                results[service_name] = False
        
        return results


class WebhookReceiver:
    """Receive real-time data via webhooks (for advanced setups)"""
    
    def __init__(self, settings):
        self.settings = settings
        self.webhook_port = settings.get('integrations.webhook.port', 8080)
    
    def start_webhook_server(self):
        """Start a simple webhook server for real-time data"""
        # This would be implemented with Flask or FastAPI for production
        print(f"🔗 Webhook server would start on port {self.webhook_port}")
        print("   📡 Ready to receive real-time data from:")
        print("      • GitHub webhooks")
        print("      • Slack webhooks") 
        print("      • Custom integrations")
    
    def handle_github_webhook(self, payload: Dict):
        """Handle incoming GitHub webhook data"""
        # Process GitHub webhook payload
        pass
    
    def handle_slack_webhook(self, payload: Dict):
        """Handle incoming Slack webhook data"""
        # Process Slack webhook payload
        pass


def create_api_integration_test():
    """Create a test script for API integrations"""
    print("🧪 API Integration Test")
    print("=" * 50)
    
    # This would test all configured APIs
    print("📊 Testing API connections...")
    print("   🐙 GitHub API: ⏳ (Token required)")
    print("   📅 Google Calendar: ⏳ (API key required)")
    print("   🤖 OpenAI API: ⏳ (API key required)")
    
    print("\n💡 To enable API integrations:")
    print("   1. Set environment variables:")
    print("      • GITHUB_TOKEN=your_github_token")
    print("      • GOOGLE_API_KEY=your_google_key")
    print("      • OPENAI_API_KEY=your_openai_key")
    print("   2. Or update config/settings.json with API keys")
    print("   3. Run: python main.py --test-apis")


if __name__ == "__main__":
    create_api_integration_test()
