"""
AI Chat History data collection module
Supports ChatGPT exports, GitHub Copilot chat, and other AI assistants
"""

import json
import os
import re
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class AIChatActivity:
    """Represents a single AI chat interaction"""
    timestamp: datetime
    ai_service: str  # 'chatgpt', 'copilot', 'grok', etc.
    conversation_id: str
    user_message: str
    ai_response: str
    topic: str
    message_count: int


class AIChatCollector:
    """Collects AI chat history from various sources"""
    
    def __init__(self, settings):
        """Initialize AI chat collector with settings"""
        self.settings = settings
        self.chatgpt_export_path = self.settings.expand_path(
            self.settings.get('data_sources.ai_chats.chatgpt_export_path', '')
        )
        self.copilot_enabled = self.settings.get('data_sources.ai_chats.copilot_enabled', True)
    
    def collect(self, target_date: date) -> List[AIChatActivity]:
        """Collect AI chat history for the specified date"""
        if not self.settings.is_enabled('ai_chats'):
            return []
        
        all_activities = []
        
        # Collect ChatGPT conversations
        try:
            chatgpt_activities = self._collect_chatgpt_history(target_date)
            all_activities.extend(chatgpt_activities)
            print(f"   🤖 ChatGPT: {len(chatgpt_activities)} conversations")
        except Exception as e:
            print(f"   ❌ ChatGPT: Error - {str(e)}")
        
        # Collect GitHub Copilot chat
        if self.copilot_enabled:
            try:
                copilot_activities = self._collect_copilot_history(target_date)
                all_activities.extend(copilot_activities)
                print(f"   🐙 Copilot: {len(copilot_activities)} conversations")
            except Exception as e:
                print(f"   ❌ Copilot: Error - {str(e)}")
        
        # TODO: Add other AI services (Grok, Claude, etc.)
        
        return sorted(all_activities, key=lambda x: x.timestamp)
    
    def _collect_chatgpt_history(self, target_date: date) -> List[AIChatActivity]:
        """Collect ChatGPT conversation history from export files"""
        activities = []
        
        if not self.chatgpt_export_path or not Path(self.chatgpt_export_path).exists():
            return activities
        
        export_path = Path(self.chatgpt_export_path)
        
        # Handle different export formats
        if export_path.is_file() and export_path.suffix == '.json':
            # Single JSON export file
            activities.extend(self._parse_chatgpt_json(export_path, target_date))
        elif export_path.is_dir():
            # Directory with multiple conversation files
            for json_file in export_path.glob('*.json'):
                activities.extend(self._parse_chatgpt_json(json_file, target_date))
        
        return activities
    
    def _parse_chatgpt_json(self, json_file: Path, target_date: date) -> List[AIChatActivity]:
        """Parse ChatGPT JSON export file"""
        activities = []
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different ChatGPT export formats
            conversations = []
            if isinstance(data, list):
                conversations = data
            elif isinstance(data, dict):
                if 'conversations' in data:
                    conversations = data['conversations']
                elif 'data' in data:
                    conversations = data['data']
                else:
                    conversations = [data]  # Single conversation
            
            for conv in conversations:
                try:
                    activity = self._parse_chatgpt_conversation(conv, target_date)
                    if activity:
                        activities.append(activity)
                except Exception as e:
                    print(f"      ⚠️  Error parsing conversation: {str(e)}")
        
        except Exception as e:
            print(f"      ❌ Error reading {json_file}: {str(e)}")
        
        return activities
    
    def _parse_chatgpt_conversation(self, conversation: Dict, target_date: date) -> Optional[AIChatActivity]:
        """Parse a single ChatGPT conversation"""
        try:
            # Extract timestamp (various formats in ChatGPT exports)
            timestamp = None
            for time_field in ['create_time', 'timestamp', 'created_at', 'update_time']:
                if time_field in conversation:
                    time_value = conversation[time_field]
                    if isinstance(time_value, (int, float)):
                        timestamp = datetime.fromtimestamp(time_value)
                    elif isinstance(time_value, str):
                        # Try different timestamp formats
                        for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                            try:
                                timestamp = datetime.strptime(time_value, fmt)
                                break
                            except ValueError:
                                continue
                    break
            
            if not timestamp or timestamp.date() != target_date:
                return None
            
            # Extract messages
            messages = conversation.get('mapping', {})
            if not messages and 'messages' in conversation:
                messages = conversation['messages']
            
            user_messages = []
            ai_messages = []
            
            if isinstance(messages, dict):
                # ChatGPT export format with mapping
                for msg_id, msg_data in messages.items():
                    if 'message' not in msg_data:
                        continue
                    
                    message = msg_data['message']
                    author = message.get('author', {}).get('role', '')
                    content = message.get('content', {})
                    
                    if isinstance(content, dict) and 'parts' in content:
                        text = ' '.join(content['parts'])
                    elif isinstance(content, str):
                        text = content
                    else:
                        continue
                    
                    if author == 'user':
                        user_messages.append(text)
                    elif author == 'assistant':
                        ai_messages.append(text)
            
            elif isinstance(messages, list):
                # Simple message list format
                for message in messages:
                    role = message.get('role', '')
                    content = message.get('content', '')
                    
                    if role == 'user':
                        user_messages.append(content)
                    elif role == 'assistant':
                        ai_messages.append(content)
            
            if not user_messages:
                return None
            
            # Generate topic from first user message
            topic = self._extract_topic(user_messages[0])
            
            # Combine messages
            user_text = ' | '.join(user_messages[:3])  # First 3 user messages
            ai_text = ' | '.join(ai_messages[:3])      # First 3 AI responses
            
            conversation_id = conversation.get('id', conversation.get('conversation_id', str(timestamp.timestamp())))
            
            return AIChatActivity(
                timestamp=timestamp,
                ai_service='chatgpt',
                conversation_id=conversation_id,
                user_message=user_text[:500],  # Limit length
                ai_response=ai_text[:500],
                topic=topic,
                message_count=len(user_messages) + len(ai_messages)
            )
        
        except Exception as e:
            print(f"      ⚠️  Error parsing conversation: {str(e)}")
            return None
    
    def _collect_copilot_history(self, target_date: date) -> List[AIChatActivity]:
        """Collect GitHub Copilot chat history from VS Code"""
        activities = []
        
        # VS Code stores Copilot chat in various locations
        possible_paths = [
            Path.home() / '.vscode' / 'logs',
            Path.home() / 'AppData' / 'Roaming' / 'Code' / 'logs',
            Path.home() / 'AppData' / 'Roaming' / 'Code' / 'User' / 'workspaceStorage'
        ]
        
        for base_path in possible_paths:
            if not base_path.exists():
                continue
            
            # Look for recent log files
            for log_file in base_path.rglob('*.log'):
                if self._is_file_from_date(log_file, target_date):
                    activities.extend(self._parse_copilot_logs(log_file, target_date))
        
        # Also check current workspace for Copilot chat
        workspace_copilot = self._collect_workspace_copilot_chat(target_date)
        activities.extend(workspace_copilot)
        
        return activities
    
    def _parse_copilot_logs(self, log_file: Path, target_date: date) -> List[AIChatActivity]:
        """Parse Copilot log files for chat interactions"""
        activities = []
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Look for chat-like patterns in logs
            # This is a simplified parser - Copilot logs can be complex
            chat_patterns = [
                r'chat.*user.*?:\s*(.+)',
                r'copilot.*response.*?:\s*(.+)',
                r'conversation.*?:\s*(.+)'
            ]
            
            timestamp = datetime.combine(target_date, datetime.min.time())
            
            for pattern in chat_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # Create a simplified activity entry
                    user_text = ' | '.join(matches[:3])
                    topic = self._extract_topic(user_text)
                    
                    activity = AIChatActivity(
                        timestamp=timestamp,
                        ai_service='copilot',
                        conversation_id=f"log_{log_file.stem}",
                        user_message=user_text[:500],
                        ai_response="[Log-based detection]",
                        topic=topic,
                        message_count=len(matches)
                    )
                    activities.append(activity)
                    break
        
        except Exception as e:
            print(f"      ⚠️  Error parsing Copilot log {log_file}: {str(e)}")
        
        return activities
    
    def _collect_workspace_copilot_chat(self, target_date: date) -> List[AIChatActivity]:
        """Collect Copilot chat from current workspace (simplified)"""
        activities = []
        
        # This is a placeholder for workspace-specific Copilot chat
        # In practice, this would need to access VS Code's internal storage
        # For now, we'll create a simple detection based on recent activity
        
        return activities
    
    def _is_file_from_date(self, file_path: Path, target_date: date) -> bool:
        """Check if file was modified on target date"""
        try:
            file_date = datetime.fromtimestamp(file_path.stat().st_mtime).date()
            return file_date == target_date
        except:
            return False
    
    def _extract_topic(self, text: str) -> str:
        """Extract topic/theme from user message"""
        if not text:
            return "General"
        
        # Simple keyword-based topic extraction
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['python', 'code', 'programming', 'debug', 'function']):
            return "Programming"
        elif any(word in text_lower for word in ['explain', 'what is', 'how to', 'tutorial']):
            return "Learning"
        elif any(word in text_lower for word in ['write', 'create', 'generate', 'make']):
            return "Creation"
        elif any(word in text_lower for word in ['fix', 'error', 'problem', 'issue']):
            return "Problem Solving"
        elif any(word in text_lower for word in ['project', 'plan', 'strategy', 'approach']):
            return "Planning"
        else:
            # Use first few words as topic
            words = text.split()[:4]
            return ' '.join(words).title() if words else "General"
