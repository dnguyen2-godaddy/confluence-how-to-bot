"""
QuickSight Dashboard Analyzer

This module analyzes existing QuickSight dashboards to extract structure,
visualizations, data sources, and other metadata for AI processing.
"""

import boto3
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from utils.config import config

logger = logging.getLogger(__name__)


@dataclass
class VisualizationInfo:
    """Information about a single visualization in a dashboard."""
    visual_id: str
    title: str
    visual_type: str
    description: Optional[str] = None
    field_wells: Optional[Dict] = None
    filters: Optional[List] = None
    interactions: Optional[Dict] = None


@dataclass
class DatasetInfo:
    """Information about a dataset used in the dashboard."""
    dataset_id: str
    name: str
    data_source_type: str
    columns: List[str]
    calculated_fields: Optional[List] = None


@dataclass
class DashboardStructure:
    """Complete structure information for a QuickSight dashboard."""
    dashboard_id: str
    name: str
    description: Optional[str]
    created_time: str
    last_updated: str
    version: str
    status: str
    sheets: List[Dict]
    visualizations: List[VisualizationInfo]
    datasets: List[DatasetInfo]
    parameters: Optional[List[Dict]] = None
    filters: Optional[List[Dict]] = None
    themes: Optional[Dict] = None


class DashboardAnalyzer:
    """Analyzes QuickSight dashboards to extract detailed information."""
    
    def __init__(self):
        """Initialize the dashboard analyzer."""
        try:
            if not config.validate_aws_config():
                raise ValueError("AWS configuration is incomplete. Please check your .env file.")
            
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
            logger.info(f"Initialized dashboard analyzer for account: {self.account_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize dashboard analyzer: {e}")
            raise
    
    def analyze_dashboard(self, dashboard_id: str) -> DashboardStructure:
        """
        Perform comprehensive analysis of a QuickSight dashboard.
        
        Args:
            dashboard_id: The QuickSight dashboard ID to analyze
            
        Returns:
            Complete dashboard structure information
        """
        try:
            logger.info(f"Starting analysis of dashboard: {dashboard_id}")
            
            # Get basic dashboard information
            dashboard_info = self._get_dashboard_info(dashboard_id)
            
            # Get dashboard definition for detailed structure
            dashboard_definition = self._get_dashboard_definition(dashboard_id)
            
            # Analyze visualizations
            visualizations = self._analyze_visualizations(dashboard_definition)
            
            # Get dataset information
            datasets = self._analyze_datasets(dashboard_definition)
            
            # Extract parameters and filters
            parameters = self._extract_parameters(dashboard_definition)
            filters = self._extract_filters(dashboard_definition)
            
            # Create complete dashboard structure
            structure = DashboardStructure(
                dashboard_id=dashboard_id,
                name=dashboard_info['name'],
                description=dashboard_info.get('description'),
                created_time=dashboard_info['created_time'],
                last_updated=dashboard_info['last_updated'],
                version=dashboard_info['version'],
                status=dashboard_info['status'],
                sheets=dashboard_definition.get('Sheets', []),
                visualizations=visualizations,
                datasets=datasets,
                parameters=parameters,
                filters=filters,
                themes=dashboard_definition.get('Themes')
            )
            
            logger.info(f"Successfully analyzed dashboard: {dashboard_id}")
            return structure
            
        except Exception as e:
            logger.error(f"Failed to analyze dashboard {dashboard_id}: {e}")
            raise
    
    def _get_dashboard_info(self, dashboard_id: str) -> Dict[str, Any]:
        """Get basic dashboard information."""
        try:
            response = self.quicksight.describe_dashboard(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id
            )
            
            dashboard = response['Dashboard']
            
            return {
                'name': dashboard['Name'],
                'description': dashboard.get('Description'),
                'created_time': dashboard['CreatedTime'].isoformat() if 'CreatedTime' in dashboard else None,
                'last_updated': dashboard['LastUpdatedTime'].isoformat() if 'LastUpdatedTime' in dashboard else None,
                'version': str(dashboard['Version']['VersionNumber']) if 'Version' in dashboard else None,
                'status': dashboard['Version']['Status'] if 'Version' in dashboard else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard info: {e}")
            raise
    
    def _get_dashboard_definition(self, dashboard_id: str) -> Dict[str, Any]:
        """Get detailed dashboard definition."""
        try:
            response = self.quicksight.describe_dashboard_definition(
                AwsAccountId=self.account_id,
                DashboardId=dashboard_id
            )
            
            return response['Definition']
            
        except Exception as e:
            logger.error(f"Failed to get dashboard definition: {e}")
            raise
    
    def _analyze_visualizations(self, dashboard_definition: Dict) -> List[VisualizationInfo]:
        """Analyze all visualizations in the dashboard."""
        visualizations = []
        
        try:
            sheets = dashboard_definition.get('Sheets', [])
            
            for sheet in sheets:
                visuals = sheet.get('Visuals', [])
                
                for visual in visuals:
                    viz_info = self._extract_visualization_info(visual)
                    if viz_info:
                        visualizations.append(viz_info)
            
            logger.info(f"Found {len(visualizations)} visualizations")
            return visualizations
            
        except Exception as e:
            logger.error(f"Failed to analyze visualizations: {e}")
            return []
    
    def _extract_visualization_info(self, visual: Dict) -> Optional[VisualizationInfo]:
        """Extract information from a single visualization."""
        try:
            # Determine visual type and extract relevant information
            visual_types = [
                'BarChartVisual', 'LineChartVisual', 'PieChartVisual', 'ScatterPlotVisual',
                'FilledMapVisual', 'HeatMapVisual', 'TreeMapVisual', 'GeospatialMapVisual',
                'TableVisual', 'PivotTableVisual', 'KPIVisual', 'GaugeChartVisual',
                'BoxPlotVisual', 'WaterfallVisual', 'HistogramVisual', 'WordCloudVisual',
                'InsightVisual', 'SankeyDiagramVisual', 'CustomContentVisual', 'EmptyVisual'
            ]
            
            visual_type = None
            visual_data = None
            
            for vtype in visual_types:
                if vtype in visual:
                    visual_type = vtype
                    visual_data = visual[vtype]
                    break
            
            if not visual_type or not visual_data:
                return None
            
            # Extract basic information
            visual_id = visual_data.get('VisualId', 'unknown')
            title = self._extract_title(visual_data)
            field_wells = visual_data.get('FieldWells')
            
            return VisualizationInfo(
                visual_id=visual_id,
                title=title,
                visual_type=visual_type,
                field_wells=field_wells
            )
            
        except Exception as e:
            logger.error(f"Failed to extract visualization info: {e}")
            return None
    
    def _extract_title(self, visual_data: Dict) -> str:
        """Extract title from visual data."""
        try:
            title_config = visual_data.get('Title', {})
            
            if title_config.get('Visibility') == 'VISIBLE':
                format_text = title_config.get('FormatText', {})
                if 'PlainText' in format_text:
                    return format_text['PlainText']
                elif 'RichText' in format_text:
                    return format_text['RichText']
            
            # Fallback to visual ID if no title
            return visual_data.get('VisualId', 'Untitled Visual')
            
        except Exception as e:
            return 'Untitled Visual'
    
    def _analyze_datasets(self, dashboard_definition: Dict) -> List[DatasetInfo]:
        """Analyze datasets used in the dashboard."""
        datasets = []
        
        try:
            dataset_declarations = dashboard_definition.get('DataSetIdentifierDeclarations', [])
            
            for declaration in dataset_declarations:
                dataset_arn = declaration.get('DataSetArn')
                identifier = declaration.get('Identifier')
                
                if dataset_arn:
                    # Extract dataset ID from ARN
                    dataset_id = dataset_arn.split('/')[-1]
                    
                    # Get detailed dataset information
                    dataset_info = self._get_dataset_details(dataset_id)
                    if dataset_info:
                        datasets.append(dataset_info)
            
            logger.info(f"Found {len(datasets)} datasets")
            return datasets
            
        except Exception as e:
            logger.error(f"Failed to analyze datasets: {e}")
            return []
    
    def _get_dataset_details(self, dataset_id: str) -> Optional[DatasetInfo]:
        """Get detailed information about a dataset."""
        try:
            response = self.quicksight.describe_data_set(
                AwsAccountId=self.account_id,
                DataSetId=dataset_id
            )
            
            dataset = response['DataSet']
            
            # Extract column information
            columns = []
            if 'ColumnGroups' in dataset:
                for group in dataset['ColumnGroups']:
                    if 'GeoSpatialColumnGroup' in group:
                        columns.extend(group['GeoSpatialColumnGroup'].get('Columns', []))
            
            # Get physical table columns if available
            if 'PhysicalTableMap' in dataset:
                for table_name, table_data in dataset['PhysicalTableMap'].items():
                    if 'RelationalTable' in table_data:
                        input_columns = table_data['RelationalTable'].get('InputColumns', [])
                        columns.extend([col['Name'] for col in input_columns])
                    elif 'CustomSql' in table_data:
                        input_columns = table_data['CustomSql'].get('Columns', [])
                        columns.extend([col['Name'] for col in input_columns])
            
            return DatasetInfo(
                dataset_id=dataset_id,
                name=dataset['Name'],
                data_source_type=self._get_data_source_type(dataset),
                columns=list(set(columns))  # Remove duplicates
            )
            
        except Exception as e:
            logger.error(f"Failed to get dataset details for {dataset_id}: {e}")
            return None
    
    def _get_data_source_type(self, dataset: Dict) -> str:
        """Determine the data source type for a dataset."""
        try:
            physical_table_map = dataset.get('PhysicalTableMap', {})
            
            for table_data in physical_table_map.values():
                if 'RelationalTable' in table_data:
                    return 'Relational Database'
                elif 'CustomSql' in table_data:
                    return 'Custom SQL'
                elif 'S3Source' in table_data:
                    return 'Amazon S3'
            
            return 'Unknown'
            
        except Exception as e:
            return 'Unknown'
    
    def _extract_parameters(self, dashboard_definition: Dict) -> Optional[List[Dict]]:
        """Extract parameters from dashboard definition."""
        try:
            return dashboard_definition.get('ParameterDeclarations', [])
        except Exception as e:
            logger.error(f"Failed to extract parameters: {e}")
            return []
    
    def _extract_filters(self, dashboard_definition: Dict) -> Optional[List[Dict]]:
        """Extract filters from dashboard definition."""
        try:
            return dashboard_definition.get('FilterGroups', [])
        except Exception as e:
            logger.error(f"Failed to extract filters: {e}")
            return []
    
    def get_dashboard_list(self) -> List[Dict[str, str]]:
        """Get list of available dashboards in the account."""
        try:
            response = self.quicksight.list_dashboards(
                AwsAccountId=self.account_id
            )
            
            dashboards = []
            for dashboard in response.get('DashboardSummaryList', []):
                dashboards.append({
                    'dashboard_id': dashboard['DashboardId'],
                    'name': dashboard['Name'],
                    'created_time': dashboard['CreatedTime'].isoformat() if 'CreatedTime' in dashboard else None,
                    'last_updated': dashboard['LastUpdatedTime'].isoformat() if 'LastUpdatedTime' in dashboard else None
                })
            
            logger.info(f"Found {len(dashboards)} dashboards in account")
            return dashboards
            
        except Exception as e:
            logger.error(f"Failed to get dashboard list: {e}")
            return []
    
    def generate_analysis_summary(self, structure: DashboardStructure) -> Dict[str, Any]:
        """Generate a summary of the dashboard analysis for AI processing."""
        try:
            summary = {
                'dashboard_info': {
                    'name': structure.name,
                    'description': structure.description,
                    'created_time': structure.created_time,
                    'last_updated': structure.last_updated,
                    'status': structure.status
                },
                'structure_overview': {
                    'total_sheets': len(structure.sheets),
                    'total_visualizations': len(structure.visualizations),
                    'total_datasets': len(structure.datasets),
                    'has_parameters': len(structure.parameters or []) > 0,
                    'has_filters': len(structure.filters or []) > 0
                },
                'visualizations': [
                    {
                        'id': viz.visual_id,
                        'title': viz.title,
                        'type': viz.visual_type,
                        'has_field_wells': viz.field_wells is not None
                    }
                    for viz in structure.visualizations
                ],
                'datasets': [
                    {
                        'id': ds.dataset_id,
                        'name': ds.name,
                        'type': ds.data_source_type,
                        'columns': ds.columns
                    }
                    for ds in structure.datasets
                ],
                'parameters': structure.parameters or [],
                'filters': structure.filters or []
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate analysis summary: {e}")
            return {}