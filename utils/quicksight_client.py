#!/usr/bin/env python3
"""
QuickSight API Client

A comprehensive client for interacting with AWS QuickSight API to fetch dashboard metadata,
datasets, and other information directly from the service.
"""

import boto3
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


class QuickSightClient:
    """Client for interacting with AWS QuickSight API."""
    
    def __init__(self, region_name: str = 'us-west-2', profile_name: Optional[str] = None):
        """
        Initialize QuickSight client.
        
        Args:
            region_name: AWS region for QuickSight service
            profile_name: AWS profile name to use (for SSO/credential management)
        """
        self.region_name = region_name
        self.profile_name = profile_name
        self.client = None
        self.account_id = None
        
        try:
            self._initialize_client()
            self._get_account_id()
        except Exception as e:
            logger.error(f"Failed to initialize QuickSight client: {e}")
            raise
    
    def _initialize_client(self):
        """Initialize the QuickSight boto3 client."""
        try:
            if self.profile_name:
                session = boto3.Session(profile_name=self.profile_name)
                self.client = session.client('quicksight', region_name=self.region_name)
                logger.info(f"Using AWS profile: {self.profile_name}")
            else:
                self.client = boto3.client('quicksight', region_name=self.region_name)
                logger.info("Using default AWS credentials")
        except NoCredentialsError:
            logger.error("No AWS credentials found. Please configure your AWS credentials.")
            raise
        except Exception as e:
            logger.error(f"Failed to create QuickSight client: {e}")
            raise
    
    def _get_account_id(self):
        """Get the AWS account ID from STS."""
        try:
            if self.profile_name:
                session = boto3.Session(profile_name=self.profile_name)
                sts_client = session.client('sts', region_name=self.region_name)
            else:
                sts_client = boto3.client('sts', region_name=self.region_name)
            
            response = sts_client.get_caller_identity()
            self.account_id = response['Account']
            logger.info(f"Using AWS Account ID: {self.account_id}")
        except Exception as e:
            logger.error(f"Failed to get AWS account ID: {e}")
            raise
    
    def list_dashboards(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        List all dashboards in the account.
        
        Args:
            max_results: Maximum number of results to return
            
        Returns:
            List of dashboard information dictionaries
        """
        try:
            response = self.client.list_dashboards(
                AwsAccountId=self.account_id,
                MaxResults=max_results
            )
            
            dashboards = response.get('DashboardSummaryList', [])
            logger.info(f"Found {len(dashboards)} dashboards")
            
            return dashboards
        except ClientError as e:
            logger.error(f"Failed to list dashboards: {e}")
            return []
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific dashboard.
        
        Args:
            dashboard_id: The ID of the dashboard to retrieve
            
        Returns:
            Dashboard information dictionary or None if not found
        """
        try:
            response = self.client.describe_dashboard(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id
            )
            
            dashboard = response.get('Dashboard', {})
            logger.info(f"Retrieved dashboard: {dashboard.get('Name', dashboard_id)}")
            
            return dashboard
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning(f"Dashboard {dashboard_id} not found")
            else:
                logger.error(f"Failed to get dashboard {dashboard_id}: {e}")
            return None
    
    def get_dashboard_definition(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the dashboard definition (JSON structure) for a specific dashboard.
        
        Args:
            dashboard_id: The ID of the dashboard to retrieve
            
        Returns:
            Dashboard definition dictionary or None if not found
        """
        try:
            response = self.client.describe_dashboard_definition(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id
            )
            
            definition = response.get('Definition', {})
            logger.info(f"Retrieved dashboard definition for: {dashboard_id}")
            
            return definition
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning(f"Dashboard definition for {dashboard_id} not found")
            else:
                logger.error(f"Failed to get dashboard definition for {dashboard_id}: {e}")
            return None
    
    def list_datasets(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        List all datasets in the account.
        
        Args:
            max_results: Maximum number of results to return
            
        Returns:
            List of dataset information dictionaries
        """
        try:
            response = self.client.list_data_sets(
                AwsAccountId=self.account_id,
                MaxResults=max_results
            )
            
            datasets = response.get('DataSetSummaries', [])
            logger.info(f"Found {len(datasets)} datasets")
            
            return datasets
        except ClientError as e:
            logger.error(f"Failed to list datasets: {e}")
            return []
    
    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific dataset.
        
        Args:
            dataset_id: The ID of the dataset to retrieve
            
        Returns:
            Dataset information dictionary or None if not found
        """
        try:
            response = self.client.describe_data_set(
                AwsAccountId=self.account_id,
                DataSetId=dataset_id
            )
            
            dataset = response.get('DataSet', {})
            logger.info(f"Retrieved dataset: {dataset.get('Name', dataset_id)}")
            
            return dataset
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning(f"Dataset {dataset_id} not found")
            else:
                logger.error(f"Failed to get dataset {dataset_id}: {e}")
            return None
    
    def get_data_source(self, data_source_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific data source.
        
        Args:
            data_source_id: The ID of the data source to retrieve
            
        Returns:
            Data source information dictionary or None if not found
        """
        try:
            response = self.client.describe_data_source(
                AwsAccountId=self.account_id,
                DataSourceId=data_source_id
            )
            
            data_source = response.get('DataSource', {})
            logger.info(f"Retrieved data source: {data_source.get('Name', data_source_id)}")
            
            return data_source
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning(f"Data source {data_source_id} not found")
            else:
                logger.error(f"Failed to get data source {data_source_id}: {e}")
            return None
    
    def search_dashboards(self, keyword: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Search for dashboards by keyword in name or description.
        
        Args:
            keyword: Keyword to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of matching dashboard information dictionaries
        """
        try:
            # First get all dashboards
            all_dashboards = self.list_dashboards(max_results=1000)
            
            # Filter by keyword (case-insensitive)
            keyword_lower = keyword.lower()
            matching_dashboards = []
            
            for dashboard in all_dashboards:
                name = dashboard.get('Name', '').lower()
                if keyword_lower in name:
                    matching_dashboards.append(dashboard)
            
            logger.info(f"Found {len(matching_dashboards)} dashboards matching '{keyword}'")
            return matching_dashboards[:max_results]
            
        except Exception as e:
            logger.error(f"Failed to search dashboards: {e}")
            return []
    
    def get_dashboard_metadata_summary(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a comprehensive metadata summary for a dashboard.
        
        Args:
            dashboard_id: The ID of the dashboard to analyze
            
        Returns:
            Metadata summary dictionary or None if not found
        """
        try:
            # Get dashboard details
            dashboard = self.get_dashboard(dashboard_id)
            if not dashboard:
                return None
            
            # Get dashboard definition
            definition = self.get_dashboard_definition(dashboard_id)
            
            # Get dataset information
            dataset_ids = set()
            if definition and 'DataSetIdentifierDeclarations' in definition:
                for dataset_decl in definition['DataSetIdentifierDeclarations']:
                    dataset_ids.add(dataset_decl['Identifier'])
            
            datasets_info = []
            for dataset_id in dataset_ids:
                dataset = self.get_dataset(dataset_id)
                if dataset:
                    datasets_info.append({
                        'id': dataset_id,
                        'name': dataset.get('Name', 'Unknown'),
                        'type': dataset.get('DataSetType', 'Unknown'),
                        'created_time': dataset.get('CreatedTime'),
                        'last_updated_time': dataset.get('LastUpdatedTime')
                    })
            
            # Compile metadata summary
            metadata_summary = {
                'dashboard_id': dashboard_id,
                'name': dashboard.get('Name', 'Unknown'),
                'version': dashboard.get('Version', {}).get('VersionNumber', 0),
                'created_time': dashboard.get('CreatedTime'),
                'last_updated_time': dashboard.get('LastUpdatedTime'),
                'last_published_time': dashboard.get('LastPublishedTime'),
                'status': dashboard.get('DashboardPublishOptions', {}).get('AdHocFilteringOption', {}).get('AvailabilityStatus', 'Unknown'),
                'sheets_count': len(definition.get('Sheets', [])) if definition else 0,
                'datasets': datasets_info,
                'permissions': dashboard.get('Permissions', []),
                'tags': dashboard.get('Tags', []),
                'theme_arn': dashboard.get('ThemeArn'),
                'source_entity_arn': dashboard.get('SourceEntityArn')
            }
            
            logger.info(f"Generated metadata summary for dashboard: {dashboard.get('Name', dashboard_id)}")
            return metadata_summary
            
        except Exception as e:
            logger.error(f"Failed to generate metadata summary for dashboard {dashboard_id}: {e}")
            return None
    
    def export_dashboard_metadata(self, dashboard_id: str, output_file: Optional[str] = None) -> Optional[str]:
        """
        Export dashboard metadata to a JSON file.
        
        Args:
            dashboard_id: The ID of the dashboard to export
            output_file: Output file path (optional, will generate if not provided)
            
        Returns:
            Path to the exported file or None if failed
        """
        try:
            metadata = self.get_dashboard_metadata_summary(dashboard_id)
            if not metadata:
                return None
            
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"outputs/quicksight_metadata_{dashboard_id}_{timestamp}.json"
            
            # Ensure output directory exists
            import os
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Export to JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Exported dashboard metadata to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to export dashboard metadata: {e}")
            return None


def main():
    """Example usage of the QuickSight client."""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Initialize client
    region = os.getenv('AWS_REGION', 'us-west-2')
    profile = os.getenv('AWS_PROFILE')
    
    try:
        client = QuickSightClient(region_name=region, profile_name=profile)
        
        # List all dashboards
        print("Listing all dashboards...")
        dashboards = client.list_dashboards()
        
        if dashboards:
            print(f"\nFound {len(dashboards)} dashboards:")
            for dashboard in dashboards[:5]:  # Show first 5
                print(f"- {dashboard.get('Name', 'Unknown')} (ID: {dashboard.get('DashboardId', 'Unknown')})")
            
            # Get metadata for first dashboard
            first_dashboard_id = dashboards[0]['DashboardId']
            print(f"\nGetting metadata for first dashboard: {dashboards[0].get('Name', 'Unknown')}")
            
            metadata = client.get_dashboard_metadata_summary(first_dashboard_id)
            if metadata:
                print(f"Dashboard has {metadata.get('sheets_count', 0)} sheets and {len(metadata.get('datasets', []))} datasets")
                
                # Export metadata
                output_file = client.export_dashboard_metadata(first_dashboard_id)
                if output_file:
                    print(f"Metadata exported to: {output_file}")
        else:
            print("No dashboards found or failed to list dashboards")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
