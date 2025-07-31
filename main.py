#!/usr/bin/env python3
"""
QuickSight & Redshift Manager - Main Entry Point

Simple interface for managing QuickSight dashboards and Redshift connections,
plus AI-powered dashboard analysis using AWS Bedrock.
"""

import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def query_redshift():
    """Query Redshift data."""
    try:
        from query_redshift import run_scorecard_query
        logger.info("Executing scorecard query...")
        data = run_scorecard_query()
        print(f"\n✅ Query successful! Retrieved {len(data)} records")
        print(f"📊 Data preview:")
        print(data.head())
        input("\nPress Enter to continue...")
    except Exception as e:
        print(f"❌ Query failed: {e}")
        input("\nPress Enter to continue...")


def manage_quicksight():
    """Manage QuickSight dashboards."""
    try:
        from utils.quicksight_manager import QuickSightManager
        
        print("\n🚀 QuickSight Dashboard Manager")
        print("================================")
        
        # Initialize QuickSight manager
        qs_manager = QuickSightManager()
        print(f"✅ Connected to QuickSight (Account: {qs_manager.account_id})")
        
        while True:
            print("\n🎯 QuickSight Operations:")
            print("1. 📋 List all dashboards")
            print("2. 🔗 Get dashboard embed URL")
            print("3. ❌ Back to main menu")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                try:
                    dashboards = qs_manager.list_dashboards()
                    if dashboards:
                        print(f"\n📊 Found {len(dashboards)} dashboards:")
                        for i, dashboard in enumerate(dashboards, 1):
                            print(f"{i}. {dashboard.get('Name', 'Unnamed')} (ID: {dashboard.get('DashboardId', 'Unknown')})")
                    else:
                        print("\n📭 No dashboards found in your account")
                    input("\nPress Enter to continue...")
                except Exception as e:
                    print(f"❌ Failed to list dashboards: {e}")
                    input("\nPress Enter to continue...")
            
            elif choice == '2':
                dashboard_id = input("\nEnter Dashboard ID: ").strip()
                if dashboard_id:
                    try:
                        url = qs_manager.get_dashboard_embed_url(dashboard_id)
                        print(f"\n🔗 Embed URL: {url}")
                        input("\nPress Enter to continue...")
                    except Exception as e:
                        print(f"❌ Failed to get embed URL: {e}")
                        input("\nPress Enter to continue...")
                else:
                    print("❌ Dashboard ID cannot be empty")
            
            elif choice == '3':
                break
            
            else:
                print("Invalid choice. Please enter 1-3.")
    
    except Exception as e:
        print(f"❌ QuickSight setup failed: {e}")
        input("\nPress Enter to continue...")


def ai_dashboard_analysis():
    """AI-powered dashboard analysis using Bedrock (FIXED VERSION)."""
    try:
        from fixed_dashboard_analyzer import FixedDashboardAnalyzer
        
        print("\n🤖 AI Dashboard Analyzer (Bedrock) - FIXED!")
        print("============================================")
        print("✅ Now works with corporate shared dashboards!")
        
        # Initialize the fixed analyzer
        analyzer = FixedDashboardAnalyzer()
        
        dashboard_id = input("\nEnter QuickSight Dashboard ID to analyze: ").strip()
        
        if dashboard_id:
            print(f"\n🔍 Analyzing dashboard: {dashboard_id}")
            print("This may take a moment...")
            
            # Optional: Get custom analysis prompt
            use_custom = input("\nUse custom analysis prompt? (y/N): ").strip().lower()
            custom_prompt = None
            if use_custom == 'y':
                custom_prompt = input("Enter your analysis focus: ").strip()
            
            # Run the analysis with fixed approach
            report = analyzer.create_dashboard_report(dashboard_id, custom_prompt)
            
            print(f"\n🎉 SUCCESS! Dashboard analysis completed!")
            print(f"📄 Report saved with detailed insights and recommendations")
            
        else:
            print("❌ Dashboard ID cannot be empty")
        
        input("\nPress Enter to continue...")
    
    except Exception as e:
        print(f"❌ AI analysis failed: {e}")
        input("\nPress Enter to continue...")


def ai_direct_analysis():
    """AI-powered direct data analysis using Bedrock."""
    try:
        from direct_data_analyzer import DirectDataAnalyzer
        
        print("\n🧠 AI Direct Data Analysis")
        print("===========================")
        print("Analyzes Redshift data directly with AI (no dashboard needed)")
        
        # Initialize the analyzer
        analyzer = DirectDataAnalyzer()
        
        # Optional: Get custom analysis prompt
        print("\n💭 Custom Analysis Focus (optional):")
        print("Examples: 'Focus on cost optimization', 'Customer satisfaction trends', etc.")
        custom_prompt = input("Press Enter for default analysis, or type your focus: ").strip()
        
        if not custom_prompt:
            custom_prompt = None
            
        print(f"\n🔍 Analyzing your business data...")
        print("This may take a moment...")
        
        # Run the analysis
        analyzer.analyze_redshift_data(custom_prompt)
        
        input("\nPress Enter to continue...")
    
    except Exception as e:
        print(f"❌ AI direct analysis failed: {e}")
        input("\nPress Enter to continue...")


def test_connections():
    """Test database and AWS connections."""
    try:
        print("\n🔧 Connection Tests")
        print("===================")
        
        # Test Redshift
        print("\n1. Testing Redshift connection...")
        try:
            from test_connection import test_configuration
            if test_configuration():
                print("✅ Redshift connection: SUCCESS")
            else:
                print("❌ Redshift connection: FAILED")
        except Exception as e:
            print(f"❌ Redshift test failed: {e}")
        
        # Test QuickSight
        print("\n2. Testing QuickSight connection...")
        try:
            from utils.quicksight_manager import QuickSightManager
            qs_manager = QuickSightManager()
            print(f"✅ QuickSight connection: SUCCESS (Account: {qs_manager.account_id})")
        except Exception as e:
            print(f"❌ QuickSight test failed: {e}")
        
        # Test Bedrock
        print("\n3. Testing Bedrock connection...")
        try:
            from quicksight_bedrock_analyzer import QuickSightBedrockAnalyzer
            analyzer = QuickSightBedrockAnalyzer()
            print("✅ Bedrock connection: SUCCESS")
        except Exception as e:
            print(f"❌ Bedrock test failed: {e}")
        
        input("\nPress Enter to continue...")
    
    except Exception as e:
        print(f"❌ Connection tests failed: {e}")
        input("\nPress Enter to continue...")


def main():
    """Main application entry point."""
    logger.info("Starting QuickSight & Redshift Manager")
    
    while True:
        print("\n" + "="*50)
        print("📊 QuickSight & Redshift Manager")
        print("="*50)
        print("Tools for dashboard creation, data querying, and AI analysis")
        
        print("\n🎯 Available Operations:")
        print("1. 📊 Query Redshift data") 
        print("2. 🚀 Manage QuickSight dashboards")
        print("3. 🤖 AI Dashboard Analysis (Bedrock)")
        print("4. 🧠 AI Direct Data Analysis (Bedrock)")
        print("5. 🔧 Test connections")
        print("6. ❌ Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            query_redshift()
        elif choice == '2':
            manage_quicksight()
        elif choice == '3':
            ai_dashboard_analysis()
        elif choice == '4':
            ai_direct_analysis()
        elif choice == '5':
            test_connections()
        elif choice == '6':
            print("\n👋 Goodbye!")
            logger.info("Application completed")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    main()