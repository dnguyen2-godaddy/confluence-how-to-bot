#!/usr/bin/env python3
"""
Confluence How-To Bot - Main Entry Point

This module serves as the main entry point for the Confluence How-To Bot application.
"""

import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    logger.info("Starting Confluence How-To Bot")
    
    print("🤖 Confluence How-To Bot")
    print("========================")
    print("AI-powered QuickSight dashboard documentation generator")
    print("Automatically analyzes dashboards and creates comprehensive how-to guides")
    
    print("\n🎯 Available Operations:")
    print("1. 🤖 Launch How-To Bot (Complete AI workflow)")
    print("2. 📊 Query Redshift scorecard data") 
    print("3. 🚀 Create new QuickSight dashboard")
    print("4. 🔧 Test database connection")
    print("5. ❌ Exit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            try:
                import how_to_bot
                print("\n🤖 Launching AI-powered How-To Bot...")
                how_to_bot.main()
            except Exception as e:
                print(f"❌ How-To Bot failed: {e}")
        
        elif choice == '2':
            try:
                from query_redshift import run_scorecard_query
                logger.info("Executing scorecard query...")
                data = run_scorecard_query()
                print(f"\n✅ Query successful! Retrieved {len(data)} records")
                print(f"📊 Data preview:")
                print(data.head())
            except Exception as e:
                print(f"❌ Query failed: {e}")
        
        elif choice == '3':
            try:
                import quicksight_setup
                print("\n🚀 Launching QuickSight setup...")
                quicksight_setup.main()
            except Exception as e:
                print(f"❌ QuickSight setup failed: {e}")
        
        elif choice == '4':
            try:
                from test_connection import test_configuration
                logger.info("Testing database connection...")
                if test_configuration():
                    print("✅ Database connection successful!")
                else:
                    print("❌ Database connection failed!")
            except Exception as e:
                print(f"❌ Connection test failed: {e}")
        
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-5.")
    
    logger.info("Application completed")


if __name__ == "__main__":
    main()
