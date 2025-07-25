#!/usr/bin/env python3
"""
DayLog - Personal Daily Activity Logger
Main application entry point
"""

import argparse
import sys
from datetime import datetime, date
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from collectors.browser import BrowserCollector
from collectors.ai_chats import AIChatCollector
from collectors.git import GitCollector
from processors.aggregator import DataAggregator
from processors.report_generator import DailyReportGenerator
from config.settings import Settings


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='DayLog - Personal Daily Activity Logger')
    parser.add_argument('--scan-today', action='store_true', 
                       help='Scan and collect today\'s activity data')
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate daily activity report')
    parser.add_argument('--full-report', action='store_true',
                       help='Scan data and generate report (combines --scan-today and --generate-report)')
    parser.add_argument('--date', type=str, 
                       help='Specific date to process (YYYY-MM-DD)')
    parser.add_argument('--config', type=str, default='config/settings.json',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Load configuration
    settings = Settings(args.config)
    
    # Determine target date
    target_date = date.today()
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD")
            sys.exit(1)
    
    print(f"🚀 DayLog - Processing data for {target_date}")
    
    # Handle combined full report option
    if args.full_report:
        args.scan_today = True
        args.generate_report = True
    
    # Initialize data collection variables
    all_data = []
    
    # Scan and collect data
    if args.scan_today or args.generate_report or not any([args.generate_report]):
        print("📊 Collecting activity data...")
        
        # Initialize collectors
        browser_collector = BrowserCollector(settings)
        ai_chat_collector = AIChatCollector(settings)
        git_collector = GitCollector(settings)
        
        # Collect data
        browser_data = browser_collector.collect(target_date)
        print(f"   ✅ Browser history: {len(browser_data)} entries")
        
        ai_chat_data = ai_chat_collector.collect(target_date)
        print(f"   ✅ AI conversations: {len(ai_chat_data)} entries")
        
        git_data = git_collector.collect(target_date)
        print(f"   ✅ Git activities: {len(git_data)} entries")
        
        # TODO: Add more collectors (files)
        
        # Aggregate data
        aggregator = DataAggregator(settings)
        all_data = aggregator.combine([browser_data, ai_chat_data, git_data])
        
        print(f"📝 Total activities collected: {len(all_data)}")
        
        # Generate quick summary for console
        if all_data:
            report_generator = DailyReportGenerator(settings)
            summary = report_generator.generate_summary_stats(all_data)
            
            print(f"📊 Quick Summary:")
            print(f"   • Productivity Score: {summary['productivity']}%")
            print(f"   • Active Time Span: {summary['timespan']}")
            print(f"   • Categories: {', '.join(f'{cat}({count})' for cat, count in summary['categories'].items())}")
        else:
            print("📊 No activities found for analysis")
    
    # Generate report
    if args.generate_report:
        print("📋 Generating daily report...")
        
        if not all_data:
            # Re-collect data if not already done
            print("📊 Collecting activity data for report...")
            browser_collector = BrowserCollector(settings)
            ai_chat_collector = AIChatCollector(settings)
            git_collector = GitCollector(settings)
            browser_data = browser_collector.collect(target_date)
            ai_chat_data = ai_chat_collector.collect(target_date)
            git_data = git_collector.collect(target_date)
            aggregator = DataAggregator(settings)
            all_data = aggregator.combine([browser_data, ai_chat_data, git_data])
        
        # Generate the report
        report_generator = DailyReportGenerator(settings)
        report_path = report_generator.generate_report(all_data, target_date)
        
        print(f"   ✅ Report saved to: {report_path}")
        
        # Show report preview
        if all_data:
            summary = report_generator.generate_summary_stats(all_data)
            print(f"   📊 Report includes {summary['total']} activities across {len(summary['categories'])} categories")
        else:
            print("   📝 Empty report generated (no activities found)")
    
    print("✨ DayLog processing complete!")


if __name__ == "__main__":
    main()
