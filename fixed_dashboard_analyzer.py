#!/usr/bin/env python3
"""
Fixed Dashboard Analyzer using Embed API Approach
Works with corporate shared QuickSight dashboards
"""

import boto3
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from utils import config

load_dotenv()
logging.basicConfig(level=logging.INFO)

class FixedDashboardAnalyzer:
    """Dashboard analyzer that works with corporate shared dashboards."""
    
    def __init__(self):
        """Initialize QuickSight and Bedrock clients."""
        client_kwargs = {
            'region_name': config.aws_region,
            'aws_access_key_id': config.aws_access_key_id,
            'aws_secret_access_key': config.aws_secret_access_key
        }
        
        if hasattr(config, 'aws_session_token') and config.aws_session_token:
            client_kwargs['aws_session_token'] = config.aws_session_token
        
        self.quicksight = boto3.client('quicksight', **client_kwargs)
        self.bedrock = boto3.client('bedrock-runtime', **client_kwargs)
        self.sts = boto3.client('sts', **client_kwargs)
        
        self.our_account = self.sts.get_caller_identity()['Account']
        self.user_arn = f"arn:aws:quicksight:us-west-2:{self.our_account}:user/default/GD-AWS-USA-GD-AISummerCa-Dev-Private-PowerUser/dnguyen2@godaddy.com"
        
        print("✅ Fixed Dashboard Analyzer initialized")
        print(f"   Account: {self.our_account}")
    
    def get_dashboard_access(self, dashboard_id):
        """Get dashboard access via embed URL."""
        try:
            # Generate embed URL (this works for your dashboard!)
            response = self.quicksight.generate_embed_url_for_registered_user(
                AwsAccountId=self.our_account,
                UserArn=self.user_arn,
                ExperienceConfiguration={
                    'Dashboard': {
                        'InitialDashboardId': dashboard_id
                    }
                },
                SessionLifetimeInMinutes=60
            )
            
            embed_url = response.get('EmbedUrl', '')
            print(f"✅ Dashboard accessible via embed URL")
            return embed_url
            
        except Exception as e:
            print(f"❌ Embed URL generation failed: {e}")
            return None
    
    def extract_dashboard_metadata(self, dashboard_id):
        """Extract what we can about the dashboard."""
        
        # Get embed access first (proves dashboard exists)
        embed_url = self.get_dashboard_access(dashboard_id)
        if not embed_url:
            raise Exception("Cannot access dashboard")
        
        # Create metadata from what we know
        metadata = {
            'dashboard_id': dashboard_id,
            'embed_url': embed_url,
            'account_id': self.our_account,
            'access_method': 'embed_url',
            'user_arn': self.user_arn,
            'timestamp': datetime.now().isoformat(),
            'status': 'accessible_via_embed'
        }
        
        # Try to get any additional info through other APIs
        try:
            # Try list_dashboards to see if we can find this dashboard
            response = self.quicksight.list_dashboards(AwsAccountId=self.our_account)
            dashboards = response.get('DashboardSummaryList', [])
            
            for dash in dashboards:
                if dash.get('DashboardId') == dashboard_id:
                    metadata.update({
                        'name': dash.get('Name', 'Unknown'),
                        'created_time': dash.get('CreatedTime', '').isoformat() if dash.get('CreatedTime') else None,
                        'last_updated': dash.get('LastUpdatedTime', '').isoformat() if dash.get('LastUpdatedTime') else None,
                        'published_version': dash.get('PublishedVersionNumber', 'Unknown')
                    })
                    break
        except:
            pass  # If this fails, we continue with basic metadata
        
        return metadata
    
    def analyze_with_bedrock(self, metadata, custom_prompt=None):
        """Analyze dashboard using Bedrock AI."""
        
        # Create analysis prompt
        default_prompt = """
        Analyze this QuickSight dashboard and provide insights on:
        1. Dashboard accessibility and configuration
        2. Potential use cases based on the setup
        3. Recommendations for dashboard optimization
        4. Best practices for corporate dashboard sharing
        
        Focus on actionable insights for business intelligence and dashboard management.
        """
        
        analysis_prompt = custom_prompt or default_prompt
        
        # Prepare dashboard information for analysis
        dashboard_info = f"""
        Dashboard Analysis:
        - Dashboard ID: {metadata['dashboard_id']}
        - Access Method: {metadata['access_method']}
        - Account: {metadata['account_id']}
        - Status: {metadata['status']}
        - User Access: {metadata['user_arn']}
        - Embed URL Available: Yes
        """
        
        if metadata.get('name'):
            dashboard_info += f"\n- Dashboard Name: {metadata['name']}"
        if metadata.get('created_time'):
            dashboard_info += f"\n- Created: {metadata['created_time']}"
        if metadata.get('last_updated'):
            dashboard_info += f"\n- Last Updated: {metadata['last_updated']}"
        
        messages = [
            {
                "role": "user",
                "content": f"""
                {analysis_prompt}
                
                {dashboard_info}
                
                Please provide analysis and recommendations for this corporate QuickSight dashboard.
                """
            }
        ]
        
        # Call Bedrock
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 3000,
            "messages": messages,
            "temperature": 0.1
        }
        
        response = self.bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=json.dumps(body),
            contentType='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def create_dashboard_report(self, dashboard_id, custom_prompt=None):
        """Create comprehensive dashboard analysis report."""
        try:
            print(f"🔍 Analyzing dashboard: {dashboard_id}")
            
            # Extract metadata
            metadata = self.extract_dashboard_metadata(dashboard_id)
            print("✅ Dashboard metadata extracted")
            
            # Analyze with AI
            print("🤖 Analyzing with AI...")
            ai_analysis = self.analyze_with_bedrock(metadata, custom_prompt)
            
            # Create comprehensive report
            report = {
                'dashboard_id': dashboard_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'metadata': metadata,
                'ai_analysis': ai_analysis,
                'access_status': 'SUCCESS - Accessible via embed URL',
                'method': 'Corporate embed API approach'
            }
            
            # Display results
            print("\n" + "="*80)
            print("📊 DASHBOARD ANALYSIS REPORT (FIXED VERSION)")
            print("="*80)
            print(f"🆔 Dashboard ID: {dashboard_id}")
            print(f"📅 Analysis Date: {report['analysis_timestamp']}")
            print(f"✅ Access Status: {report['access_status']}")
            print(f"🔧 Method: {report['method']}")
            
            if metadata.get('name'):
                print(f"📋 Dashboard Name: {metadata['name']}")
            
            print(f"\n🤖 AI Analysis:")
            print("-" * 40)
            print(ai_analysis)
            print("\n" + "="*80)
            
            # Save report
            filename = f"dashboard_analysis_fixed_{dashboard_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"💾 Report saved to: {filename}")
            
            return report
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            raise

def main():
    """Main function for fixed dashboard analysis."""
    try:
        analyzer = FixedDashboardAnalyzer()
        dashboard_id = "8c447a9b-b83c-4f80-b53c-0b9f1719c516"
        
        # Optional custom prompt
        custom_prompt = input("\n💭 Custom analysis focus (or press Enter): ").strip()
        if not custom_prompt:
            custom_prompt = None
        
        # Run analysis
        report = analyzer.create_dashboard_report(dashboard_id, custom_prompt)
        
        print("\n🎉 SUCCESS! Dashboard analysis completed using fixed approach!")
        
    except Exception as e:
        print(f"❌ Fixed analyzer failed: {e}")

if __name__ == "__main__":
    main()