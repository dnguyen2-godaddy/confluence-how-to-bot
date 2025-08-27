#!/usr/bin/env python3
"""
QuickSight Metadata Analyzer

This script demonstrates how to integrate QuickSight API metadata with the existing
dashboard analyzer workflow. It fetches dashboard metadata directly from QuickSight
and can be used to enhance the analysis process.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Add the utils directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from quicksight_client import QuickSightClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QuickSightMetadataAnalyzer:
    """Analyzer that combines QuickSight API metadata with dashboard analysis."""
    
    def __init__(self, region_name: str = 'us-west-2', profile_name: Optional[str] = None):
        """
        Initialize the metadata analyzer.
        
        Args:
            region_name: AWS region for QuickSight service
            profile_name: AWS profile name to use
        """
        self.quicksight_client = QuickSightClient(region_name=region_name, profile_name=profile_name)
        
    def analyze_dashboard_by_name(self, dashboard_name: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a dashboard by searching for it by name.
        
        Args:
            dashboard_name: Name or partial name of the dashboard to analyze
            
        Returns:
            Comprehensive analysis dictionary or None if not found
        """
        try:
            logger.info(f"Searching for dashboard: {dashboard_name}")
            
            # Search for dashboards matching the name
            matching_dashboards = self.quicksight_client.search_dashboards(dashboard_name)
            
            if not matching_dashboards:
                logger.warning(f"No dashboards found matching '{dashboard_name}'")
                return None
            
            # Use the first (most relevant) match
            dashboard = matching_dashboards[0]
            dashboard_id = dashboard['DashboardId']
            
            logger.info(f"Found dashboard: {dashboard.get('Name', 'Unknown')} (ID: {dashboard_id})")
            
            # Get comprehensive metadata
            return self.analyze_dashboard_by_id(dashboard_id)
            
        except Exception as e:
            logger.error(f"Failed to analyze dashboard by name '{dashboard_name}': {e}")
            return None
    
    def analyze_dashboard_by_id(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a dashboard by its ID.
        
        Args:
            dashboard_id: The ID of the dashboard to analyze
            
        Returns:
            Comprehensive analysis dictionary or None if not found
        """
        try:
            logger.info(f"Analyzing dashboard ID: {dashboard_id}")
            
            # Get basic metadata
            metadata = self.quicksight_client.get_dashboard_metadata_summary(dashboard_id)
            if not metadata:
                logger.error(f"Failed to get metadata for dashboard {dashboard_id}")
                return None
            
            # Get detailed dashboard definition
            definition = self.quicksight_client.get_dashboard_definition(dashboard_id)
            
            # Enhanced analysis
            analysis = {
                'metadata': metadata,
                'definition_analysis': self._analyze_dashboard_definition(definition),
                'dataset_analysis': self._analyze_datasets(metadata.get('datasets', [])),
                'technical_insights': self._generate_technical_insights(metadata, definition),
                'analysis_timestamp': datetime.now().isoformat(),
                'analysis_method': 'quicksight_api'
            }
            
            logger.info(f"Completed analysis for dashboard: {metadata.get('name', dashboard_id)}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze dashboard {dashboard_id}: {e}")
            return None
    
    def _analyze_dashboard_definition(self, definition: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the dashboard definition structure."""
        if not definition:
            return {'error': 'No definition available'}
        
        try:
            analysis = {
                'sheets_count': len(definition.get('Sheets', [])),
                'sheets_info': [],
                'visuals_count': 0,
                'filters_count': len(definition.get('FilterGroups', [])),
                'calculated_fields': [],
                'parameters': []
            }
            
            # Analyze sheets
            for sheet in definition.get('Sheets', []):
                sheet_info = {
                    'name': sheet.get('Name', 'Unknown'),
                    'visuals_count': len(sheet.get('Visuals', [])),
                    'layout': sheet.get('Layout', {}),
                    'visual_types': []
                }
                
                # Count visual types
                for visual in sheet.get('Visuals', []):
                    visual_type = visual.get('VisualType', 'Unknown')
                    sheet_info['visual_types'].append(visual_type)
                    analysis['visuals_count'] += 1
                
                analysis['sheets_info'].append(sheet_info)
            
            # Extract calculated fields
            if 'CalculatedFields' in definition:
                for field in definition['CalculatedFields']:
                    analysis['calculated_fields'].append({
                        'name': field.get('Name', 'Unknown'),
                        'expression': field.get('Expression', 'Unknown')
                    })
            
            # Extract parameters
            if 'Parameters' in definition:
                for param in definition['Parameters']:
                    analysis['parameters'].append({
                        'name': param.get('Name', 'Unknown'),
                        'type': param.get('Type', 'Unknown')
                    })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze dashboard definition: {e}")
            return {'error': f'Analysis failed: {str(e)}'}
    
    def _analyze_datasets(self, datasets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the datasets used by the dashboard."""
        try:
            analysis = {
                'total_datasets': len(datasets),
                'dataset_types': {},
                'dataset_details': []
            }
            
            for dataset in datasets:
                dataset_type = dataset.get('type', 'Unknown')
                analysis['dataset_types'][dataset_type] = analysis['dataset_types'].get(dataset_type, 0) + 1
                
                analysis['dataset_details'].append({
                    'id': dataset.get('id', 'Unknown'),
                    'name': dataset.get('name', 'Unknown'),
                    'type': dataset_type,
                    'created': dataset.get('created_time'),
                    'updated': dataset.get('last_updated_time')
                })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze datasets: {e}")
            return {'error': f'Dataset analysis failed: {str(e)}'}
    
    def _generate_technical_insights(self, metadata: Dict[str, Any], definition: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate technical insights about the dashboard."""
        try:
            insights = {
                'complexity_score': 0,
                'performance_considerations': [],
                'best_practices': [],
                'potential_issues': []
            }
            
            # Calculate complexity score
            complexity_factors = 0
            
            # Sheets complexity
            sheets_count = metadata.get('sheets_count', 0)
            if sheets_count > 5:
                complexity_factors += 2
                insights['performance_considerations'].append("High number of sheets may impact loading performance")
            elif sheets_count > 10:
                complexity_factors += 3
                insights['potential_issues'].append("Very high sheet count - consider dashboard consolidation")
            
            # Visuals complexity
            if definition:
                total_visuals = sum(len(sheet.get('Visuals', [])) for sheet in definition.get('Sheets', []))
                if total_visuals > 20:
                    complexity_factors += 2
                    insights['performance_considerations'].append("High visual count may slow down rendering")
                elif total_visuals > 50:
                    complexity_factors += 3
                    insights['potential_issues'].append("Extremely high visual count - performance risk")
            
            # Dataset complexity
            datasets_count = len(metadata.get('datasets', []))
            if datasets_count > 3:
                complexity_factors += 1
                insights['performance_considerations'].append("Multiple datasets may increase query complexity")
            
            # Set complexity score
            if complexity_factors <= 2:
                insights['complexity_score'] = 1  # Low
            elif complexity_factors <= 4:
                insights['complexity_score'] = 2  # Medium
            else:
                insights['complexity_score'] = 3  # High
            
            # Add best practices
            if metadata.get('tags'):
                insights['best_practices'].append("Dashboard has tags for organization")
            
            if metadata.get('last_published_time'):
                insights['best_practices'].append("Dashboard has been published")
            
            # Add potential issues
            if not metadata.get('last_updated_time'):
                insights['potential_issues'].append("Dashboard may be outdated")
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate technical insights: {e}")
            return {'error': f'Insights generation failed: {str(e)}'}
    
    def export_analysis(self, analysis: Dict[str, Any], dashboard_name: str) -> Optional[str]:
        """
        Export the analysis results to a JSON file.
        
        Args:
            analysis: The analysis results to export
            dashboard_name: Name of the dashboard for the filename
            
        Returns:
            Path to the exported file or None if failed
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in dashboard_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            
            output_file = f"outputs/quicksight_analysis_{safe_name}_{timestamp}.json"
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Export to JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Analysis exported to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to export analysis: {e}")
            return None
    
    def generate_summary_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a human-readable summary report from the analysis."""
        try:
            metadata = analysis.get('metadata', {})
            definition_analysis = analysis.get('definition_analysis', {})
            dataset_analysis = analysis.get('dataset_analysis', {})
            technical_insights = analysis.get('technical_insights', {})
            
            report = f"""
# QuickSight Dashboard Analysis Report

## Dashboard Overview
- **Name**: {metadata.get('name', 'Unknown')}
- **ID**: {metadata.get('dashboard_id', 'Unknown')}
- **Created**: {metadata.get('created_time', 'Unknown')}
- **Last Updated**: {metadata.get('last_updated_time', 'Unknown')}
- **Status**: {metadata.get('status', 'Unknown')}

## Structure Analysis
- **Sheets**: {definition_analysis.get('sheets_count', 0)}
- **Total Visuals**: {definition_analysis.get('visuals_count', 0)}
- **Filters**: {definition_analysis.get('filters_count', 0)}
- **Calculated Fields**: {len(definition_analysis.get('calculated_fields', []))}
- **Parameters**: {len(definition_analysis.get('parameters', []))}

## Data Sources
- **Total Datasets**: {dataset_analysis.get('total_datasets', 0)}
- **Dataset Types**: {', '.join(f'{k}: {v}' for k, v in dataset_analysis.get('dataset_types', {}).items())}

## Technical Insights
- **Complexity Score**: {technical_insights.get('complexity_score', 0)} (1=Low, 2=Medium, 3=High)

### Performance Considerations
{chr(10).join(f'- {item}' for item in technical_insights.get('performance_considerations', []))}

### Best Practices
{chr(10).join(f'- {item}' for item in technical_insights.get('best_practices', []))}

### Potential Issues
{chr(10).join(f'- {item}' for item in technical_insights.get('potential_issues', []))}

## Analysis Details
- **Analysis Method**: {analysis.get('analysis_method', 'Unknown')}
- **Analysis Timestamp**: {analysis.get('analysis_timestamp', 'Unknown')}
"""
            
            return report.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate summary report: {e}")
            return f"Error generating report: {str(e)}"


def main():
    """Main function to demonstrate the metadata analyzer."""
    load_dotenv()
    
    print("🚀 QuickSight Metadata Analyzer")
    print("=" * 50)
    print()
    
    # Configuration
    region = os.getenv('AWS_REGION', 'us-west-2')
    profile = os.getenv('AWS_PROFILE')
    
    try:
        # Initialize analyzer
        analyzer = QuickSightMetadataAnalyzer(region_name=region, profile_name=profile)
        
        # Get user input
        print("Choose an option:")
        print("1. Search and analyze dashboard by name")
        print("2. Analyze dashboard by ID")
        print("3. List all available dashboards")
        print()
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            dashboard_name = input("Enter dashboard name or partial name: ").strip()
            if dashboard_name:
                print(f"\n🔍 Analyzing dashboard: {dashboard_name}")
                analysis = analyzer.analyze_dashboard_by_name(dashboard_name)
                
                if analysis:
                    # Export analysis
                    output_file = analyzer.export_analysis(analysis, dashboard_name)
                    if output_file:
                        print(f"✅ Analysis exported to: {output_file}")
                    
                    # Generate and display summary
                    summary = analyzer.generate_summary_report(analysis)
                    print("\n📊 Analysis Summary:")
                    print(summary)
                else:
                    print("❌ Failed to analyze dashboard")
        
        elif choice == "2":
            dashboard_id = input("Enter dashboard ID: ").strip()
            if dashboard_id:
                print(f"\n🔍 Analyzing dashboard ID: {dashboard_id}")
                analysis = analyzer.analyze_dashboard_by_id(dashboard_id)
                
                if analysis:
                    # Export analysis
                    output_file = analyzer.export_analysis(analysis, f"dashboard_{dashboard_id}")
                    if output_file:
                        print(f"✅ Analysis exported to: {output_file}")
                    
                    # Generate and display summary
                    summary = analyzer.generate_summary_report(analysis)
                    print("\n📊 Analysis Summary:")
                    print(summary)
                else:
                    print("❌ Failed to analyze dashboard")
        
        elif choice == "3":
            print("\n🔍 Listing all dashboards...")
            dashboards = analyzer.quicksight_client.list_dashboards(max_results=20)
            
            if dashboards:
                print(f"\nFound {len(dashboards)} dashboards:")
                for i, dashboard in enumerate(dashboards, 1):
                    name = dashboard.get('Name', 'Unknown')
                    dashboard_id = dashboard.get('DashboardId', 'Unknown')
                    created = dashboard.get('CreatedTime')
                    print(f"{i:2d}. {name}")
                    print(f"     ID: {dashboard_id}")
                    print(f"     Created: {created}")
                    print()
            else:
                print("❌ No dashboards found")
        
        else:
            print("❌ Invalid choice")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Make sure you have:")
        print("   1. Configured AWS credentials")
        print("   2. QuickSight permissions")
        print("   3. Correct AWS region")


if __name__ == "__main__":
    main()
