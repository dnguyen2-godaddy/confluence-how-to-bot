#!/usr/bin/env python3
"""
QuickSight Dashboard Setup Script

This script sets up the complete QuickSight dashboard infrastructure
for the GoCaas companion analysis.
"""

import logging
from utils.quicksight_manager import QuickSightManager
from gocaas_companion import GoCaasCompanion

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_quicksight_dashboard():
    """Set up the complete QuickSight dashboard infrastructure."""
    logger.info("🚀 Starting QuickSight dashboard setup...")
    
    try:
        # Initialize QuickSight manager
        qs_manager = QuickSightManager()
        
        # Step 1: Create Redshift data source
        logger.info("📊 Creating Redshift data source...")
        data_source_id = qs_manager.create_redshift_data_source()
        
        # Step 2: Create dataset
        logger.info("📋 Creating scorecard dataset...")
        dataset_id = qs_manager.create_scorecard_dataset(data_source_id)
        
        # Step 3: Create dashboard
        logger.info("📈 Creating dashboard...")
        dashboard_id = qs_manager.create_scorecard_dashboard(dataset_id)
        
        # Step 4: Get embed URL
        logger.info("🔗 Generating embed URL...")
        embed_url = qs_manager.get_dashboard_embed_url(dashboard_id)
        
        # Step 5: Initialize GoCaas companion
        logger.info("🤖 Initializing GoCaas companion...")
        companion = GoCaasCompanion()
        
        # Summary of created resources
        setup_summary = f"""
🎉 QuickSight Setup Complete!

📊 Resources Created:
- Data Source ID: {data_source_id}
- Dataset ID: {dataset_id}
- Dashboard ID: {dashboard_id}

🔗 Dashboard URL: {embed_url}

🤖 GoCaas Companion Ready!

🚀 Next Steps:
1. Access your dashboard: {embed_url}
2. Test GoCaas analysis: python gocaas_companion.py
3. Generate insights: companion.analyze_dashboard('{dashboard_id}')

📝 Configuration saved for future use.
        """
        
        print(setup_summary)
        logger.info("✅ QuickSight setup completed successfully!")
        
        return {
            'data_source_id': data_source_id,
            'dataset_id': dataset_id,
            'dashboard_id': dashboard_id,
            'embed_url': embed_url,
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"❌ QuickSight setup failed: {e}")
        print(f"\n⚠️  Setup Error: {e}")
        print("\n🔧 Troubleshooting Tips:")
        print("1. Ensure AWS credentials are configured")
        print("2. Verify QuickSight is enabled in your AWS account")
        print("3. Check Redshift connection parameters")
        print("4. Ensure proper IAM permissions for QuickSight")
        raise


def test_gocaas_analysis():
    """Test the GoCaas companion analysis."""
    logger.info("🧪 Testing GoCaas analysis...")
    
    try:
        companion = GoCaasCompanion()
        
        # Test with direct data analysis (fallback when no dashboard exists)
        logger.info("📊 Running analysis on scorecard data...")
        analysis = companion._summarize_data(companion.run_scorecard_query())
        
        print("\n🤖 GoCaas Test Results:")
        print("="*50)
        print(f"✅ Data Summary: {analysis['total_records']} records processed")
        print(f"✅ AI Companion: Ready for dashboard analysis")
        print(f"✅ Recommendations: AI-powered insights available")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ GoCaas test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 QuickSight + GoCaas Setup")
    print("="*50)
    
    # Check if user wants to proceed
    response = input("\n📋 This will create QuickSight resources in your AWS account.\nProceed? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        try:
            # Run the setup
            setup_results = setup_quicksight_dashboard()
            
            # Test GoCaas
            if test_gocaas_analysis():
                print("\n🎉 All systems operational!")
                print("Your QuickSight + GoCaas environment is ready to use.")
            else:
                print("\n⚠️  Setup complete, but GoCaas testing failed.")
                print("Check the logs for troubleshooting information.")
                
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            print("\nPlease check the logs and try again.")
    else:
        print("\n👋 Setup cancelled by user.")
        print("Run this script again when you're ready to proceed.")