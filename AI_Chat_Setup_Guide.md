# AI Chat Integration Setup Guide

## 🤖 ChatGPT Integration

### Method 1: Export from OpenAI Account (Recommended)

1. **Go to ChatGPT Settings**:
   - Visit [chat.openai.com](https://chat.openai.com)
   - Click your profile → Settings & Beta
   - Go to "Data controls"

2. **Export Your Data**:
   - Click "Export data"
   - Wait for email with download link
   - Download the ZIP file

3. **Configure DayLog**:
   ```json
   {
     "data_sources": {
       "ai_chats": {
         "enabled": true,
         "chatgpt_export_path": "C:\\Users\\Pawel\\Downloads\\ChatGPT_conversations.json",
         "copilot_enabled": true
       }
     }
   }
   ```

### Method 2: Manual JSON File

Create a JSON file with your conversations:

```json
[
  {
    "create_time": 1690300800,
    "title": "Python Development Help",
    "mapping": {
      "msg_1": {
        "message": {
          "author": {"role": "user"},
          "content": {"parts": ["Help me create a Python application"]}
        }
      },
      "msg_2": {
        "message": {
          "author": {"role": "assistant"},
          "content": {"parts": ["I'd be happy to help you create a Python application..."]}
        }
      }
    }
  }
]
```

## 🐙 GitHub Copilot Integration

### Current Status
- **Automatic Detection**: DayLog attempts to find Copilot chat from VS Code logs
- **Limited Access**: VS Code doesn't expose full Copilot chat history via API
- **Log-based**: Currently detects activity patterns from log files

### Manual Enhancement
You can manually log important Copilot interactions:

1. **Create a Copilot log file**: `copilot_chats.json`
2. **Add important conversations**:
   ```json
   [
     {
       "timestamp": "2025-07-25T14:30:00Z",
       "user_message": "How do I handle SQLite database locking?",
       "ai_response": "Here are several approaches to handle SQLite locking...",
       "topic": "Database Programming"
     }
   ]
   ```

3. **Update settings**:
   ```json
   {
     "data_sources": {
       "ai_chats": {
         "copilot_manual_log": "C:\\Users\\Pawel\\Desktop\\Projects\\DayLog\\copilot_chats.json"
       }
     }
   }
   ```

## 🔧 Other AI Services

### Adding Grok/X AI
Update your browser history settings to include X.com conversations:
```json
{
  "processing": {
    "categorization": {
      "work_keywords": ["github", "stackoverflow", "docs", "api", "grok", "x.com"]
    }
  }
}
```

### Adding Claude/Anthropic
Similar to ChatGPT, but check if Anthropic offers data export options.

## 🔍 Testing Your Setup

1. **Run the test script**:
   ```bash
   python test_daylog.py
   ```

2. **Check with real data**:
   ```bash
   python main.py --scan-today
   ```

3. **Verify in output**:
   Look for "🤖 ChatGPT: X conversations" in the output.

## 📊 Expected Output

When working correctly, you should see:
```
📊 Collecting activity data...
   📱 Chrome: 15 entries
   📱 Edge: 8 entries  
   📱 Firefox: 0 entries
   🤖 ChatGPT: 3 conversations
   🐙 Copilot: 2 conversations
   ✅ Browser history: 23 entries
   ✅ AI conversations: 5 entries
📝 Total activities collected: 28
```

## 🛠️ Troubleshooting

### No ChatGPT conversations found
- Check the export file path in settings.json
- Ensure the JSON file is valid
- Verify the date range matches your target date

### Copilot detection issues
- VS Code logs are complex and location varies
- Consider manual logging for important conversations
- Check VS Code version compatibility

### Performance issues
- Large ChatGPT exports can be slow to process
- Consider filtering by date range
- Use the `max_entries_per_category` setting to limit output

---

*Next: Once AI chats are working, we can add Git activity tracking and file monitoring!* 🚀
