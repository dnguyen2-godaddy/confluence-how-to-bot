"""
QuickSight Dashboard Management for GoCaas Integration
"""

import boto3
import json
import logging
from typing import Dict, List, Optional
from utils.config import config

logger = logging.getLogger(__name__)


class QuickSightManager:
    """Manages QuickSight dashboards and data sources for GoCaas analysis."""
    
    def __init__(self):
        """Initialize QuickSight client."""
        self.quicksight = boto3.client('quicksight', region_name='us-west-2')
        self.account_id = boto3.client('sts').get_caller_identity()['Account']
        
    def create_redshift_data_source(self) -> str:
        """Create a Redshift data source in QuickSight."""
        data_source_id = 'confluence-bot-redshift-source'
        
        try:
            response = self.quicksight.create_data_source(
                AwsAccountId=self.account_id,
                DataSourceId=data_source_id,
                Name='Confluence Bot Redshift Data',
                Type='REDSHIFT',
                DataSourceParameters={
                    'RedshiftParameters': {
                        'Host': config.redshift_host,
                        'Port': config.redshift_port,
                        'Database': config.redshift_database
                    }
                },
                Credentials={
                    'CredentialPair': {
                        'Username': config.redshift_user,
                        'Password': config.redshift_password
                    }
                },
                Permissions=[
                    {
                        'Principal': f'arn:aws:quicksight:us-west-2:{self.account_id}:user/default/{config.redshift_user}',
                        'Actions': [
                            'quicksight:UpdateDataSourcePermissions',
                            'quicksight:DescribeDataSource',
                            'quicksight:DescribeDataSourcePermissions',
                            'quicksight:PassDataSource',
                            'quicksight:UpdateDataSource',
                            'quicksight:DeleteDataSource'
                        ]
                    }
                ]
            )
            logger.info(f"Created QuickSight data source: {data_source_id}")
            return data_source_id
            
        except Exception as e:
            logger.error(f"Failed to create data source: {e}")
            raise
    
    def create_scorecard_dataset(self, data_source_id: str) -> str:
        """Create a dataset from the scorecard query."""
        dataset_id = 'scorecard-metrics-dataset'
        
        try:
            response = self.quicksight.create_data_set(
                AwsAccountId=self.account_id,
                DataSetId=dataset_id,
                Name='Scorecard Metrics Dataset',
                PhysicalTableMap={
                    'scorecard-table': {
                        'RelationalTable': {
                            'DataSourceArn': f'arn:aws:quicksight:us-west-2:{self.account_id}:datasource/{data_source_id}',
                            'Schema': 'ba_corporate',
                            'Name': 'scorecard_test_dn',
                            'InputColumns': [
                                {'Name': 'metric_report_mst_month', 'Type': 'DATETIME'},
                                {'Name': 'entry_type', 'Type': 'STRING'},
                                {'Name': 'business_unit', 'Type': 'STRING'},
                                {'Name': 'metric_name', 'Type': 'STRING'},
                                {'Name': 'region_name', 'Type': 'STRING'},
                                {'Name': 'higher_is_better', 'Type': 'INTEGER'},
                                {'Name': 'metric_value', 'Type': 'DECIMAL'}
                            ]
                        }
                    }
                },
                ImportMode='SPICE'
            )
            logger.info(f"Created QuickSight dataset: {dataset_id}")
            return dataset_id
            
        except Exception as e:
            logger.error(f"Failed to create dataset: {e}")
            raise
    
    def create_scorecard_dashboard(self, dataset_id: str) -> str:
        """Create a dashboard with scorecard visualizations."""
        dashboard_id = 'scorecard-dashboard'
        
        # Dashboard definition with multiple visualizations
        dashboard_definition = {
            "DataSetIdentifierDeclarations": [
                {
                    "DataSetArn": f"arn:aws:quicksight:us-west-2:{self.account_id}:dataset/{dataset_id}",
                    "Identifier": "scorecard_dataset"
                }
            ],
            "Sheets": [
                {
                    "SheetId": "scorecard-overview",
                    "Name": "Scorecard Overview",
                    "Visuals": [
                        {
                            "BarChartVisual": {
                                "VisualId": "metrics-by-region",
                                "Title": {"Visibility": "VISIBLE", "Label": "Metrics by Region"},
                                "FieldWells": {
                                    "BarChartAggregatedFieldWells": {
                                        "Category": [{"CategoricalDimensionField": {"FieldId": "region_name", "Column": {"DataSetIdentifier": "scorecard_dataset", "ColumnName": "region_name"}}}],
                                        "Values": [{"NumericalMeasureField": {"FieldId": "metric_value", "Column": {"DataSetIdentifier": "scorecard_dataset", "ColumnName": "metric_value"}, "AggregationFunction": {"SimpleNumericalAggregation": "SUM"}}}]
                                    }
                                }
                            }
                        },
                        {
                            "LineChartVisual": {
                                "VisualId": "metrics-trend",
                                "Title": {"Visibility": "VISIBLE", "Label": "Metrics Trend Over Time"},
                                "FieldWells": {
                                    "LineChartAggregatedFieldWells": {
                                        "Category": [{"DateDimensionField": {"FieldId": "metric_month", "Column": {"DataSetIdentifier": "scorecard_dataset", "ColumnName": "metric_report_mst_month"}}}],
                                        "Values": [{"NumericalMeasureField": {"FieldId": "metric_value", "Column": {"DataSetIdentifier": "scorecard_dataset", "ColumnName": "metric_value"}, "AggregationFunction": {"SimpleNumericalAggregation": "SUM"}}}],
                                        "Colors": [{"CategoricalDimensionField": {"FieldId": "metric_name", "Column": {"DataSetIdentifier": "scorecard_dataset", "ColumnName": "metric_name"}}}]
                                    }
                                }
                            }
                        }
                    ]
                }
            ]
        }
        
        try:
            response = self.quicksight.create_dashboard(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id,
                Name='Scorecard Metrics Dashboard',
                Definition=dashboard_definition,
                Permissions=[
                    {
                        'Principal': f'arn:aws:quicksight:us-west-2:{self.account_id}:user/default/{config.redshift_user}',
                        'Actions': [
                            'quicksight:DescribeDashboard',
                            'quicksight:ListDashboardVersions',
                            'quicksight:UpdateDashboardPermissions',
                            'quicksight:QueryDashboard',
                            'quicksight:UpdateDashboard',
                            'quicksight:DeleteDashboard',
                            'quicksight:DescribeDashboardPermissions',
                            'quicksight:ExportToCsv'
                        ]
                    }
                ]
            )
            logger.info(f"Created QuickSight dashboard: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            raise
    
    def get_dashboard_embed_url(self, dashboard_id: str) -> str:
        """Get embeddable URL for the dashboard."""
        try:
            response = self.quicksight.get_dashboard_embed_url(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id,
                IdentityType='IAM',
                SessionLifetimeInMinutes=600,  # 10 hours
                UndoRedoDisabled=False,
                ResetDisabled=False
            )
            return response['EmbedUrl']
            
        except Exception as e:
            logger.error(f"Failed to get embed URL: {e}")
            raise
    
    def export_dashboard_data(self, dashboard_id: str) -> Dict:
        """Export dashboard data for GoCaas analysis."""
        try:
            # Get dashboard description
            dashboard_response = self.quicksight.describe_dashboard(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id
            )
            
            # Extract key metrics and visualizations
            dashboard_data = {
                'dashboard_id': dashboard_id,
                'name': dashboard_response['Dashboard']['Name'],
                'created_time': dashboard_response['Dashboard']['CreatedTime'].isoformat(),
                'last_updated': dashboard_response['Dashboard']['LastUpdatedTime'].isoformat(),
                'version': dashboard_response['Dashboard']['Version'],
                'embed_url': self.get_dashboard_embed_url(dashboard_id),
                'data_sets': []
            }
            
            logger.info(f"Exported dashboard data for: {dashboard_id}")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to export dashboard data: {e}")
            raise