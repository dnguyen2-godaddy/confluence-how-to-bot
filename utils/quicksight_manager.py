"""
QuickSight Manager - Handles QuickSight dashboard operations and connectivity
"""

import base64
import boto3
import glob
import json
import logging
import os
import re
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any
from utils.config import config

logger = logging.getLogger(__name__)


class QuickSightManager:
    """Manager class for QuickSight dashboard operations."""
    
    def __init__(self, enable_write_operations=False):
        """Initialize QuickSight client with AWS credentials.
        
        Args:
            enable_write_operations (bool): Enable dashboard creation/import operations
        """
        try:
            # Store write operations setting
            self.enable_write_operations = enable_write_operations
            
            # Initialize QuickSight client
            self.client = boto3.client(
                'quicksight',
                region_name=config.aws_region,
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key,
                aws_session_token=getattr(config, 'aws_session_token', None)
            )
            
            # Log security context for audit
            if enable_write_operations:
                logger.info("🔓 QuickSight client initialized with WRITE permissions enabled")
                logger.warning("⚠️ Write operations enabled - can create/modify dashboards")
            else:
                logger.info("🔒 QuickSight client initialized with read-only intent")
            
            # Get AWS account ID
            sts = boto3.client(
                'sts',
                region_name=config.aws_region,
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key,
                aws_session_token=getattr(config, 'aws_session_token', None)
            )
            
            identity = sts.get_caller_identity()
            self.account_id = identity['Account']
            logger.info(f"✅ QuickSight Manager initialized for account: {self.account_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize QuickSight Manager: {e}")
            raise

    def test_connection(self) -> bool:
        """Test QuickSight connection by listing dashboards."""
        try:
            response = self.client.list_dashboards(
                AwsAccountId=self.account_id,
                MaxResults=10
            )
            logger.info(f"✅ QuickSight connection successful. Found {len(response.get('DashboardSummaryList', []))} dashboards")
            return True
        except Exception as e:
            logger.error(f"❌ QuickSight connection failed: {e}")
            return False
    
    def validate_security_permissions(self) -> Dict[str, bool]:
        """Validate current permissions and security context."""
        permissions_check = {
            'can_list_dashboards': False,
            'can_describe_dashboard': False,
            'can_read_only': True,  # Assume read-only until proven otherwise
            'has_write_access': False
        }
        
        try:
            # Test read permissions
            self.client.list_dashboards(AwsAccountId=self.account_id, MaxResults=1)
            permissions_check['can_list_dashboards'] = True
            logger.info("🔍 Confirmed: Can list dashboards")
            
            # Test if we have any dashboards to test describe
            dashboards = self.list_dashboards()
            if dashboards:
                dashboard_id = dashboards[0]['DashboardId']
                self.client.describe_dashboard(AwsAccountId=self.account_id, DashboardId=dashboard_id)
                permissions_check['can_describe_dashboard'] = True
                logger.info("🔍 Confirmed: Can describe dashboards")
            
            # Test for dangerous write permissions (we should NOT have these)
            try:
                # This should fail in a secure setup
                self.client.list_iam_policy_assignments(AwsAccountId=self.account_id)
                permissions_check['has_write_access'] = True
                permissions_check['can_read_only'] = False
                logger.warning("⚠️ WARNING: Detected write permissions - consider using read-only role")
            except:
                logger.info("🔒 Confirmed: No write permissions (this is good for security)")
                
        except Exception as e:
            logger.error(f"❌ Security validation failed: {e}")
            
        return permissions_check
    
    def list_dashboards(self, include_shared=True) -> List[Dict]:
        """List all available QuickSight dashboards, including shared ones."""
        try:
            dashboards = []
            next_token = None
            
            # Get dashboards from own account
            while True:
                if next_token:
                    response = self.client.list_dashboards(
                        AwsAccountId=self.account_id,
                        NextToken=next_token
                    )
                else:
                    response = self.client.list_dashboards(
                        AwsAccountId=self.account_id
                    )
                
                dashboards.extend(response.get('DashboardSummaryList', []))
                next_token = response.get('NextToken')
                
                if not next_token:
                    break
            
            # Try to get shared dashboards if enabled
            if include_shared:
                try:
                    # Search for dashboards shared with current user
                    # Note: search_dashboards requires at least one filter, so we use a broad name search
                    shared_response = self.client.search_dashboards(
                        AwsAccountId=self.account_id,
                        Filters=[
                            {
                                'Name': 'DASHBOARD_NAME',
                                'Operator': 'StringLike', 
                                'Value': '%'  # Search for dashboards with any name
                            }
                        ]
                    )
                    shared_dashboards = shared_response.get('DashboardSummaryList', [])
                    
                    # Add shared dashboards that aren't already in the list
                    existing_ids = {d.get('DashboardId') for d in dashboards}
                    for shared_dash in shared_dashboards:
                        if shared_dash.get('DashboardId') not in existing_ids:
                            shared_dash['_shared'] = True  # Mark as shared
                            dashboards.append(shared_dash)
                    
                    logger.info(f"🌐 Found {len(shared_dashboards)} shared/accessible dashboards")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Could not search for shared dashboards: {e}")
            
            logger.info(f"📊 Found {len(dashboards)} total QuickSight dashboards")
            return dashboards
            
        except Exception as e:
            logger.error(f"❌ Failed to list dashboards: {e}")
            return []
    
    def get_dashboard_details(self, dashboard_id: str) -> Optional[Dict]:
        """Get detailed information about a specific dashboard."""
        try:
            response = self.client.describe_dashboard(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id
            )
            return response.get('Dashboard')
        except Exception as e:
            logger.error(f"❌ Failed to get dashboard details for {dashboard_id}: {e}")
            return None
    
    def get_embed_url(self, dashboard_id: str, user_arn: Optional[str] = None, 
                      session_lifetime: int = 600) -> Optional[str]:
        """Generate dashboard embed URL for embedding in applications."""
        try:
            params = {
                'AwsAccountId': self.account_id,
                'DashboardId': dashboard_id,
                'IdentityType': 'IAM',
                'SessionLifetimeInMinutes': session_lifetime,
                'UndoRedoDisabled': False,
                'ResetDisabled': False
            }
            
            if user_arn:
                params['UserArn'] = user_arn
            
            response = self.client.get_dashboard_embed_url(**params)
            embed_url = response.get('EmbedUrl')
            
            logger.info(f"🔗 Generated embed URL for dashboard: {dashboard_id}")
            return embed_url
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embed URL for {dashboard_id}: {e}")
            return None
    
    def generate_anonymous_embed_url(self, dashboard_id: str, 
                                     allowed_domains: List[str] = None,
                                     session_lifetime: int = 600) -> Optional[str]:
        """Generate anonymous embed URL (no authentication required)."""
        try:
            experience_config = {
                'Dashboard': {
                    'InitialDashboardId': dashboard_id
                }
            }
            
            params = {
                'AwsAccountId': self.account_id,
                'SessionLifetimeInMinutes': session_lifetime,
                'AuthorizedResourceArns': [
                    f"arn:aws:quicksight:{config.aws_region}:{self.account_id}:dashboard/{dashboard_id}"
                ],
                'ExperienceConfiguration': experience_config
            }
            
            if allowed_domains:
                params['AllowedDomains'] = allowed_domains
            
            response = self.client.generate_embed_url_for_anonymous_user(**params)
            embed_url = response.get('EmbedUrl')
            
            logger.info(f"🔗 Generated anonymous embed URL for dashboard: {dashboard_id}")
            return embed_url
            
        except Exception as e:
            logger.error(f"❌ Failed to generate anonymous embed URL for {dashboard_id}: {e}")
            return None
    
    def list_datasets(self) -> List[Dict]:
        """List all available QuickSight datasets."""
        try:
            datasets = []
            next_token = None
            
            while True:
                if next_token:
                    response = self.client.list_data_sets(
                        AwsAccountId=self.account_id,
                        NextToken=next_token
                    )
                else:
                    response = self.client.list_data_sets(
                        AwsAccountId=self.account_id
                    )
                
                datasets.extend(response.get('DataSetSummaries', []))
                next_token = response.get('NextToken')
                
                if not next_token:
                    break
            
            logger.info(f"📊 Found {len(datasets)} QuickSight datasets")
            return datasets
            
        except Exception as e:
            logger.error(f"❌ Failed to list datasets: {e}")
            return []
    
    def create_dashboard_from_template(self, dashboard_id: str, template_arn: str, 
                                       dashboard_name: str, 
                                       dataset_references: List[Dict]) -> bool:
        """Create a new dashboard from a template."""
        try:
            source_entity = {
                'SourceTemplate': {
                    'DataSetReferences': dataset_references,
                    'Arn': template_arn
                }
            }
            
            response = self.client.create_dashboard(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id,
                Name=dashboard_name,
                SourceEntity=source_entity
            )
            
            if response['CreationStatus'] in ['CREATION_SUCCESSFUL', 'CREATION_IN_PROGRESS']:
                logger.info(f"✅ Dashboard creation initiated: {dashboard_id}")
                return True
            else:
                logger.error(f"❌ Dashboard creation failed: {response}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to create dashboard {dashboard_id}: {e}")
            return False
    
    def import_dashboard_definition(self, dashboard_id: str, save_to_file: bool = True) -> Optional[Dict]:
        """Import/download dashboard definition from QuickSight for LLM analysis."""
        try:
            # Get dashboard basic info
            dashboard_response = self.client.describe_dashboard(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id
            )
            
            # Get detailed dashboard definition
            definition_response = self.client.describe_dashboard_definition(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id
            )
            
            dashboard_data = {
                'dashboard_id': dashboard_id,
                'name': dashboard_response.get('Dashboard', {}).get('Name'),
                'arn': dashboard_response.get('Dashboard', {}).get('Arn'),
                'created_time': str(dashboard_response.get('Dashboard', {}).get('CreatedTime')),
                'last_updated': str(dashboard_response.get('Dashboard', {}).get('LastUpdatedTime')),
                'last_published': str(dashboard_response.get('Dashboard', {}).get('LastPublishedTime')),
                'version_number': dashboard_response.get('Dashboard', {}).get('Version', {}).get('VersionNumber'),
                'status': dashboard_response.get('Dashboard', {}).get('Version', {}).get('Status'),
                'definition': definition_response.get('Definition'),
                'parameters': definition_response.get('Parameters'),
                'dashboard_publish_options': definition_response.get('DashboardPublishOptions'),
                'version_description': definition_response.get('VersionDescription')
            }
            
            if save_to_file:
                filename = f"dashboard_{dashboard_id}_import.json"
                with open(filename, 'w') as f:
                    json.dump(dashboard_data, f, indent=2, default=str)
                logger.info(f"📥 Dashboard imported and saved to: {filename}")
            
            logger.info(f"📥 Successfully imported dashboard: {dashboard_id}")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Failed to import dashboard {dashboard_id}: {e}")
            return None
    
    def export_dashboard_for_llm(self, dashboard_id: str) -> Optional[Dict]:
        """Export dashboard in a format optimized for LLM analysis."""
        try:
            dashboard_data = self.import_dashboard_definition(dashboard_id, save_to_file=False)
            if not dashboard_data:
                return None
            
            # Extract key information for LLM analysis
            llm_optimized = {
                'dashboard_summary': {
                    'id': dashboard_data['dashboard_id'],
                    'name': dashboard_data['name'],
                    'created': dashboard_data['created_time'],
                    'last_updated': dashboard_data['last_updated'],
                    'status': dashboard_data['status']
                },
                'structure': {},
                'visualizations': [],
                'datasets': [],
                'parameters': dashboard_data.get('parameters', []),
                'insights': []
            }
            
            definition = dashboard_data.get('definition', {})
            
            # Extract sheets information
            sheets = definition.get('Sheets', [])
            llm_optimized['structure']['total_sheets'] = len(sheets)
            llm_optimized['structure']['sheets'] = []
            
            for sheet in sheets:
                sheet_info = {
                    'sheet_id': sheet.get('SheetId'),
                    'name': sheet.get('Name'),
                    'visual_count': len(sheet.get('Visuals', [])),
                    'visuals': []
                }
                
                # Extract visual information
                for visual in sheet.get('Visuals', []):
                    visual_info = {
                        'visual_id': visual.get('VisualId'),
                        'type': self._get_visual_type(visual),
                        'title': self._get_visual_title(visual),
                        'subtitle': self._get_visual_subtitle(visual)
                    }
                    sheet_info['visuals'].append(visual_info)
                    llm_optimized['visualizations'].append(visual_info)
                
                llm_optimized['structure']['sheets'].append(sheet_info)
            
            # Extract dataset information
            dataset_declarations = definition.get('DataSetIdentifierDeclarations', [])
            for dataset in dataset_declarations:
                dataset_info = {
                    'identifier': dataset.get('Identifier'),
                    'arn': dataset.get('DataSetArn')
                }
                llm_optimized['datasets'].append(dataset_info)
            
            # Add insights for LLM
            llm_optimized['insights'] = [
                f"Dashboard contains {len(sheets)} sheets with {len(llm_optimized['visualizations'])} total visualizations",
                f"Uses {len(llm_optimized['datasets'])} datasets",
                f"Visual types include: {', '.join(set(v['type'] for v in llm_optimized['visualizations'] if v['type']))}"
            ]
            
            # Save LLM-optimized version
            filename = f"dashboard_{dashboard_id}_llm_analysis.json"
            with open(filename, 'w') as f:
                json.dump(llm_optimized, f, indent=2, default=str)
            
            logger.info(f"🤖 Dashboard exported for LLM analysis: {filename}")
            return llm_optimized
            
        except Exception as e:
            logger.error(f"❌ Failed to export dashboard for LLM: {e}")
            return None
    
    def _get_visual_type(self, visual: Dict) -> str:
        """Extract visual type from visual definition."""
        for key in visual.keys():
            if key.endswith('Visual') and key != 'Visual':
                return key.replace('Visual', '')
        return 'Unknown'
    
    def _get_visual_title(self, visual: Dict) -> str:
        """Extract visual title."""
        for visual_type in visual.values():
            if isinstance(visual_type, dict) and 'Title' in visual_type:
                title_config = visual_type['Title']
                if isinstance(title_config, dict) and 'Visibility' in title_config:
                    if title_config.get('Visibility') == 'VISIBLE':
                        return title_config.get('Text', 'Untitled')
        return 'Untitled'
    
    def _get_visual_subtitle(self, visual: Dict) -> str:
        """Extract visual subtitle."""
        for visual_type in visual.values():
            if isinstance(visual_type, dict) and 'Subtitle' in visual_type:
                subtitle_config = visual_type['Subtitle']
                if isinstance(subtitle_config, dict) and 'Visibility' in subtitle_config:
                    if subtitle_config.get('Visibility') == 'VISIBLE':
                        return subtitle_config.get('Text', '')
        return ''
    
    def export_dashboard_definition(self, dashboard_id: str) -> Optional[Dict]:
        """Export dashboard definition for backup or migration."""
        return self.import_dashboard_definition(dashboard_id, save_to_file=True)
    
    def get_dashboard_permissions(self, dashboard_id: str) -> Optional[Dict]:
        """Get dashboard permissions and sharing settings."""
        try:
            response = self.client.describe_dashboard_permissions(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id
            )
            return response.get('Permissions', [])
        except Exception as e:
            logger.error(f"❌ Failed to get dashboard permissions for {dashboard_id}: {e}")
            return None
    

    
    def generate_howto_documentation(self, dashboard_id: str) -> Optional[str]:
        """Generate comprehensive how-to documentation from dashboard analysis using AI."""
        try:
            import boto3
            import json
            from datetime import datetime
            
            # Check if analysis file exists
            analysis_file = f"dashboard_{dashboard_id}_llm_analysis.json"
            if not os.path.exists(analysis_file):
                logger.error(f"Analysis file not found: {analysis_file}")
                print(f"❌ Please run dashboard analysis first for dashboard {dashboard_id}")
                return None
            
            # Read the analysis file
            with open(analysis_file, 'r') as f:
                dashboard_data = json.load(f)
            
            # Initialize Bedrock client
            client_kwargs = {
                'region_name': config.aws_region,
                'aws_access_key_id': config.aws_access_key_id,
                'aws_secret_access_key': config.aws_secret_access_key
            }
            
            if hasattr(config, 'aws_session_token') and config.aws_session_token:
                client_kwargs['aws_session_token'] = config.aws_session_token
            
            bedrock = boto3.client('bedrock-runtime', **client_kwargs)
            
            # Create hardcoded prompt for how-to documentation
            howto_prompt = """
You are a technical documentation expert specializing in business intelligence dashboards. 

Your task is to create a comprehensive "How-To Guide" for using a QuickSight dashboard based on its technical analysis.

Create documentation that includes:

1. **DASHBOARD OVERVIEW**
   - Purpose and business value
   - Who should use this dashboard
   - Key business questions it answers

2. **GETTING STARTED**
   - How to access the dashboard
   - Initial setup or permissions needed
   - Navigation basics

3. **UNDERSTANDING THE VISUALIZATIONS**
   - Explanation of each chart/visual type
   - What business insights each visual provides
   - How to interpret the data correctly

4. **INTERACTIVE FEATURES**
   - Filters and parameters available
   - How to drill down or explore data
   - Time period selections

5. **BUSINESS USE CASES**
   - Specific scenarios when to use this dashboard
   - Example business decisions it supports
   - Best practices for analysis

6. **TROUBLESHOOTING**
   - Common issues users might face
   - How to refresh data
   - When to contact support

7. **TIPS & BEST PRACTICES**
   - How to get the most value from the dashboard
   - Recommended viewing frequency
   - Key metrics to focus on

Write in a clear, business-friendly tone. Include step-by-step instructions where appropriate.
Make the guide actionable and practical for business users.

Format the output as a complete markdown document ready for publication.
            """
            
            # Prepare the analysis data as context
            dashboard_context = f"""
Dashboard Analysis Data:

**Dashboard Information:**
- Name: {dashboard_data.get('dashboard_summary', {}).get('name', 'Unknown')}
- ID: {dashboard_data.get('dashboard_summary', {}).get('id', 'Unknown')}
- Created: {dashboard_data.get('dashboard_summary', {}).get('created', 'Unknown')}
- Status: {dashboard_data.get('dashboard_summary', {}).get('status', 'Unknown')}

**Structure:**
- Total Sheets: {dashboard_data.get('structure', {}).get('total_sheets', 0)}
- Total Visualizations: {len(dashboard_data.get('visualizations', []))}

**Visualizations:**
{json.dumps(dashboard_data.get('visualizations', []), indent=2)}

**Datasets:**
{json.dumps(dashboard_data.get('datasets', []), indent=2)}

**Parameters:**
{json.dumps(dashboard_data.get('parameters', []), indent=2)}

**Current Insights:**
{chr(10).join(['• ' + insight for insight in dashboard_data.get('insights', [])])}
            """
            
            # Prepare Bedrock request
            messages = [
                {
                    "role": "user",
                    "content": f"{howto_prompt}\n\n{dashboard_context}"
                }
            ]
            
            print("🤖 Generating how-to documentation with AI...")
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": messages,
                "temperature": 0.1
            }
            
            # Call Bedrock
            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
                body=json.dumps(body),
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            documentation = response_body['content'][0]['text']
            
            # Save documentation to file
            doc_filename = f"dashboard_{dashboard_id}_howto_guide.md"
            with open(doc_filename, 'w') as f:
                f.write(documentation)
            
            logger.info(f"📖 How-to documentation generated: {doc_filename}")
            
            return documentation
            
        except Exception as e:
            logger.error(f"❌ Failed to generate how-to documentation: {e}")
            return None
    
    def import_dashboard_from_file(self, file_path: str, new_dashboard_id: str = None, new_dashboard_name: str = None) -> Optional[str]:
        """Import/recreate a dashboard from an exported definition file."""
        if not self.enable_write_operations:
            logger.error("❌ Dashboard import requires write permissions")
            print("❌ Dashboard import disabled - requires write mode")
            print("💡 Use 'Enable Write Mode' option to allow dashboard imports")
            return None
            
        try:
            # Read the dashboard definition file
            if not os.path.exists(file_path):
                logger.error(f"❌ Dashboard definition file not found: {file_path}")
                return None
            
            with open(file_path, 'r') as f:
                dashboard_data = json.load(f)
            
            # Extract necessary information
            original_definition = dashboard_data.get('definition')
            if not original_definition:
                logger.error("❌ No dashboard definition found in file")
                return None
            
            # Generate new dashboard ID if not provided
            if not new_dashboard_id:
                new_dashboard_id = str(uuid.uuid4())
            
            # Use original name if new name not provided
            if not new_dashboard_name:
                new_dashboard_name = dashboard_data.get('name', 'Imported Dashboard')
            
            # Create the dashboard
            response = self.client.create_dashboard(
                AwsAccountId=self.account_id,
                DashboardId=new_dashboard_id,
                Name=new_dashboard_name,
                Definition=original_definition,
                DashboardPublishOptions={
                    'AdHocFilteringOption': {
                        'AvailabilityStatus': 'ENABLED'
                    },
                    'ExportToCSVOption': {
                        'AvailabilityStatus': 'ENABLED'
                    },
                    'SheetControlsOption': {
                        'VisibilityState': 'EXPANDED'
                    }
                }
            )
            
            logger.info(f"✅ Dashboard imported successfully: {new_dashboard_id}")
            logger.info(f"📊 Dashboard name: {new_dashboard_name}")
            logger.info(f"🔄 Status: {response.get('CreationStatus', 'Unknown')}")
            
            return new_dashboard_id
            
        except Exception as e:
            logger.error(f"❌ Failed to import dashboard from file: {e}")
            return None
    
    def import_dashboard_from_account(self, source_account_id: str, source_dashboard_id: str, 
                                    new_dashboard_id: str = None, new_dashboard_name: str = None) -> Optional[str]:
        """Import a dashboard from another AWS account (requires cross-account permissions)."""
        if not self.enable_write_operations:
            logger.error("❌ Cross-account dashboard import requires write permissions")
            print("❌ Cross-account import disabled - requires write mode")
            print("💡 Use 'Enable Write Mode' option to allow dashboard imports")
            return None
            
        try:
            # This requires cross-account permissions to be set up
            if not new_dashboard_id:
                new_dashboard_id = str(uuid.uuid4())
            
            # Try to describe the dashboard from the source account
            response = self.client.describe_dashboard(
                AwsAccountId=source_account_id,
                DashboardId=source_dashboard_id
            )
            
            # Get the dashboard definition
            definition_response = self.client.describe_dashboard_definition(
                AwsAccountId=source_account_id,
                DashboardId=source_dashboard_id
            )
            
            if not new_dashboard_name:
                new_dashboard_name = response.get('Dashboard', {}).get('Name', 'Imported Dashboard')
            
            # Create the dashboard in current account
            create_response = self.client.create_dashboard(
                AwsAccountId=self.account_id,
                DashboardId=new_dashboard_id,
                Name=new_dashboard_name,
                Definition=definition_response.get('Definition'),
                DashboardPublishOptions={
                    'AdHocFilteringOption': {
                        'AvailabilityStatus': 'ENABLED'
                    },
                    'ExportToCSVOption': {
                        'AvailabilityStatus': 'ENABLED'
                    },
                    'SheetControlsOption': {
                        'VisibilityState': 'EXPANDED'
                    }
                }
            )
            
            logger.info(f"✅ Dashboard imported from account {source_account_id}: {new_dashboard_id}")
            return new_dashboard_id
            
        except Exception as e:
            logger.error(f"❌ Failed to import dashboard from account {source_account_id}: {e}")
            return None
    
    def clone_dashboard(self, source_dashboard_id: str, new_dashboard_id: str = None, new_dashboard_name: str = None) -> Optional[str]:
        """Clone an existing dashboard within the same account."""
        if not self.enable_write_operations:
            logger.error("❌ Dashboard cloning requires write permissions")
            print("❌ Dashboard cloning disabled - requires write mode")
            print("💡 Use 'Enable Write Mode' option to allow dashboard operations")
            return None
            
        try:
            # Get the source dashboard definition
            dashboard_data = self.import_dashboard_definition(source_dashboard_id, save_to_file=False)
            if not dashboard_data:
                return None
            
            if not new_dashboard_id:
                new_dashboard_id = str(uuid.uuid4())
            
            if not new_dashboard_name:
                original_name = dashboard_data.get('name', 'Unknown Dashboard')
                new_dashboard_name = f"{original_name} (Clone)"
            
            # Create the cloned dashboard
            response = self.client.create_dashboard(
                AwsAccountId=self.account_id,
                DashboardId=new_dashboard_id,
                Name=new_dashboard_name,
                Definition=dashboard_data.get('definition'),
                DashboardPublishOptions={
                    'AdHocFilteringOption': {
                        'AvailabilityStatus': 'ENABLED'
                    },
                    'ExportToCSVOption': {
                        'AvailabilityStatus': 'ENABLED'
                    },
                    'SheetControlsOption': {
                        'VisibilityState': 'EXPANDED'
                    }
                }
            )
            
            logger.info(f"✅ Dashboard cloned successfully: {new_dashboard_id}")
            logger.info(f"📊 New dashboard name: {new_dashboard_name}")
            
            return new_dashboard_id
            
        except Exception as e:
            logger.error(f"❌ Failed to clone dashboard: {e}")
            return None
    
    def list_importable_files(self) -> List[str]:
        """List available dashboard definition files for import."""
        try:
            definition_files = glob.glob("dashboard_*_import.json")
            return definition_files
        except Exception as e:
            logger.error(f"❌ Failed to list importable files: {e}")
            return []
    
    def smart_dashboard_import(self, dashboard_id: str, new_dashboard_name: str = None) -> Optional[str]:
        """Smart import - try to find and import dashboard from any source."""
        try:
            logger.info(f"🔍 Smart import attempting to find dashboard: {dashboard_id}")
            
            # Step 1: Check if it already exists in current account
            try:
                existing = self.client.describe_dashboard(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id
            )
                print(f"✅ Dashboard {dashboard_id} found in your account!")
                print(f"📊 Name: {existing.get('Dashboard', {}).get('Name', 'Unknown')}")
                print(f"📋 Status: {existing.get('Dashboard', {}).get('Version', {}).get('Status', 'Unknown')}")
                print(f"💡 This dashboard is accessible for analysis")
                return dashboard_id  # Return the ID to indicate it's accessible
            except Exception as e:
                if "ResourceNotFoundException" not in str(e):
                    logger.error(f"Error checking existing dashboard: {e}")
                    return None
                pass  # Dashboard doesn't exist in current account, continue
            
            # Step 1.5: Check if it's accessible via shared/search functionality
            try:
                search_response = self.client.search_dashboards(
                    AwsAccountId=self.account_id,
                    Filters=[
                        {
                            'Name': 'DASHBOARD_NAME',
                            'Operator': 'StringLike',
                            'Value': '%'  # Search for dashboards with any name
                        }
                    ]
                )
                shared_dashboards = search_response.get('DashboardSummaryList', [])
                for shared_dash in shared_dashboards:
                    if shared_dash.get('DashboardId') == dashboard_id:
                        print(f"✅ Dashboard {dashboard_id} found as shared/accessible dashboard!")
                        print(f"📊 Name: {shared_dash.get('Name', 'Unknown')}")
                        print(f"🌐 Source: Shared with your account")
                        print(f"💡 This dashboard is accessible for analysis")
                        return dashboard_id
            except Exception as e:
                logger.warning(f"Could not search for shared dashboard: {e}")
                pass
            
            # Step 2: Check if we have an export file for this dashboard
            export_file = f"dashboard_{dashboard_id}_import.json"
            if os.path.exists(export_file):
                print(f"📁 Found export file: {export_file}")
                print(f"🔄 Importing from file...")
                return self.import_dashboard_from_file(export_file, new_dashboard_name=new_dashboard_name)
            
            # Step 3: Try to help user get what they need
            print(f"❌ Dashboard {dashboard_id} not found in your account ({self.account_id})")
            print(f"❌ No export file found: {export_file}")
            print()
            
            # Ask if user wants to try cross-account import
            print("🤔 Let's try to import this dashboard anyway!")
            print()
            print("Option 1: Try Cross-Account Import")
            print("If you know the source AWS account ID, I can try to import it directly.")
            try_cross_account = input("Do you have the source AWS account ID? (y/n): ").strip().lower()
            
            if try_cross_account in ['y', 'yes']:
                source_account = input("Enter the source AWS account ID (12 digits): ").strip()
                if len(source_account) == 12 and source_account.isdigit():
                    print(f"\n🔄 Attempting cross-account import from {source_account}...")
                    result = self.import_dashboard_from_account(
                        source_account, 
                        dashboard_id,
                        new_dashboard_name=new_dashboard_name
                    )
                    if result:
                        print(f"✅ Success! Dashboard imported with ID: {result}")
                        return result
                    else:
                        print("❌ Cross-account import failed (likely permissions issue)")
                else:
                    print("❌ Invalid account ID format (must be 12 digits)")
            else:
                print("⚠️ Skipping cross-account import")
            
            print()
            print("Option 2: Create Dashboard Definition File")
            create_file = input("Create a dashboard definition file for this ID? (y/n): ").strip().lower()
            
            if create_file in ['y', 'yes']:
                placeholder_name = new_dashboard_name or f"Dashboard {dashboard_id}"
                result = self._create_dashboard_definition_file(dashboard_id, placeholder_name)
                if result:
                    print(f"✅ Created dashboard definition file: {result}")
                    print("💡 You can now use 'Import from file' to create this dashboard when you have write permissions")
                    return dashboard_id  # Return original ID as reference
            
            print()
            print("💡 Other options:")
            print("• Ask the dashboard owner to export it as a file")
            print("• Use the 'Import from another account' option with the correct account ID")
            print("• Verify the dashboard ID is correct")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Smart import failed: {e}")
            return None
    
    def extract_dashboard_id_from_url(self, url_or_id: str) -> str:
        """Extract dashboard ID from QuickSight URL or return ID if already clean."""
        try:
            # If it's already a clean dashboard ID (UUID format), return it
            if len(url_or_id) == 36 and url_or_id.count('-') == 4:
                return url_or_id
            
            # Try to extract from QuickSight URL patterns
            # Pattern: https://quicksight.aws.amazon.com/sn/dashboards/DASHBOARD_ID
            url_pattern = r'/dashboards/([a-f0-9-]{36})'
            match = re.search(url_pattern, url_or_id)
            if match:
                return match.group(1)
            
            # Pattern: dashboard/DASHBOARD_ID
            simple_pattern = r'dashboard[/:]([a-f0-9-]{36})'
            match = re.search(simple_pattern, url_or_id, re.IGNORECASE)
            if match:
                return match.group(1)
            
            # If nothing matches, return original input
            return url_or_id
            
        except Exception as e:
            logger.error(f"Failed to extract dashboard ID: {e}")
            return url_or_id
    
    def extract_account_id_from_url(self, url: str) -> Optional[str]:
        """Extract AWS account ID from QuickSight URL."""
        try:
            # Pattern for account ID in QuickSight URLs
            # Example: https://us-west-2.quicksight.aws.amazon.com/sn/accounts/123456789012/dashboards/...
            account_pattern = r'/accounts/(\d{12})/'
            match = re.search(account_pattern, url)
            if match:
                return match.group(1)
            
            # Alternative pattern for direct account URLs
            # Example: https://quicksight.aws.amazon.com/sn/123456789012/dashboards/...
            alt_pattern = r'/sn/(\d{12})/'
            match = re.search(alt_pattern, url)
            if match:
                return match.group(1)
                
            return None
        except Exception as e:
            logger.error(f"Failed to extract account ID from URL: {e}")
            return None
    
    def analyze_dashboard_by_url(self, dashboard_url: str) -> Optional[str]:
        """Analyze a dashboard by its public/embed URL."""
        try:
            print(f"🌐 Attempting to analyze dashboard from URL: {dashboard_url}")
            
            # Extract dashboard ID from URL if possible
            dashboard_id = self.extract_dashboard_id_from_url(dashboard_url)
            
            if dashboard_id and dashboard_id != dashboard_url:
                print(f"🔍 Extracted dashboard ID: {dashboard_id}")
                
                # Try multiple approaches to access the dashboard
                
                # Approach 1: Try current account
                try:
                    existing = self.client.describe_dashboard(
                        AwsAccountId=self.account_id,
                        DashboardId=dashboard_id
                    )
                    print(f"✅ Dashboard accessible in your account!")
                    print(f"📊 Name: {existing.get('Dashboard', {}).get('Name', 'Unknown')}")
                    return dashboard_id
                except Exception as e:
                    if "ResourceNotFoundException" not in str(e):
                        logger.error(f"Unexpected error accessing dashboard: {e}")
                        return None
                
                # Approach 2: Try to extract account ID from URL
                account_id_from_url = self.extract_account_id_from_url(dashboard_url)
                if account_id_from_url and account_id_from_url != self.account_id:
                    print(f"🔍 Detected source account from URL: {account_id_from_url}")
                    try:
                        cross_account = self.client.describe_dashboard(
                            AwsAccountId=account_id_from_url,
                            DashboardId=dashboard_id
                        )
                        print(f"✅ Dashboard found in source account!")
                        print(f"📊 Name: {cross_account.get('Dashboard', {}).get('Name', 'Unknown')}")
                        print(f"⚠️ Note: Cross-account access - you may need specific permissions")
                        return dashboard_id
                    except Exception as cross_e:
                        print(f"❌ Cannot access dashboard from account {account_id_from_url}")
                        print(f"💡 You may need the dashboard owner to grant you access")
                
                # Approach 3: Public/embedded dashboard guidance
                if "embed" in dashboard_url.lower():
                    print(f"🔍 This appears to be an embedded dashboard URL")
                    print(f"💡 Embedded dashboards may have different access patterns")
                    print(f"💡 Try asking the dashboard owner for direct access")
                else:
                    print(f"⚠️ Dashboard exists but not accessible with current permissions")
                    print(f"💡 Possible solutions:")
                    print(f"  • Ask dashboard owner to share with your account ({self.account_id})")
                    print(f"  • Request cross-account access permissions")
                    print(f"  • Use an export file if available")
                
                return None
            else:
                print(f"⚠️ Could not extract dashboard ID from URL")
                print(f"💡 This might be:")
                print(f"  • An embedded dashboard requiring special access")
                print(f"  • A public dashboard with restricted API access")
                print(f"  • An invalid or malformed URL")
                return None
                
        except Exception as e:
            logger.error(f"Failed to analyze dashboard by URL: {e}")
            return None
    
    def _create_dashboard_definition_file(self, dashboard_id: str, dashboard_name: str) -> Optional[str]:
        """Create a placeholder dashboard definition file when original is not available."""
        try:
            # Create a simple placeholder dashboard definition
            placeholder_data = {
                'dashboard_id': dashboard_id,
                'name': dashboard_name,
                'arn': f"arn:aws:quicksight:us-west-2:{self.account_id}:dashboard/{dashboard_id}",
                'created_time': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'last_published': datetime.now().isoformat(),
                'version_number': 1,
                'status': 'CREATION_SUCCESSFUL',
                'definition': {
                "Sheets": [
                    {
                            "SheetId": f"{dashboard_id}_sheet_1",
                            "Name": "Placeholder Sheet",
                        "Visuals": [
                            {
                                "BarChartVisual": {
                                        "VisualId": f"{dashboard_id}_visual_1",
                                    "Title": {
                                        "Visibility": "VISIBLE",
                                            "Text": "Placeholder Chart"
                                        },
                                        "Subtitle": {
                                        "Visibility": "VISIBLE",
                                            "Text": f"This is a placeholder for dashboard {dashboard_id}"
                                        }
                                    }
                                }
                            ]
                        }
                    ],
                    "DataSetIdentifierDeclarations": [],
                    "ParameterDeclarations": []
                },
                'parameters': [],
                'dashboard_publish_options': {
                    'AdHocFilteringOption': {
                        'AvailabilityStatus': 'ENABLED'
                    },
                    'ExportToCSVOption': {
                        'AvailabilityStatus': 'ENABLED'
                    },
                    'SheetControlsOption': {
                        'VisibilityState': 'EXPANDED'
                    }
                },
                'version_description': f'Placeholder definition for dashboard {dashboard_id}'
            }
            
            # Save to file
            filename = f"dashboard_{dashboard_id}_import.json"
            with open(filename, 'w') as f:
                json.dump(placeholder_data, f, indent=2, default=str)
            
            logger.info(f"✅ Dashboard definition file created: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Failed to create dashboard definition file: {e}")
            return None
    
    def analyze_dashboard_screenshot(self, image_path: str) -> Optional[str]:
        """Analyze a dashboard screenshot using AI vision capabilities."""
        try:
            logger.info(f"🖼️ Analyzing dashboard screenshot: {image_path}")
            
            # Check if file exists
            if not os.path.exists(image_path):
                print(f"❌ Image file not found: {image_path}")
                return None
            
            # Check file extension
            valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext not in valid_extensions:
                print(f"❌ Unsupported image format: {file_ext}")
                print(f"💡 Supported formats: {', '.join(valid_extensions)}")
                return None
            
            # Read and encode image
            print("📖 Reading image file...")
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Determine media type
            media_type_map = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg', 
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            media_type = media_type_map.get(file_ext, 'image/jpeg')
            
            # Prepare AI analysis prompt
            analysis_prompt = """
You are an expert business intelligence analyst specializing in dashboard analysis.

Analyze this QuickSight dashboard screenshot and provide comprehensive insights.

Please provide a detailed analysis covering:

1. **DASHBOARD OVERVIEW**
   - Dashboard title and purpose (if visible)
   - Overall layout and design
   - Number of visualizations present

2. **VISUALIZATION ANALYSIS**
   - Type of each chart/visualization (bar charts, line charts, pie charts, tables, etc.)
   - Data being displayed in each visualization
   - Key metrics and KPIs visible
   - Time periods or date ranges shown

3. **DATA INSIGHTS**
   - What business domain this dashboard covers (sales, finance, operations, etc.)
   - Key trends or patterns visible in the data
   - Notable data points or outliers
   - Performance indicators (positive/negative trends)

4. **INTERACTIVE ELEMENTS**
   - Filters, dropdowns, or parameter controls visible
   - Navigation elements or drill-down capabilities
   - Time period selectors

5. **BUSINESS VALUE**
   - What business questions this dashboard answers
   - Who would typically use this dashboard (executives, analysts, managers)
   - Key decisions this dashboard could inform

6. **TECHNICAL OBSERVATIONS**
   - Data quality and completeness visible
   - Dashboard responsiveness indicators
   - Any error messages or data issues

7. **RECOMMENDATIONS**
   - Suggestions for dashboard improvement
   - Additional visualizations that could be helpful
   - Data exploration opportunities

Please be specific and detailed in your analysis. Focus on actionable insights that would help someone understand and use this dashboard effectively.

Format your response as a structured analysis that could be used for documentation or training purposes.
            """
            
            # Initialize Bedrock client
            bedrock = boto3.client(
                'bedrock-runtime',
                region_name=config.aws_region,
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key,
                aws_session_token=getattr(config, 'aws_session_token', None)
            )
            
            # Prepare Bedrock request with image
            print("🤖 Analyzing screenshot with AI vision...")
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": analysis_prompt
                        }
                    ]
                }
            ]
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": messages,
                "temperature": 0.1
            }
            
            # Call Bedrock with vision model
            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
                body=json.dumps(body),
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            analysis_text = response_body['content'][0]['text']
            
            # Generate filename based on image name and timestamp
            image_basename = os.path.splitext(os.path.basename(image_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"screenshot_analysis_{image_basename}_{timestamp}.md"
            
            # Save analysis to markdown file
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(f"# Dashboard Screenshot Analysis\n\n")
                f.write(f"**Image Source:** {image_path}\n")
                f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Image Format:** {media_type}\n\n")
                f.write("---\n\n")
                f.write(analysis_text)
            
            logger.info(f"✅ Screenshot analysis saved to: {output_filename}")
            print(f"📄 Analysis saved to: {output_filename}")
            
            # Also show a preview of key insights
            if "DASHBOARD OVERVIEW" in analysis_text.upper() or "KEY" in analysis_text.upper():
                print("\n🔍 Quick Preview:")
                lines = analysis_text.split('\n')
                preview_lines = []
                for line in lines[:10]:  # Show first 10 lines as preview
                    if line.strip():
                        preview_lines.append(f"  {line}")
                        if len(preview_lines) >= 5:  # Limit preview
                            break
                
                for line in preview_lines:
                    print(line)
                print("  ...")
                print(f"\n📖 See full analysis in: {output_filename}")
            
            return output_filename
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze screenshot: {e}")
            print(f"❌ Screenshot analysis failed: {e}")
            return None
