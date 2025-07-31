#!/usr/bin/env python3
"""
QuickSight Dashboard Setup and Management

This script demonstrates how to create and manage QuickSight dashboards
for your scorecard data.
"""

import logging
import json
from typing import Dict, Any
from utils.quicksight_manager import QuickSightManager
from query_redshift import run_scorecard_query

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_dashboard() -> Dict[str, Any]:
    """
    Create a complete QuickSight dashboard infrastructure.
    
    Returns:
        Dictionary with dashboard information and URLs
    """
    try:
        print("🚀 Starting QuickSight Dashboard Creation")
        print("=" * 60)
        
        # Initialize QuickSight manager
        logger.info("Initializing QuickSight manager...")
        qs_manager = QuickSightManager()
        
        # Setup complete dashboard infrastructure
        logger.info("Creating dashboard infrastructure...")
        result = qs_manager.setup_complete_dashboard()
        
        # Get dashboard information
        dashboard_info = qs_manager.get_dashboard_info(result['dashboard_id'])
        
        # Display results
        print("\n✅ Dashboard Creation Complete!")
        print("=" * 60)
        print(f"📊 Data Source ID: {result['data_source_id']}")
        print(f"📋 Dataset ID: {result['dataset_id']}")
        print(f"📈 Dashboard ID: {result['dashboard_id']}")
        print(f"🔗 Embed URL: {result['embed_url']}")
        print(f"📅 Created: {dashboard_info.get('created_time', 'N/A')}")
        print(f"🔄 Status: {dashboard_info.get('status', 'N/A')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Dashboard creation failed: {e}")
        print(f"\n❌ Error: {e}")
        print("\n🔧 Troubleshooting Tips:")
        print("1. Ensure AWS credentials are configured in .env")
        print("2. Verify QuickSight is enabled in your AWS account")
        print("3. Check Redshift connection parameters")
        print("4. Ensure proper IAM permissions for QuickSight")
        raise


def get_dashboard_url(dashboard_id: str) -> str:
    """
    Get an embed URL for an existing dashboard.
    
    Args:
        dashboard_id: The QuickSight dashboard ID
        
    Returns:
        The embeddable URL
    """
    try:
        qs_manager = QuickSightManager()
        embed_url = qs_manager.get_dashboard_embed_url(dashboard_id)
        
        print(f"\n🔗 Dashboard Embed URL:")
        print(f"{embed_url}")
        
        return embed_url
        
    except Exception as e:
        logger.error(f"Failed to get dashboard URL: {e}")
        raise


def test_data_connection():
    """Test the Redshift data connection."""
    try:
        print("\n🧪 Testing Redshift Connection")
        print("=" * 40)
        
        # Test data retrieval
        logger.info("Testing Redshift connection...")
        data = run_scorecard_query()
        
        print(f"✅ Connection successful!")
        print(f"📊 Retrieved {len(data)} records")
        print(f"📅 Date range: {data['metric_report_mst_month'].min()} to {data['metric_report_mst_month'].max()}")
        print(f"🏢 Business units: {', '.join(data['business_unit'].unique())}")
        print(f"🌍 Regions: {', '.join(data['region_name'].unique())}")
        
        return True
        
    except Exception as e:
        logger.error(f"Data connection test failed: {e}")
        print(f"❌ Connection failed: {e}")
        return False


def show_usage_examples():
    """Show usage examples for the QuickSight integration."""
    
    examples = """
    
📚 QuickSight Integration Usage Examples
========================================

1. 🔧 Setup your environment (.env file):
   ```
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   AWS_REGION=us-west-2
   
   REDSHIFT_HOST=your_redshift_host
   REDSHIFT_DATABASE=your_database
   REDSHIFT_PORT=5439
   REDSHIFT_USER=your_username
   REDSHIFT_PASSWORD=your_password
   ```

2. 📊 Create a complete dashboard:
   ```python
   from utils.quicksight_manager import QuickSightManager
   
   qs_manager = QuickSightManager()
   result = qs_manager.setup_complete_dashboard()
   print(f"Dashboard URL: {result['embed_url']}")
   ```

3. 🔗 Get embed URL for existing dashboard:
   ```python
   embed_url = qs_manager.get_dashboard_embed_url('your-dashboard-id')
   ```

4. 📋 Get dashboard information:
   ```python
   info = qs_manager.get_dashboard_info('your-dashboard-id')
   print(f"Dashboard: {info['name']}")
   ```

5. 🌐 Embed in a web page:
   ```html
   <iframe 
       src="{embed_url}" 
       width="100%" 
       height="600">
   </iframe>
   ```

🎯 Key Features:
• Automated data source creation from your Redshift connection
• Dataset creation using your existing scorecard query
• Interactive dashboard with multiple visualizations:
  - Bar chart: Metrics by Region
  - Line chart: Metrics Trend Over Time  
  - Pivot table: Detailed Metrics Table
• Secure embed URLs for web integration
• Complete error handling and logging

⚠️  Important Notes:
• QuickSight account must be set up in your AWS account
• Ensure proper IAM permissions for QuickSight operations
• URLs are valid for 60 minutes (default) but can be regenerated
• Uses SPICE for better dashboard performance
"""
    
    print(examples)


def main():
    """Main function for QuickSight setup and management."""
    print("🌟 QuickSight Dashboard Management")
    print("===================================")
    
    # Show usage examples
    if input("\n📖 Would you like to see usage examples? (y/N): ").lower() in ['y', 'yes']:
        show_usage_examples()
    
    # Test data connection
    if input("\n🧪 Test Redshift data connection? (y/N): ").lower() in ['y', 'yes']:
        if not test_data_connection():
            print("\n⚠️  Please fix your Redshift connection before proceeding.")
            return
    
    # Main menu
    while True:
        print("\n🎯 What would you like to do?")
        print("1. 📊 Create new dashboard")
        print("2. 🔗 Get embed URL for existing dashboard")
        print("3. 📋 Show usage examples")
        print("4. ❌ Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            try:
                result = create_dashboard()
                
                # Save result to file for future reference
                with open('quicksight_setup_result.json', 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n💾 Dashboard details saved to: quicksight_setup_result.json")
                
            except Exception as e:
                print(f"Dashboard creation failed: {e}")
        
        elif choice == '2':
            dashboard_id = input("Enter dashboard ID: ").strip()
            if dashboard_id:
                try:
                    get_dashboard_url(dashboard_id)
                except Exception as e:
                    print(f"Failed to get URL: {e}")
            else:
                print("Dashboard ID cannot be empty.")
        
        elif choice == '3':
            show_usage_examples()
        
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()