#!/usr/bin/env python3
"""
Direct Data Analyzer using Bedrock
Analyzes Redshift data directly without QuickSight dashboard
"""

import boto3
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from utils import config
from query_redshift import run_scorecard_query

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectDataAnalyzer:
    """Analyzes data directly using Bedrock without QuickSight dashboard."""
    
    def __init__(self):
        """Initialize Bedrock client."""
        client_kwargs = {
            'region_name': config.aws_region,
            'aws_access_key_id': config.aws_access_key_id,
            'aws_secret_access_key': config.aws_secret_access_key
        }
        
        if hasattr(config, 'aws_session_token') and config.aws_session_token:
            client_kwargs['aws_session_token'] = config.aws_session_token
        
        self.bedrock = boto3.client('bedrock-runtime', **client_kwargs)
        logger.info("✅ Direct Data Analyzer initialized")
    
    def analyze_redshift_data(self, custom_prompt=None):
        """Analyze Redshift data directly with Bedrock."""
        try:
            # Get data from Redshift
            print("📊 Fetching data from Redshift...")
            df = run_scorecard_query()
            print(f"✅ Retrieved {len(df)} records")
            
            # Prepare data summary for analysis
            data_summary = {
                'total_records': len(df),
                'columns': list(df.columns),
                'date_range': {
                    'start': df['metric_report_mst_month'].min() if 'metric_report_mst_month' in df.columns else 'Unknown',
                    'end': df['metric_report_mst_month'].max() if 'metric_report_mst_month' in df.columns else 'Unknown'
                },
                'business_units': df['business_unit'].unique().tolist() if 'business_unit' in df.columns else [],
                'metrics': df['metric_name'].unique().tolist() if 'metric_name' in df.columns else [],
                'entry_types': df['entry_type'].unique().tolist() if 'entry_type' in df.columns else [],
                'sample_data': df.head(10).to_dict('records')
            }
            
            # Create analysis prompt
            default_prompt = """
            Analyze this business scorecard data and provide insights on:
            1. Key performance metrics and trends
            2. Business unit performance comparison
            3. Target vs actual performance analysis
            4. Notable patterns or anomalies
            5. Recommendations for improvement
            
            Focus on actionable insights for business decision making.
            """
            
            analysis_prompt = custom_prompt or default_prompt
            
            # Prepare Bedrock request
            messages = [
                {
                    "role": "user",
                    "content": f"""
                    {analysis_prompt}
                    
                    Here's the business scorecard data summary:
                    
                    Dataset Overview:
                    - Total Records: {data_summary['total_records']}
                    - Date Range: {data_summary['date_range']['start']} to {data_summary['date_range']['end']}
                    - Business Units: {', '.join(data_summary['business_units'])}
                    - Metrics: {', '.join(data_summary['metrics'][:10])}{'...' if len(data_summary['metrics']) > 10 else ''}
                    - Entry Types: {', '.join(data_summary['entry_types'])}
                    
                    Sample Data:
                    {json.dumps(data_summary['sample_data'], indent=2, default=str)}
                    
                    Please provide a comprehensive analysis with specific insights and recommendations.
                    """
                }
            ]
            
            # Call Bedrock
            print("🤖 Analyzing data with AI...")
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": messages,
                "temperature": 0.1
            }
            
            response = self.bedrock.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
                body=json.dumps(body),
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            analysis = response_body['content'][0]['text']
            
            # Display results
            print("\n" + "="*80)
            print("📊 BUSINESS SCORECARD ANALYSIS")
            print("="*80)
            print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📈 Data Records: {data_summary['total_records']}")
            print(f"📊 Business Units: {len(data_summary['business_units'])}")
            print(f"📋 Metrics: {len(data_summary['metrics'])}")
            print("\n🤖 AI Analysis:")
            print("-" * 40)
            print(analysis)
            print("\n" + "="*80)
            
            # Save report
            report = {
                'timestamp': datetime.now().isoformat(),
                'data_summary': data_summary,
                'analysis': analysis,
                'custom_prompt': custom_prompt
            }
            
            filename = f"redshift_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"💾 Report saved to: {filename}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            raise

def main():
    """Main function for direct data analysis."""
    print("🤖 Direct Business Data Analyzer")
    print("=" * 50)
    
    try:
        analyzer = DirectDataAnalyzer()
        
        # Get custom prompt
        print("\n💭 Custom Analysis Focus (optional):")
        print("Press Enter for default analysis, or type your focus:")
        custom_prompt = input("> ").strip()
        
        if not custom_prompt:
            custom_prompt = None
        
        # Run analysis
        analyzer.analyze_redshift_data(custom_prompt)
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    main()