# DayLog - Personal Daily Activity Logger

## 📋 Project Overview

**Goal**: Create an automated system that generates a comprehensive daily log by collecting and analyzing various data sources from your computer usage, including browsing history, AI chat interactions, file activities, and system usage patterns.

**Vision**: At the end of each day, automatically generate a readable summary like:
```
📅 July 25, 2025 - Daily Activity Summary

🌐 Web Activity:
- Spent 2.5 hours on development-related sites (Stack Overflow, GitHub)
- 45 minutes on ChatGPT discussing C programming and project planning
- Researched ActivityWatch and time tracking solutions

💻 Development Work:
- Modified 5 files in PDF-converter2 project
- Compiled and tested C programs 3 times
- Committed changes to Git repository

🤖 AI Interactions:
- ChatGPT: Discussed DayLog project architecture
- GitHub Copilot: Code suggestions for file parsing
- Total AI assistance time: 1.2 hours

📁 File Activity:
- Most active folder: C:\Users\Pawel\Desktop\Projects\
- Created new project: DayLog
- Edited configuration files in Code::Blocks
```

## 🎯 Data Sources & Collection Methods

### 1. Browser Activity
**Sources:**
- Chrome History: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\History`
- Edge History: `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\History`
- Firefox History: `%APPDATA%\Mozilla\Firefox\Profiles\[profile]\places.sqlite`

**Data Points:**
- URLs visited with timestamps
- Page titles and visit duration
- Search queries performed

### 2. AI Chat Interactions
**ChatGPT:**
- Export data from OpenAI account settings
- Parse conversation JSON files
- Extract topics and time spent

**GitHub Copilot:**
- VS Code chat history from workspace settings
- Extension logs and usage statistics

**Grok/X:**
- Browser history analysis for x.com interactions
- Potential API integration if available

### 3. System & File Activity
**File System Monitoring:**
- Recently accessed files (last 24 hours)
- File modifications and creations
- Directory navigation patterns

**Application Usage:**
- Window focus tracking
- Application launch times and duration
- Process monitoring

### 4. Development Activity
**Version Control:**
- Git commit history with messages
- Repository activity across projects
- Branch switching and merging

**IDE/Editor Activity:**
- VS Code workspace history
- File editing patterns
- Extension usage

**Terminal/Command History:**
- PowerShell command history
- Compilation and execution logs
- Package installations and updates

### 5. System Logs
**Windows Event Logs:**
- Application launches and crashes
- System startup/shutdown times
- Network connectivity events

## 🛠️ Implementation Approaches

### Option 1: Ready-Made Foundation + Custom Extensions

**Primary Tool: ActivityWatch**
- ✅ Free and open-source
- ✅ Already tracks apps, windows, and browser activity
- ✅ REST API for custom data integration
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Extensible with custom watchers

**Implementation:**
1. Install ActivityWatch as base tracker
2. Create custom watchers for:
   - AI chat history parsing
   - Git activity monitoring
   - File system changes
3. Build aggregation layer to combine all data
4. Use AI (GPT API) to generate human-readable summaries

### Option 2: Custom-Built Solution

**Advantages:**
- ✅ Full control over data collection and privacy
- ✅ Tailored specifically to your needs
- ✅ Learning experience in system programming
- ✅ No external dependencies

**Challenges:**
- ❌ More development time required
- ❌ Need to handle cross-platform compatibility
- ❌ Requires deep system knowledge

## 💻 Language Comparison: Python vs C

### Python Approach
**Advantages:**
- ✅ **Rapid Development**: Faster prototyping and iteration
- ✅ **Rich Ecosystem**: Libraries for everything (sqlite3, psutil, win32gui, pandas)
- ✅ **Easy Database Access**: Simple SQLite integration for browser history
- ✅ **API Integration**: Easy REST API calls and JSON parsing
- ✅ **Data Processing**: Pandas for data analysis and manipulation
- ✅ **AI Integration**: OpenAI, Anthropic APIs readily available
- ✅ **Cross-Platform**: Works on Windows, Mac, Linux with minimal changes

**Best Libraries:**
```python
# Core system monitoring
import psutil          # Process and system monitoring
import sqlite3         # Browser history databases
import win32gui        # Windows-specific GUI interactions
import win32process    # Process monitoring on Windows

# Data processing
import pandas as pd    # Data analysis and manipulation
import json           # Configuration and data files
import datetime       # Time handling

# External integrations
import requests       # API calls
import openai         # GPT integration for summaries
```

**Disadvantages:**
- ❌ Slightly higher resource usage
- ❌ Requires Python runtime installation
- ❌ May need compilation for distribution

### C Approach
**Advantages:**
- ✅ **Performance**: Faster execution and lower resource usage
- ✅ **System Integration**: Direct Windows API access
- ✅ **Your Expertise**: You're comfortable with C
- ✅ **Standalone**: Compiles to executable without runtime dependencies
- ✅ **Learning**: Deeper understanding of system internals

**Required Libraries:**
```c
// Windows API
#include <windows.h>    // Core Windows functionality
#include <psapi.h>      // Process enumeration
#include <tlhelp32.h>   // Tool help for process snapshots

// SQLite integration
#include <sqlite3.h>    // Browser history databases

// JSON handling
#include <cjson/cJSON.h> // JSON parsing (third-party)

// HTTP requests
#include <winhttp.h>    // Windows HTTP API
```

**Disadvantages:**
- ❌ **Development Time**: Much longer to implement
- ❌ **Complexity**: Memory management, error handling
- ❌ **Library Ecosystem**: Limited compared to Python
- ❌ **JSON/API Handling**: More complex HTTP and JSON operations
- ❌ **Database Integration**: More complex SQLite C API

## 🏗️ Recommended Architecture

### Hybrid Approach (Recommended)
1. **Use ActivityWatch** as the foundation for basic tracking
2. **Python scripts** for data aggregation and processing
3. **Custom watchers** for specific data sources (Git, AI chats)
4. **AI-powered summarization** using GPT API
5. **C components** only where performance is critical

### Data Flow
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │ -> │   Collectors    │ -> │   Aggregator    │
│                 │    │                 │    │                 │
│ • Browser DB    │    │ • ActivityWatch │    │ • Data merger   │
│ • Git logs      │    │ • Custom Python │    │ • Time alignment│
│ • File system   │    │ • File watcher  │    │ • Deduplication │
│ • AI chat logs  │    │ • Git parser    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       v
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Daily Report  │ <- │   AI Summary    │ <- │   Processor     │
│                 │    │                 │    │                 │
│ • Markdown file │    │ • GPT API call  │    │ • Categorization│
│ • JSON export   │    │ • Natural lang. │    │ • Statistics    │
│ • Web dashboard │    │ • Templating    │    │ • Pattern detect│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Implementation Steps

### Phase 1: Foundation (Week 1-2)
1. **Setup Project Structure**
   ```
   DayLog/
   ├── collectors/          # Data collection modules
   ├── processors/          # Data processing and analysis
   ├── outputs/            # Generated reports and logs
   ├── config/             # Configuration files
   ├── tests/              # Unit tests
   └── docs/               # Documentation
   ```

2. **Install ActivityWatch**
   - Download and setup ActivityWatch
   - Understand data structure and API
   - Test basic data collection

3. **Browser History Reader**
   - Python script to read Chrome/Edge SQLite databases
   - Parse URLs, timestamps, and titles
   - Handle locked database files

### Phase 2: Core Data Collection (Week 3-4)
4. **File System Monitor**
   - Track recently modified files
   - Monitor directory access patterns
   - Log file creation/deletion events

5. **Git Activity Tracker**
   - Parse git log for commits
   - Track repository activity
   - Monitor branch changes

6. **AI Chat History Parser**
   - ChatGPT export file processor
   - VS Code Copilot chat extraction
   - Timestamp alignment with other activities

### Phase 3: Data Processing (Week 5-6)
7. **Data Aggregation Engine**
   - Combine data from all sources
   - Resolve timestamp conflicts
   - Remove duplicates and noise

8. **Categorization System**
   - Classify activities (work, learning, entertainment)
   - Identify productivity patterns
   - Calculate time spent per category

### Phase 4: Intelligence Layer (Week 7-8)
9. **AI-Powered Summarization**
   - Integration with GPT API
   - Template-based report generation
   - Natural language activity descriptions

10. **Pattern Recognition**
    - Daily/weekly pattern analysis
    - Productivity trend identification
    - Anomaly detection

### Phase 5: User Interface (Week 9-10)
11. **Report Generation**
    - Markdown daily reports
    - JSON data export
    - Optional web dashboard

12. **Automation & Scheduling**
    - Windows Task Scheduler integration
    - Automated daily report generation
    - Email/notification system

## 🔒 Privacy & Security Considerations

### Data Sensitivity
- **High**: Browser history, chat conversations, file contents
- **Medium**: Application usage, file names, git commits
- **Low**: System events, process names

### Security Measures
1. **Local Processing**: Keep all data on local machine
2. **Encryption**: Encrypt stored activity logs
3. **Selective Collection**: Option to exclude sensitive data
4. **Data Retention**: Automatic cleanup of old logs
5. **API Key Security**: Secure storage of AI service keys

## 🎯 Success Metrics

### Technical Goals
- [ ] Collect data from at least 5 different sources
- [ ] Generate daily reports automatically
- [ ] Process data in under 30 seconds
- [ ] 95% accuracy in activity categorization

### User Experience Goals
- [ ] Setup takes less than 15 minutes
- [ ] Reports are generated without user intervention
- [ ] Insights are actionable and meaningful
- [ ] Privacy is maintained throughout

## 🚀 Getting Started

### Immediate Next Steps
1. **Choose your approach**: 
   - **Recommended**: Python + ActivityWatch hybrid
   - **Alternative**: Pure Python custom solution
   - **Advanced**: C implementation for learning

2. **Set up development environment**
3. **Start with browser history parsing** (simplest data source)
4. **Build iteratively**, adding one data source at a time

### Decision Point: Python vs C

**Choose Python if:**
- You want to see results quickly
- You plan to integrate with web APIs
- You want rich data processing capabilities
- You prefer rapid prototyping

**Choose C if:**
- You want to deepen your C knowledge
- Performance is critical
- You prefer minimal dependencies
- You enjoy low-level system programming

**Recommendation**: Start with Python for rapid prototyping, then rewrite performance-critical components in C if needed.

---

*Last Updated: July 25, 2025*
*Next Review: After language decision and initial implementation*
