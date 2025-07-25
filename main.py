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
from processors.aggregator import DataAggregator
from config.settings import Settings


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='DayLog - Personal Daily Activity Logger')
    parser.add_argument('--scan-today', action='store_true', 
                       help='Scan and collect today\'s activity data')
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate daily activity report')
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
    
    # Scan and collect data
    if args.scan_today or not any([args.generate_report]):
        print("📊 Collecting activity data...")
        
        # Initialize collectors
        browser_collector = BrowserCollector(settings)
        ai_chat_collector = AIChatCollector(settings)
        
        # Collect data
        browser_data = browser_collector.collect(target_date)
        print(f"   ✅ Browser history: {len(browser_data)} entries")
        
        ai_chat_data = ai_chat_collector.collect(target_date)
        print(f"   ✅ AI conversations: {len(ai_chat_data)} entries")
        
        # TODO: Add more collectors (files, git)
        
        # Aggregate data
        aggregator = DataAggregator(settings)
        all_data = aggregator.combine([browser_data, ai_chat_data])
        
        print(f"📝 Total activities collected: {len(all_data)}")
    
    # Generate report
    if args.generate_report:
        print("📋 Generating daily report...")
        # TODO: Implement report generation
        print("   ⏳ Report generation coming soon...")
    
    print("✨ DayLog processing complete!")


if __name__ == "__main__":
    main()
