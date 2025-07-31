"""
QuickSight Manager for Dashboard Creation and Management

This module provides functionality to create and manage QuickSight dashboards,
data sources, and datasets programmatically.
"""

import boto3
import json
import logging
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
from utils.config import config

logger = logging.getLogger(__name__)


class QuickSightManager:
    """Manages QuickSight dashboards, data sources, and datasets."""
    
    def __init__(self):
        """Initialize QuickSight client and get AWS account ID."""
        try:
            # Validate AWS configuration
            if not config.validate_aws_config():
                raise ValueError("AWS configuration is incomplete. Please check your .env file for AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.")
            
            # Initialize AWS clients
            self.quicksight = boto3.client(
                'quicksight',
                region_name=config.aws_region,
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key
            )
            
            sts_client = boto3.client(
                'sts',
                region_name=config.aws_region,
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key
            )
            
            self.account_id = sts_client.get_caller_identity()['Account']
            logger.info(f"Initialized QuickSight manager for account: {self.account_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize QuickSight manager: {e}")
            raise
    
    def create_redshift_data_source(self, data_source_id: str = None) -> str:
        """
        Create a Redshift data source in QuickSight.
        
        Args:
            data_source_id: Optional custom data source ID
            
        Returns:
            The created data source ID
        """
        if not data_source_id:
            data_source_id = 'confluence-bot-redshift-source'
        
        try:
            # Validate Redshift configuration
            if not config.validate_redshift_config():
                raise ValueError("Redshift configuration is incomplete. Please check your .env file.")
            
            response = self.quicksight.create_data_source(
                AwsAccountId=self.account_id,
                DataSourceId=data_source_id,
                Name='Confluence Bot - Redshift Data Source',
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
                SslProperties={
                    'DisableSsl': False  # Enable SSL for security
                }
            )
            
            logger.info(f"Created QuickSight data source: {data_source_id}")
            return data_source_id
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceExistsException':
                logger.info(f"Data source {data_source_id} already exists")
                return data_source_id
            else:
                logger.error(f"Failed to create data source: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to create data source: {e}")
            raise
    
    def create_scorecard_dataset(self, data_source_id: str, dataset_id: str = None) -> str:
        """
        Create a dataset from the scorecard query.
        
        Args:
            data_source_id: The Redshift data source ID
            dataset_id: Optional custom dataset ID
            
        Returns:
            The created dataset ID
        """
        if not dataset_id:
            dataset_id = 'scorecard-metrics-dataset'
        
        try:
            # Define the custom SQL query from your query_redshift.py
            scorecard_query = """
            SELECT 
              TO_CHAR(metric_report_mst_month, 'MM-YYYY') AS metric_report_mst_month,
              entry_type,
              business_unit, 
              metric_name, 
              region_name, 
              CASE 
                WHEN higher_is_better = 1 THEN 'true'
                WHEN higher_is_better = 0 THEN 'false'
                ELSE NULL
              END AS higher_is_better,
              SUM(metric_value) AS metric_value
            FROM ba_corporate.scorecard_test_dn
            WHERE metric_report_mst_month >= '2025-01-01'
            AND business_unit = 'CARE & SERVICES'
            GROUP BY 
              metric_report_mst_month,
              entry_type,
              business_unit, 
              metric_name, 
              region_name, 
              higher_is_better
            ORDER BY 
              metric_report_mst_month,
              business_unit
            """
            
            response = self.quicksight.create_data_set(
                AwsAccountId=self.account_id,
                DataSetId=dataset_id,
                Name='Scorecard Metrics Dataset',
                PhysicalTableMap={
                    'scorecard-table': {
                        'CustomSql': {
                            'DataSourceArn': f'arn:aws:quicksight:{config.aws_region}:{self.account_id}:datasource/{data_source_id}',
                            'Name': 'ScoreCard Query',
                            'SqlQuery': scorecard_query,
                            'Columns': [
                                {'Name': 'metric_report_mst_month', 'Type': 'STRING'},
                                {'Name': 'entry_type', 'Type': 'STRING'},
                                {'Name': 'business_unit', 'Type': 'STRING'},
                                {'Name': 'metric_name', 'Type': 'STRING'},
                                {'Name': 'region_name', 'Type': 'STRING'},
                                {'Name': 'higher_is_better', 'Type': 'STRING'},
                                {'Name': 'metric_value', 'Type': 'DECIMAL'}
                            ]
                        }
                    }
                },
                ImportMode='SPICE'  # Use SPICE for better performance
            )
            
            logger.info(f"Created QuickSight dataset: {dataset_id}")
            return dataset_id
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceExistsException':
                logger.info(f"Dataset {dataset_id} already exists")
                return dataset_id
            else:
                logger.error(f"Failed to create dataset: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to create dataset: {e}")
            raise
    
    def create_scorecard_dashboard(self, dataset_id: str, dashboard_id: str = None) -> str:
        """
        Create a dashboard with scorecard visualizations.
        
        Args:
            dataset_id: The dataset ID to use
            dashboard_id: Optional custom dashboard ID
            
        Returns:
            The created dashboard ID
        """
        if not dashboard_id:
            dashboard_id = 'scorecard-dashboard'
        
        try:
            # Dashboard definition with multiple visualizations
            dashboard_definition = {
                "DataSetIdentifierDeclarations": [
                    {
                        "DataSetArn": f"arn:aws:quicksight:{config.aws_region}:{self.account_id}:dataset/{dataset_id}",
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
                                    "Title": {
                                        "Visibility": "VISIBLE",
                                        "FormatText": {
                                            "PlainText": "Metrics by Region"
                                        }
                                    },
                                    "FieldWells": {
                                        "BarChartAggregatedFieldWells": {
                                            "Category": [{
                                                "CategoricalDimensionField": {
                                                    "FieldId": "region_name",
                                                    "Column": {
                                                        "DataSetIdentifier": "scorecard_dataset",
                                                        "ColumnName": "region_name"
                                                    }
                                                }
                                            }],
                                            "Values": [{
                                                "NumericalMeasureField": {
                                                    "FieldId": "metric_value",
                                                    "Column": {
                                                        "DataSetIdentifier": "scorecard_dataset",
                                                        "ColumnName": "metric_value"
                                                    },
                                                    "AggregationFunction": {
                                                        "SimpleNumericalAggregation": "SUM"
                                                    }
                                                }
                                            }]
                                        }
                                    }
                                }
                            },
                            {
                                "LineChartVisual": {
                                    "VisualId": "metrics-trend",
                                    "Title": {
                                        "Visibility": "VISIBLE",
                                        "FormatText": {
                                            "PlainText": "Metrics Trend Over Time"
                                        }
                                    },
                                    "FieldWells": {
                                        "LineChartAggregatedFieldWells": {
                                            "Category": [{
                                                "CategoricalDimensionField": {
                                                    "FieldId": "metric_month",
                                                    "Column": {
                                                        "DataSetIdentifier": "scorecard_dataset",
                                                        "ColumnName": "metric_report_mst_month"
                                                    }
                                                }
                                            }],
                                            "Values": [{
                                                "NumericalMeasureField": {
                                                    "FieldId": "metric_value",
                                                    "Column": {
                                                        "DataSetIdentifier": "scorecard_dataset",
                                                        "ColumnName": "metric_value"
                                                    },
                                                    "AggregationFunction": {
                                                        "SimpleNumericalAggregation": "SUM"
                                                    }
                                                }
                                            }],
                                            "Colors": [{
                                                "CategoricalDimensionField": {
                                                    "FieldId": "metric_name",
                                                    "Column": {
                                                        "DataSetIdentifier": "scorecard_dataset",
                                                        "ColumnName": "metric_name"
                                                    }
                                                }
                                            }]
                                        }
                                    }
                                }
                            },
                            {
                                "PivotTableVisual": {
                                    "VisualId": "metrics-table",
                                    "Title": {
                                        "Visibility": "VISIBLE",
                                        "FormatText": {
                                            "PlainText": "Detailed Metrics Table"
                                        }
                                    },
                                    "FieldWells": {
                                        "PivotTableAggregatedFieldWells": {
                                            "Rows": [
                                                {
                                                    "CategoricalDimensionField": {
                                                        "FieldId": "metric_name",
                                                        "Column": {
                                                            "DataSetIdentifier": "scorecard_dataset",
                                                            "ColumnName": "metric_name"
                                                        }
                                                    }
                                                },
                                                {
                                                    "CategoricalDimensionField": {
                                                        "FieldId": "region_name",
                                                        "Column": {
                                                            "DataSetIdentifier": "scorecard_dataset",
                                                            "ColumnName": "region_name"
                                                        }
                                                    }
                                                }
                                            ],
                                            "Columns": [{
                                                "CategoricalDimensionField": {
                                                    "FieldId": "metric_month",
                                                    "Column": {
                                                        "DataSetIdentifier": "scorecard_dataset",
                                                        "ColumnName": "metric_report_mst_month"
                                                    }
                                                }
                                            }],
                                            "Values": [{
                                                "NumericalMeasureField": {
                                                    "FieldId": "metric_value",
                                                    "Column": {
                                                        "DataSetIdentifier": "scorecard_dataset",
                                                        "ColumnName": "metric_value"
                                                    },
                                                    "AggregationFunction": {
                                                        "SimpleNumericalAggregation": "SUM"
                                                    }
                                                }
                                            }]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
            
            response = self.quicksight.create_dashboard(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id,
                Name='Scorecard Metrics Dashboard',
                Definition=dashboard_definition
            )
            
            logger.info(f"Created QuickSight dashboard: {dashboard_id}")
            return dashboard_id
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceExistsException':
                logger.info(f"Dashboard {dashboard_id} already exists")
                return dashboard_id
            else:
                logger.error(f"Failed to create dashboard: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            raise
    
    def get_dashboard_embed_url(self, dashboard_id: str, session_lifetime_minutes: int = 60) -> str:
        """
        Generate an embed URL for the dashboard.
        
        Args:
            dashboard_id: The dashboard ID
            session_lifetime_minutes: How long the URL should be valid
            
        Returns:
            The embeddable URL
        """
        try:
            response = self.quicksight.generate_embed_url_for_anonymous_user(
                AwsAccountId=self.account_id,
                Namespace='default',
                SessionLifetimeInMinutes=session_lifetime_minutes,
                AuthorizedResourceArns=[
                    f'arn:aws:quicksight:{config.aws_region}:{self.account_id}:dashboard/{dashboard_id}'
                ],
                ExperienceConfiguration={
                    'Dashboard': {
                        'InitialDashboardId': dashboard_id
                    }
                }
            )
            
            logger.info(f"Generated embed URL for dashboard: {dashboard_id}")
            return response['EmbedUrl']
            
        except Exception as e:
            logger.error(f"Failed to generate embed URL: {e}")
            raise
    
    def get_dashboard_info(self, dashboard_id: str) -> Dict[str, Any]:
        """
        Get dashboard information and metadata.
        
        Args:
            dashboard_id: The dashboard ID
            
        Returns:
            Dashboard information dictionary
        """
        try:
            response = self.quicksight.describe_dashboard(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id
            )
            
            dashboard_data = {
                'dashboard_id': dashboard_id,
                'name': response['Dashboard']['Name'],
                'created_time': response['Dashboard']['CreatedTime'].isoformat() if 'CreatedTime' in response['Dashboard'] else None,
                'last_updated': response['Dashboard']['LastUpdatedTime'].isoformat() if 'LastUpdatedTime' in response['Dashboard'] else None,
                'version': response['Dashboard']['Version']['VersionNumber'] if 'Version' in response['Dashboard'] else None,
                'status': response['Dashboard']['Version']['Status'] if 'Version' in response['Dashboard'] else None
            }
            
            logger.info(f"Retrieved dashboard info for: {dashboard_id}")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get dashboard info: {e}")
            raise
    
    def setup_complete_dashboard(self, 
                                 data_source_id: str = None,
                                 dataset_id: str = None,
                                 dashboard_id: str = None) -> Dict[str, str]:
        """
        Create the complete dashboard infrastructure from scratch.
        
        Args:
            data_source_id: Optional custom data source ID
            dataset_id: Optional custom dataset ID
            dashboard_id: Optional custom dashboard ID
            
        Returns:
            Dictionary with all created resource IDs
        """
        try:
            logger.info("Starting complete dashboard setup...")
            
            # Step 1: Create data source
            ds_id = self.create_redshift_data_source(data_source_id)
            
            # Step 2: Create dataset
            dataset_id = self.create_scorecard_dataset(ds_id, dataset_id)
            
            # Step 3: Create dashboard
            dash_id = self.create_scorecard_dashboard(dataset_id, dashboard_id)
            
            # Step 4: Get embed URL
            embed_url = self.get_dashboard_embed_url(dash_id)
            
            result = {
                'data_source_id': ds_id,
                'dataset_id': dataset_id,
                'dashboard_id': dash_id,
                'embed_url': embed_url,
                'status': 'success'
            }
            
            logger.info("Complete dashboard setup finished successfully!")
            return result
            
        except Exception as e:
            logger.error(f"Failed to setup complete dashboard: {e}")
            raise