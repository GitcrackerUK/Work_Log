"""
Configuration management for DayLog
"""

import json
import os
from pathlib import Path
from typing import Dict, Any


class Settings:
    """Configuration settings manager"""
    
    DEFAULT_CONFIG = {
        "data_sources": {
            "browser": {
                "enabled": True,
                "chrome_path": "%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\History",
                "edge_path": "%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Default\\History",
                "firefox_path": "%APPDATA%\\Mozilla\\Firefox\\Profiles"
            },
            "files": {
                "enabled": True,
                "watch_directories": [
                    "%USERPROFILE%\\Desktop",
                    "%USERPROFILE%\\Documents",
                    "%USERPROFILE%\\Downloads"
                ],
                "exclude_extensions": [".tmp", ".log", ".cache"]
            },
            "git": {
                "enabled": True,
                "project_directories": [
                    "%USERPROFILE%\\Desktop\\Projects"
                ]
            },
            "ai_chats": {
                "enabled": True,
                "chatgpt_export_path": "",
                "copilot_enabled": True
            }
        },
        "processing": {
            "categorization": {
                "work_keywords": ["github", "stackoverflow", "docs", "api"],
                "learning_keywords": ["tutorial", "course", "learn", "guide"],
                "entertainment_keywords": ["youtube", "netflix", "game", "social"]
            },
            "privacy": {
                "exclude_urls": ["private", "password", "banking"],
                "exclude_file_patterns": ["*password*", "*secret*", "*key*"]
            }
        },
        "output": {
            "format": "markdown",
            "include_statistics": True,
            "include_timeline": True,
            "max_entries_per_category": 10
        },
        "ai_integration": {
            "enabled": False,
            "openai_api_key": "",
            "summarization_enabled": False
        },
        "integrations": {
            "github": {
                "enabled": False,
                "token": "",
                "username": "GitcrackerUK",
                "repositories": ["Work_Log", "DayLog"]
            },
            "google_calendar": {
                "enabled": False,
                "api_key": "",
                "calendar_id": "primary"
            },
            "slack": {
                "enabled": False,
                "token": "",
                "channels": ["general", "development"]
            },
            "webhook": {
                "enabled": False,
                "port": 8080,
                "secret": ""
            }
        }
    }
    
    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize settings from file or create default"""
        self.config_path = Path(config_path)
        self.settings = self._load_or_create_config()
    
    def _load_or_create_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_with_defaults(config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")
                print("Using default configuration...")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self._save_config(self.DEFAULT_CONFIG)
            print(f"Created default configuration at {self.config_path}")
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_with_defaults(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults to ensure all keys exist"""
        def deep_merge(default: dict, user: dict) -> dict:
            result = default.copy()
            for key, value in user.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(self.DEFAULT_CONFIG, user_config)
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'data_sources.browser.enabled')"""
        keys = key_path.split('.')
        value = self.settings
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.settings
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save updated configuration
        self._save_config(self.settings)
    
    def expand_path(self, path: str) -> str:
        """Expand environment variables in path"""
        return os.path.expandvars(path)
    
    def is_enabled(self, source: str) -> bool:
        """Check if a data source is enabled"""
        return self.get(f'data_sources.{source}.enabled', False)
