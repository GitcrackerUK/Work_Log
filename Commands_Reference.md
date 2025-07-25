# DayLog Commands Reference

## 🚀 Quick Start Commands

### **Generate Full Daily Report** (Recommended)
```bash
python main.py --full-report
```
*Scans data AND generates a beautiful markdown report in one command*

### **Test with Sample Data**
```bash
python test_daylog.py
```
*Creates sample activities and generates a test report*

### **Scan Today's Activities Only**
```bash
python main.py --scan-today
```
*Collects data and shows console summary (no report file)*

### **Generate Report Only** (from previously scanned data)
```bash
python main.py --generate-report
```
*Creates report file from existing data collection*

### **Process Specific Date**
```bash
python main.py --full-report --date 2025-07-24
```
*Generate report for any specific date (YYYY-MM-DD format)*

## 📋 Report Features

### **What the Report Includes:**
- ✅ **Daily Overview** with key insights
- ✅ **Activity Statistics** (productivity score, time span, totals)  
- ✅ **Category Breakdown** (work, learning, entertainment, general)
- ✅ **Hourly Timeline** showing when you were most active
- ✅ **Detailed Activity Lists** with timestamps and context
- ✅ **Smart Insights** about your productivity patterns

### **Sample Report Structure:**
```
📅 Daily Activity Report - July 25, 2025

🎯 Daily Overview
💡 Key Insights:
  • High productivity focus (87.5% work/learning)
  • Peak activity at 20:00
  • Focused session (2.7 hours)

📊 Activity Statistics
📈 Activity Breakdown
⏰ Timeline
💼 Work Activities  
📚 Learning Activities
🎯 Entertainment Activities
```

## 📁 Output Files

Reports are saved to: `outputs/DayLog_YYYY-MM-DD.md`

Examples:
- `outputs/DayLog_2025-07-25.md`
- `outputs/DayLog_2025-07-24.md`

## 🎯 Productivity Insights

The report automatically calculates:

- **Productivity Score**: % of time spent on work/learning vs entertainment
- **Peak Hours**: When you're most active
- **Activity Patterns**: Categories and types of activities
- **Time Efficiency**: Total active time span

## 💡 Tips for Best Results

### **For Real Browser Data:**
1. Close all browsers (Chrome, Edge, Firefox)
2. Run `python main.py --full-report`
3. Browsers will be locked while running, so data collection works

### **For ChatGPT Integration:**
1. Export your ChatGPT conversations from OpenAI
2. Update `config/settings.json` with the file path:
   ```json
   "chatgpt_export_path": "C:\\Users\\Pawel\\Downloads\\conversations.json"
   ```

### **For Testing:**
- Use `python test_daylog.py` to see how reports look with sample data
- Reports work perfectly even with zero real data

## 🚀 What's Next?

Your DayLog now has:
- ✅ Browser history collection
- ✅ AI chat integration  
- ✅ Smart categorization
- ✅ Beautiful report generation

**Ready to add:**
- 📁 File activity monitoring
- ⚙️ Git repository tracking
- 📊 Advanced analytics dashboard

---

*Happy logging! 📈*
