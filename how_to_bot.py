#!/usr/bin/env python3
"""
Confluence How-To Bot - Main Workflow

This is the main workflow orchestrator that coordinates dashboard analysis,
AI-powered documentation generation, and Confluence upload.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from utils.dashboard_analyzer import DashboardAnalyzer, DashboardStructure
from utils.ai_analyzer import AIAnalyzer
from utils.document_generator import DocumentGenerator
from utils.confluence_uploader import ConfluenceUploader
from utils.config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HowToBot:
    """Main orchestrator for the Confluence How-To Bot workflow."""
    
    def __init__(self):
        """Initialize the How-To Bot with all required components."""
        try:
            logger.info("Initializing Confluence How-To Bot...")
            
            # Initialize components
            self.dashboard_analyzer = DashboardAnalyzer()
            self.ai_analyzer = AIAnalyzer()
            self.document_generator = DocumentGenerator()
            self.confluence_uploader = ConfluenceUploader()
            
            logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize How-To Bot: {e}")
            raise
    
    def process_dashboard(self, 
                         dashboard_id: str,
                         upload_to_confluence: bool = True,
                         save_local: bool = True,
                         parent_page_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete workflow: analyze dashboard, generate documentation, and upload to Confluence.
        
        Args:
            dashboard_id: QuickSight dashboard ID to process
            upload_to_confluence: Whether to upload to Confluence
            save_local: Whether to save documentation locally
            parent_page_title: Parent page title in Confluence
            
        Returns:
            Complete processing results
        """
        try:
            logger.info(f"🚀 Starting complete workflow for dashboard: {dashboard_id}")
            
            results = {
                'dashboard_id': dashboard_id,
                'start_time': datetime.now().isoformat(),
                'stages': {}
            }
            
            # Stage 1: Dashboard Analysis
            logger.info("📊 Stage 1: Analyzing dashboard structure...")
            dashboard_structure = self.dashboard_analyzer.analyze_dashboard(dashboard_id)
            results['stages']['analysis'] = {
                'status': 'completed',
                'dashboard_name': dashboard_structure.name,
                'visualizations_count': len(dashboard_structure.visualizations),
                'datasets_count': len(dashboard_structure.datasets)
            }
            logger.info(f"✅ Analysis complete: {dashboard_structure.name}")
            
            # Stage 2: AI Analysis
            logger.info("🤖 Stage 2: AI-powered documentation analysis...")
            
            # Get AI insights
            purpose_analysis = self.ai_analyzer.analyze_dashboard_purpose(dashboard_structure)
            navigation_guide = self.ai_analyzer.generate_navigation_guide(dashboard_structure)
            use_cases = self.ai_analyzer.generate_use_cases(dashboard_structure, purpose_analysis)
            best_practices = self.ai_analyzer.generate_best_practices(dashboard_structure)
            
            results['stages']['ai_analysis'] = {
                'status': 'completed',
                'purpose': purpose_analysis.get('purpose', 'N/A'),
                'target_audience': purpose_analysis.get('target_audience', 'N/A'),
                'complexity_level': purpose_analysis.get('complexity_level', 'N/A'),
                'use_cases_count': len(use_cases)
            }
            logger.info("✅ AI analysis complete")
            
            # Stage 3: Document Generation
            logger.info("📝 Stage 3: Generating documentation...")
            documentation = self.document_generator.generate_complete_documentation(
                dashboard_structure,
                purpose_analysis,
                navigation_guide,
                use_cases,
                best_practices
            )
            
            results['stages']['documentation'] = {
                'status': 'completed',
                'title': documentation['title'],
                'summary': documentation['summary']
            }
            logger.info("✅ Documentation generated")
            
            # Stage 4: Save Local Files (if requested)
            if save_local:
                logger.info("💾 Stage 4a: Saving local files...")
                output_dir = f"output_{dashboard_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                saved_files = self.document_generator.save_documentation(documentation, output_dir)
                
                results['stages']['local_save'] = {
                    'status': 'completed',
                    'output_directory': output_dir,
                    'files_saved': saved_files
                }
                logger.info(f"✅ Local files saved to: {output_dir}")
            
            # Stage 5: Upload to Confluence (if requested)
            if upload_to_confluence:
                logger.info("📤 Stage 5: Uploading to Confluence...")
                
                # Create directory structure if needed
                directory_result = self.confluence_uploader.create_dashboard_directory_structure(
                    dashboard_structure.name
                )
                
                # Upload documentation
                upload_result = self.confluence_uploader.upload_documentation(
                    documentation,
                    parent_page_title or directory_result.get('main_page', {}).get('title'),
                    update_existing=True
                )
                
                results['stages']['confluence_upload'] = {
                    'status': 'completed' if upload_result['success'] else 'failed',
                    'action': upload_result.get('action'),
                    'page_url': upload_result.get('page_url'),
                    'page_id': upload_result.get('page_id'),
                    'error': upload_result.get('error')
                }
                
                if upload_result['success']:
                    logger.info(f"✅ Documentation uploaded to Confluence: {upload_result['page_url']}")
                else:
                    logger.error(f"❌ Confluence upload failed: {upload_result['error']}")
            
            # Complete workflow
            results['end_time'] = datetime.now().isoformat()
            results['status'] = 'completed'
            results['success'] = True
            
            logger.info("🎉 Workflow completed successfully!")
            return results
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            results['status'] = 'failed'
            results['success'] = False
            results['error'] = str(e)
            results['end_time'] = datetime.now().isoformat()
            return results
    
    def list_available_dashboards(self) -> List[Dict[str, str]]:
        """Get list of available dashboards for processing."""
        try:
            logger.info("📋 Fetching available dashboards...")
            dashboards = self.dashboard_analyzer.get_dashboard_list()
            logger.info(f"Found {len(dashboards)} dashboards")
            return dashboards
            
        except Exception as e:
            logger.error(f"Failed to get dashboard list: {e}")
            return []
    
    def validate_configuration(self) -> Dict[str, bool]:
        """Validate all required configurations."""
        validation_results = {
            'aws_config': config.validate_aws_config(),
            'ai_config': config.validate_ai_config(),
            'confluence_config': config.validate_confluence_config(),
            'redshift_config': config.validate_redshift_config()
        }
        
        all_valid = all(validation_results.values())
        validation_results['all_valid'] = all_valid
        
        return validation_results
    
    def test_integrations(self) -> Dict[str, Any]:
        """Test all integrations to ensure they're working."""
        test_results = {}
        
        # Test QuickSight connection
        try:
            dashboards = self.dashboard_analyzer.get_dashboard_list()
            test_results['quicksight'] = {
                'status': 'success',
                'dashboard_count': len(dashboards)
            }
        except Exception as e:
            test_results['quicksight'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        # Test AI connection
        try:
            # Simple test with minimal dashboard structure
            from utils.dashboard_analyzer import DashboardStructure
            test_structure = DashboardStructure(
                dashboard_id='test',
                name='Test Dashboard',
                description='Test',
                created_time='2024-01-01',
                last_updated='2024-01-01',
                version='1',
                status='PUBLISHED',
                sheets=[],
                visualizations=[],
                datasets=[]
            )
            
            purpose = self.ai_analyzer.analyze_dashboard_purpose(test_structure)
            test_results['ai'] = {
                'status': 'success',
                'test_response': bool(purpose.get('purpose'))
            }
        except Exception as e:
            test_results['ai'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        # Test Confluence connection
        try:
            space_info = self.confluence_uploader.get_space_info()
            test_results['confluence'] = {
                'status': 'success',
                'space_name': space_info.get('name'),
                'space_key': space_info.get('key')
            }
        except Exception as e:
            test_results['confluence'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        return test_results
    
    def analyze_dashboard_only(self, dashboard_id: str) -> Dict[str, Any]:
        """Analyze dashboard without generating documentation (for preview)."""
        try:
            logger.info(f"📊 Analyzing dashboard: {dashboard_id}")
            
            # Analyze dashboard structure
            structure = self.dashboard_analyzer.analyze_dashboard(dashboard_id)
            
            # Generate analysis summary
            summary = self.dashboard_analyzer.generate_analysis_summary(structure)
            
            # Get AI purpose analysis
            purpose_analysis = self.ai_analyzer.analyze_dashboard_purpose(structure)
            
            return {
                'success': True,
                'dashboard_id': dashboard_id,
                'structure_summary': summary,
                'purpose_analysis': purpose_analysis,
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_confluence_existing_docs(self) -> List[Dict[str, Any]]:
        """Get list of existing dashboard documentation in Confluence."""
        try:
            return self.confluence_uploader.list_existing_dashboard_docs()
        except Exception as e:
            logger.error(f"Failed to get existing docs: {e}")
            return []


def main():
    """Main interactive interface for the How-To Bot."""
    print("🤖 Confluence How-To Bot")
    print("=" * 50)
    print("AI-powered QuickSight dashboard documentation generator")
    
    try:
        # Initialize the bot
        bot = HowToBot()
        
        # Validate configuration
        print("\n🔧 Validating configuration...")
        validation = bot.validate_configuration()
        
        for component, status in validation.items():
            if component != 'all_valid':
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {component.replace('_', ' ').title()}: {'OK' if status else 'MISSING'}")
        
        if not validation['all_valid']:
            print("\n⚠️  Some configurations are missing. Please check your .env file.")
            print("Required environment variables:")
            print("   - AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION")
            print("   - OPENAI_API_KEY")
            print("   - CONFLUENCE_URL, CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN, CONFLUENCE_SPACE_KEY")
            return
        
        # Test integrations
        print("\n🧪 Testing integrations...")
        tests = bot.test_integrations()
        
        for service, result in tests.items():
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"   {status_icon} {service.title()}: {result['status']}")
            if result['status'] == 'failed':
                print(f"      Error: {result['error']}")
        
        if any(test['status'] == 'failed' for test in tests.values()):
            print("\n⚠️  Some integrations failed. Please check your configuration.")
            return
        
        # Main menu
        while True:
            print("\n🎯 What would you like to do?")
            print("1. 📊 List available dashboards")
            print("2. 🔍 Analyze specific dashboard (preview)")
            print("3. 📝 Generate complete documentation")
            print("4. 📚 View existing Confluence documentation")
            print("5. ⚙️  Test integrations again")
            print("6. ❌ Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                dashboards = bot.list_available_dashboards()
                if dashboards:
                    print(f"\n📊 Found {len(dashboards)} dashboards:")
                    for i, dashboard in enumerate(dashboards, 1):
                        print(f"   {i}. {dashboard['name']} (ID: {dashboard['dashboard_id']})")
                        if dashboard.get('created_time'):
                            print(f"      Created: {dashboard['created_time'][:10]}")
                else:
                    print("No dashboards found.")
            
            elif choice == '2':
                dashboard_id = input("Enter dashboard ID: ").strip()
                if dashboard_id:
                    print("🔍 Analyzing dashboard...")
                    result = bot.analyze_dashboard_only(dashboard_id)
                    
                    if result['success']:
                        print("\n✅ Analysis Results:")
                        print(f"   Dashboard: {result['structure_summary']['dashboard_info']['name']}")
                        print(f"   Purpose: {result['purpose_analysis']['purpose']}")
                        print(f"   Target Audience: {result['purpose_analysis']['target_audience']}")
                        print(f"   Visualizations: {result['structure_summary']['structure_overview']['total_visualizations']}")
                        print(f"   Data Sources: {result['structure_summary']['structure_overview']['total_datasets']}")
                    else:
                        print(f"❌ Analysis failed: {result['error']}")
            
            elif choice == '3':
                dashboard_id = input("Enter dashboard ID: ").strip()
                if dashboard_id:
                    upload_confluence = input("Upload to Confluence? (y/N): ").lower() in ['y', 'yes']
                    save_local = input("Save locally? (Y/n): ").lower() not in ['n', 'no']
                    
                    parent_page = None
                    if upload_confluence:
                        parent_page = input("Parent page title (optional): ").strip() or None
                    
                    print("\n🚀 Starting complete workflow...")
                    results = bot.process_dashboard(
                        dashboard_id=dashboard_id,
                        upload_to_confluence=upload_confluence,
                        save_local=save_local,
                        parent_page_title=parent_page
                    )
                    
                    print(f"\n📋 Workflow Results:")
                    print(f"   Status: {'✅ Success' if results['success'] else '❌ Failed'}")
                    
                    if results['success']:
                        for stage, info in results['stages'].items():
                            print(f"   {stage.replace('_', ' ').title()}: {info['status']}")
                        
                        if 'confluence_upload' in results['stages'] and results['stages']['confluence_upload']['page_url']:
                            print(f"\n🔗 Confluence Page: {results['stages']['confluence_upload']['page_url']}")
                        
                        if 'local_save' in results['stages']:
                            print(f"\n💾 Local Files: {results['stages']['local_save']['output_directory']}")
                    else:
                        print(f"   Error: {results.get('error', 'Unknown error')}")
            
            elif choice == '4':
                docs = bot.get_confluence_existing_docs()
                if docs:
                    print(f"\n📚 Found {len(docs)} existing documentation pages:")
                    for doc in docs:
                        print(f"   • {doc['title']}")
                        print(f"     URL: {doc['url']}")
                else:
                    print("No existing documentation found.")
            
            elif choice == '5':
                print("\n🧪 Re-testing integrations...")
                tests = bot.test_integrations()
                for service, result in tests.items():
                    status_icon = "✅" if result['status'] == 'success' else "❌"
                    print(f"   {status_icon} {service.title()}: {result['status']}")
            
            elif choice == '6':
                print("\n👋 Goodbye!")
                break
            
            else:
                print("Invalid choice. Please enter 1-6.")
    
    except Exception as e:
        logger.error(f"Application failed: {e}")
        print(f"\n❌ Application error: {e}")


if __name__ == "__main__":
    main()