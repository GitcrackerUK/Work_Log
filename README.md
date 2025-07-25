# DayLog - Personal Daily Activity Logger

A Python-based automated system that generates comprehensive daily activity logs by collecting and analyzing data from various sources including browser history, AI chat interactions, file activities, and system usage patterns.

## 🚀 Quick Start

```bash
# Clone and setup
cd DayLog
pip install -r requirements.txt

# Run your first activity scan
python main.py --scan-today

# Generate daily report
python main.py --generate-report
```

## 📁 Project Structure

```
DayLog/
├── collectors/          # Data collection modules
│   ├── __init__.py
│   ├── browser.py      # Browser history collection
│   ├── files.py        # File system monitoring
│   ├── git.py          # Git activity tracking
│   └── ai_chats.py     # AI chat history parsing
├── processors/         # Data processing and analysis
│   ├── __init__.py
│   ├── aggregator.py   # Data combination and cleaning
│   ├── categorizer.py  # Activity categorization
│   └── summarizer.py   # AI-powered summarization
├── outputs/            # Generated reports and logs
├── config/             # Configuration files
│   └── settings.json
├── tests/              # Unit tests
├── requirements.txt    # Python dependencies
├── main.py            # Main application entry point
└── README.md          # This file
```

## 🔧 Features (Planned)

- [x] Project setup and architecture
- [ ] Browser history collection (Chrome, Edge, Firefox)
- [ ] File system activity monitoring
- [ ] Git repository activity tracking
- [ ] AI chat history parsing (ChatGPT, Copilot)
- [ ] Data aggregation and deduplication
- [ ] Activity categorization and analysis
- [ ] AI-powered daily summaries
- [ ] Automated report generation
- [ ] Privacy-focused local processing

## 📊 Data Sources

- **Browser Activity**: URLs, search queries, time spent
- **File System**: Recently accessed/modified files
- **Development**: Git commits, code compilation, IDE usage
- **AI Interactions**: ChatGPT, GitHub Copilot conversations
- **System**: Application usage, window focus tracking

## 🛡️ Privacy

All data processing happens locally on your machine. No data is sent to external services except for AI summarization (optional, with your API keys).

---

*Started: July 25, 2025*
