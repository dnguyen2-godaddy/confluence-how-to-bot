#!/usr/bin/env python3
"""
QuickSight + Bedrock Dashboard Analyzer

Connects to QuickSight dashboards and uses AWS Bedrock to analyze them with LLM.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from utils.quicksight_manager import QuickSightManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QuickSightBedrockAnalyzer:
    """Analyzes QuickSight dashboards using AWS Bedrock LLM."""
    
    def __init__(self):
        """Initialize QuickSight and Bedrock clients."""
        try:
            from utils import config
            self.quicksight_manager = QuickSightManager()
            
            # Initialize Bedrock client with config
            client_kwargs = {
                'region_name': config.aws_region,
                'aws_access_key_id': config.aws_access_key_id,
                'aws_secret_access_key': config.aws_secret_access_key
            }
            
            # Add session token if available (for temporary credentials)
            if hasattr(config, 'aws_session_token') and config.aws_session_token:
                client_kwargs['aws_session_token'] = config.aws_session_token
            
            self.bedrock_client = boto3.client('bedrock-runtime', **client_kwargs)
            logger.info("✅ QuickSight + Bedrock analyzer initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize: {e}")
            raise
    
    def get_dashboard_metadata(self, dashboard_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard metadata for analysis."""
        try:
            logger.info(f"📊 Getting dashboard metadata for: {dashboard_id}")
            
            # Get dashboard info
            dashboard_info = self.quicksight_manager.get_dashboard_info(dashboard_id)
            
            # Get dashboard definition (structure, visuals, etc.)
            dashboard_def = self.quicksight_manager.quicksight.describe_dashboard_definition(
                AwsAccountId=self.quicksight_manager.account_id,
                DashboardId=dashboard_id
            )
            
            metadata = {
                'basic_info': {
                    'name': dashboard_info.get('name', 'Unknown'),
                    'description': dashboard_info.get('description', ''),
                    'created_time': str(dashboard_info.get('created_time', '')),
                    'last_updated': str(dashboard_info.get('last_updated_time', '')),
                    'status': dashboard_info.get('status', 'Unknown')
                },
                'structure': {
                    'sheets_count': len(dashboard_def.get('Definition', {}).get('Sheets', [])),
                    'data_sets': dashboard_def.get('Definition', {}).get('DataSetIdentifiersDeclarations', []),
                    'calculated_fields': dashboard_def.get('Definition', {}).get('CalculatedFields', [])
                },
                'visuals_summary': self._analyze_visuals(dashboard_def),
                'data_sources': self._get_data_sources_info(dashboard_def)
            }
            
            logger.info("✅ Dashboard metadata extracted successfully")
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Failed to get dashboard metadata: {e}")
            raise
    
    def _analyze_visuals(self, dashboard_def: Dict) -> Dict[str, Any]:
        """Analyze the types and structure of visuals in the dashboard."""
        visuals_summary = {
            'total_visuals': 0,
            'visual_types': {},
            'sheets': []
        }
        
        sheets = dashboard_def.get('Definition', {}).get('Sheets', [])
        
        for sheet in sheets:
            sheet_info = {
                'name': sheet.get('Name', 'Unnamed Sheet'),
                'visuals': []
            }
            
            visuals = sheet.get('Visuals', [])
            visuals_summary['total_visuals'] += len(visuals)
            
            for visual in visuals:
                visual_type = None
                visual_title = 'Untitled Visual'
                
                # Determine visual type
                if 'BarChartVisual' in visual:
                    visual_type = 'Bar Chart'
                    visual_title = visual['BarChartVisual'].get('Title', {}).get('Visibility', 'Bar Chart')
                elif 'LineChartVisual' in visual:
                    visual_type = 'Line Chart'
                    visual_title = visual['LineChartVisual'].get('Title', {}).get('Visibility', 'Line Chart')
                elif 'PieChartVisual' in visual:
                    visual_type = 'Pie Chart'
                    visual_title = visual['PieChartVisual'].get('Title', {}).get('Visibility', 'Pie Chart')
                elif 'TableVisual' in visual:
                    visual_type = 'Table'
                    visual_title = visual['TableVisual'].get('Title', {}).get('Visibility', 'Table')
                elif 'PivotTableVisual' in visual:
                    visual_type = 'Pivot Table'
                    visual_title = visual['PivotTableVisual'].get('Title', {}).get('Visibility', 'Pivot Table')
                else:
                    visual_type = 'Other'
                
                # Count visual types
                visuals_summary['visual_types'][visual_type] = visuals_summary['visual_types'].get(visual_type, 0) + 1
                
                sheet_info['visuals'].append({
                    'type': visual_type,
                    'title': visual_title
                })
            
            visuals_summary['sheets'].append(sheet_info)
        
        return visuals_summary
    
    def _get_data_sources_info(self, dashboard_def: Dict) -> list:
        """Extract data source information from dashboard definition."""
        data_sets = dashboard_def.get('Definition', {}).get('DataSetIdentifiersDeclarations', [])
        return [{'id': ds.get('Identifier'), 'arn': ds.get('DataSetArn')} for ds in data_sets]
    
    def analyze_with_bedrock(self, dashboard_metadata: Dict, analysis_prompt: str = None) -> str:
        """Use AWS Bedrock to analyze the dashboard metadata."""
        try:
            logger.info("🤖 Starting Bedrock analysis...")
            
            if not analysis_prompt:
                analysis_prompt = """
                Analyze this QuickSight dashboard and provide insights on:
                1. Dashboard purpose and business value
                2. Data visualization effectiveness
                3. Potential improvements or recommendations
                4. Key metrics and KPIs being tracked
                5. Overall dashboard design assessment
                """
            
            # Prepare the prompt for Claude
            full_prompt = f"""
            {analysis_prompt}
            
            Dashboard Metadata:
            {json.dumps(dashboard_metadata, indent=2, default=str)}
            
            Please provide a comprehensive analysis in a clear, structured format.
            """
            
            # Call Bedrock Claude model
            response = self.bedrock_client.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 4000,
                    'messages': [
                        {
                            'role': 'user',
                            'content': full_prompt
                        }
                    ]
                })
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            analysis = response_body['content'][0]['text']
            
            logger.info("✅ Bedrock analysis completed successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Bedrock analysis failed: {e}")
            raise
    
    def create_comprehensive_report(self, dashboard_id: str, custom_prompt: str = None) -> Dict[str, Any]:
        """Create a comprehensive dashboard analysis report."""
        try:
            logger.info(f"📝 Creating comprehensive report for dashboard: {dashboard_id}")
            
            # Get dashboard metadata
            metadata = self.get_dashboard_metadata(dashboard_id)
            
            # Analyze with Bedrock
            bedrock_analysis = self.analyze_with_bedrock(metadata, custom_prompt)
            
            # Create comprehensive report
            report = {
                'dashboard_id': dashboard_id,
                'analysis_timestamp': str(datetime.now()),
                'dashboard_metadata': metadata,
                'ai_analysis': bedrock_analysis,
                'summary': {
                    'total_visuals': metadata['visuals_summary']['total_visuals'],
                    'total_sheets': metadata['structure']['sheets_count'],
                    'data_sources_count': len(metadata['data_sources']),
                    'visual_types': metadata['visuals_summary']['visual_types']
                }
            }
            
            logger.info("✅ Comprehensive report created successfully")
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to create report: {e}")
            raise


def main():
    """Main function to demonstrate QuickSight + Bedrock analysis."""
    print("🤖 QuickSight + Bedrock Dashboard Analyzer")
    print("=" * 50)
    
    try:
        # Initialize analyzer
        analyzer = QuickSightBedrockAnalyzer()
        
        # Get dashboard ID from user
        dashboard_id = input("📊 Enter QuickSight Dashboard ID: ").strip()
        
        if not dashboard_id:
            print("❌ Dashboard ID is required")
            return
        
        # Optional custom analysis prompt
        print("\n💭 Custom Analysis Prompt (optional):")
        print("Press Enter for default analysis, or type your custom prompt:")
        custom_prompt = input("> ").strip()
        
        if not custom_prompt:
            custom_prompt = None
        
        print(f"\n🔍 Analyzing dashboard: {dashboard_id}")
        print("⏳ This may take a few moments...")
        
        # Create comprehensive report
        report = analyzer.create_comprehensive_report(dashboard_id, custom_prompt)
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 DASHBOARD ANALYSIS REPORT")
        print("=" * 60)
        
        print(f"\n📋 Dashboard: {report['dashboard_metadata']['basic_info']['name']}")
        print(f"🆔 ID: {dashboard_id}")
        print(f"📅 Analyzed: {report['analysis_timestamp']}")
        
        print(f"\n📈 Summary:")
        print(f"  • Total Visuals: {report['summary']['total_visuals']}")
        print(f"  • Total Sheets: {report['summary']['total_sheets']}")
        print(f"  • Data Sources: {report['summary']['data_sources_count']}")
        print(f"  • Visual Types: {report['summary']['visual_types']}")
        
        print(f"\n🤖 AI Analysis:")
        print("-" * 40)
        print(report['ai_analysis'])
        
        # Save report to file
        report_filename = f"dashboard_analysis_{dashboard_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Full report saved to: {report_filename}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        logger.error(f"Analysis failed: {e}")


if __name__ == "__main__":
    main()