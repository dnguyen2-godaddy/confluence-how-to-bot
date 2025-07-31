"""
AI-Powered Dashboard Analysis and Documentation Generator

This module uses AI to analyze QuickSight dashboard structures and generate
comprehensive how-to documentation for end users.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
from utils.config import config
from utils.dashboard_analyzer import DashboardStructure

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI-powered analyzer for creating dashboard documentation."""
    
    def __init__(self):
        """Initialize the AI analyzer."""
        try:
            if not config.validate_ai_config():
                raise ValueError("OpenAI API configuration is missing. Please check your .env file for OPENAI_API_KEY.")
            
            self.client = OpenAI(api_key=config.openai_api_key)
            logger.info("Initialized AI analyzer with OpenAI")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI analyzer: {e}")
            raise
    
    def analyze_dashboard_purpose(self, structure: DashboardStructure) -> Dict[str, str]:
        """
        Use AI to determine the dashboard's purpose and target audience.
        
        Args:
            structure: Dashboard structure from analyzer
            
        Returns:
            Dictionary with purpose, audience, and key insights
        """
        try:
            # Prepare dashboard information for AI analysis
            dashboard_context = self._prepare_dashboard_context(structure)
            
            prompt = f"""
            Analyze this QuickSight dashboard and determine its purpose, target audience, and key insights.
            
            Dashboard Information:
            {json.dumps(dashboard_context, indent=2)}
            
            Please provide analysis in the following JSON format:
            {{
                "purpose": "Brief description of what this dashboard is designed to accomplish",
                "target_audience": "Who is the intended audience (executives, analysts, operations team, etc.)",
                "key_insights": "What are the main insights users can derive from this dashboard",
                "business_value": "How does this dashboard provide business value",
                "complexity_level": "beginner/intermediate/advanced - based on the dashboard complexity"
            }}
            
            Focus on practical understanding for end users who need to navigate and use this dashboard effectively.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert business intelligence analyst who specializes in dashboard design and user experience. Provide clear, practical insights about dashboard purpose and usage."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse the JSON response
            result = json.loads(response.choices[0].message.content)
            logger.info("Successfully analyzed dashboard purpose with AI")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze dashboard purpose: {e}")
            # Return fallback analysis
            return {
                "purpose": f"Analytics dashboard for {structure.name}",
                "target_audience": "Business users and analysts",
                "key_insights": "Data-driven insights from organizational metrics",
                "business_value": "Enables data-driven decision making",
                "complexity_level": "intermediate"
            }
    
    def generate_navigation_guide(self, structure: DashboardStructure) -> Dict[str, Any]:
        """
        Generate comprehensive navigation guide for the dashboard.
        
        Args:
            structure: Dashboard structure from analyzer
            
        Returns:
            Structured navigation guide
        """
        try:
            dashboard_context = self._prepare_dashboard_context(structure)
            
            prompt = f"""
            Create a comprehensive navigation guide for this QuickSight dashboard. 
            Focus on helping end users understand how to navigate and interact with the dashboard effectively.
            
            Dashboard Information:
            {json.dumps(dashboard_context, indent=2)}
            
            Please provide the guide in the following JSON format:
            {{
                "overview": {{
                    "dashboard_structure": "High-level description of how the dashboard is organized",
                    "navigation_tips": ["List of general navigation tips"],
                    "key_interactions": ["List of key interactive features"]
                }},
                "sheets_guide": [
                    {{
                        "sheet_name": "Name of the sheet/tab",
                        "purpose": "What this sheet is designed to show",
                        "key_visualizations": ["List of main charts/visuals"],
                        "how_to_use": "Step-by-step guidance for using this sheet",
                        "insights_to_look_for": ["What insights users should focus on"]
                    }}
                ],
                "visualizations_guide": [
                    {{
                        "visualization_title": "Title of the visualization",
                        "type": "Type of chart/visual",
                        "purpose": "What this visualization shows",
                        "how_to_read": "How to interpret this visualization",
                        "interactive_features": ["List of interactive capabilities"],
                        "common_actions": ["Common user actions for this visual"]
                    }}
                ],
                "filters_and_parameters": {{
                    "available_filters": ["List of available filters"],
                    "how_to_use_filters": "Instructions for using filters",
                    "parameter_guidance": "How to use parameters if available"
                }},
                "troubleshooting": [
                    {{
                        "issue": "Common issue users might face",
                        "solution": "How to resolve the issue"
                    }}
                ]
            }}
            
            Make the guide practical and user-friendly, assuming users have basic dashboard experience but may be new to this specific dashboard.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a technical documentation expert specializing in creating user-friendly guides for business intelligence tools. Write clear, actionable instructions that help users navigate dashboards effectively."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info("Successfully generated navigation guide with AI")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate navigation guide: {e}")
            return self._generate_fallback_navigation_guide(structure)
    
    def generate_use_cases(self, structure: DashboardStructure, purpose_analysis: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Generate specific use cases and scenarios for the dashboard.
        
        Args:
            structure: Dashboard structure from analyzer
            purpose_analysis: Results from purpose analysis
            
        Returns:
            List of use cases with scenarios
        """
        try:
            dashboard_context = self._prepare_dashboard_context(structure)
            
            prompt = f"""
            Based on this dashboard analysis and its purpose, generate specific use cases and scenarios 
            where users would interact with this dashboard.
            
            Dashboard Information:
            {json.dumps(dashboard_context, indent=2)}
            
            Purpose Analysis:
            {json.dumps(purpose_analysis, indent=2)}
            
            Please provide use cases in the following JSON format:
            {{
                "use_cases": [
                    {{
                        "scenario": "Specific business scenario or question",
                        "user_role": "Who would typically perform this task",
                        "steps": ["Step-by-step process to accomplish the task"],
                        "expected_outcome": "What the user should discover or accomplish",
                        "tips": ["Additional tips for this use case"]
                    }}
                ]
            }}
            
            Focus on real-world scenarios where business users would interact with this dashboard to make decisions or gain insights.
            Generate 3-5 practical use cases.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a business analyst expert who understands how different roles use dashboards in their daily work. Create practical, realistic use cases that demonstrate the dashboard's value."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info("Successfully generated use cases with AI")
            return result.get("use_cases", [])
            
        except Exception as e:
            logger.error(f"Failed to generate use cases: {e}")
            return self._generate_fallback_use_cases(structure)
    
    def generate_best_practices(self, structure: DashboardStructure) -> Dict[str, List[str]]:
        """
        Generate best practices for using the dashboard effectively.
        
        Args:
            structure: Dashboard structure from analyzer
            
        Returns:
            Dictionary with categorized best practices
        """
        try:
            dashboard_context = self._prepare_dashboard_context(structure)
            
            prompt = f"""
            Generate best practices and recommendations for effectively using this QuickSight dashboard.
            
            Dashboard Information:
            {json.dumps(dashboard_context, indent=2)}
            
            Please provide best practices in the following JSON format:
            {{
                "data_interpretation": ["Best practices for interpreting the data correctly"],
                "navigation_efficiency": ["Tips for navigating the dashboard efficiently"],
                "performance_optimization": ["Recommendations for optimal dashboard performance"],
                "decision_making": ["How to use the dashboard for effective decision making"],
                "collaboration": ["Best practices for sharing insights with others"],
                "maintenance": ["Tips for keeping dashboard usage effective over time"]
            }}
            
            Focus on practical, actionable advice that will help users get the most value from the dashboard.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a dashboard usability expert who helps organizations maximize the value of their business intelligence tools. Provide practical, actionable best practices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info("Successfully generated best practices with AI")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate best practices: {e}")
            return self._generate_fallback_best_practices()
    
    def _prepare_dashboard_context(self, structure: DashboardStructure) -> Dict[str, Any]:
        """Prepare dashboard information for AI analysis."""
        return {
            "name": structure.name,
            "description": structure.description,
            "total_sheets": len(structure.sheets),
            "total_visualizations": len(structure.visualizations),
            "visualizations": [
                {
                    "title": viz.title,
                    "type": viz.visual_type.replace('Visual', ''),
                    "visual_id": viz.visual_id
                }
                for viz in structure.visualizations
            ],
            "datasets": [
                {
                    "name": ds.name,
                    "type": ds.data_source_type,
                    "columns": ds.columns[:10]  # Limit to first 10 columns for context
                }
                for ds in structure.datasets
            ],
            "has_parameters": len(structure.parameters or []) > 0,
            "has_filters": len(structure.filters or []) > 0,
            "parameter_count": len(structure.parameters or []),
            "filter_count": len(structure.filters or [])
        }
    
    def _generate_fallback_navigation_guide(self, structure: DashboardStructure) -> Dict[str, Any]:
        """Generate fallback navigation guide if AI analysis fails."""
        return {
            "overview": {
                "dashboard_structure": f"This dashboard contains {len(structure.visualizations)} visualizations across {len(structure.sheets)} sheets.",
                "navigation_tips": [
                    "Use the tabs at the top to navigate between different sheets",
                    "Click on charts to interact and filter data",
                    "Use the filter panels to focus on specific data segments"
                ],
                "key_interactions": ["Filtering", "Drilling down", "Cross-filtering"]
            },
            "sheets_guide": [
                {
                    "sheet_name": f"Sheet {i+1}",
                    "purpose": "Data analysis and insights",
                    "key_visualizations": [viz.title for viz in structure.visualizations],
                    "how_to_use": "Navigate through the visualizations to explore your data",
                    "insights_to_look_for": ["Trends", "Patterns", "Anomalies"]
                }
                for i in range(len(structure.sheets))
            ],
            "visualizations_guide": [
                {
                    "visualization_title": viz.title,
                    "type": viz.visual_type.replace('Visual', ''),
                    "purpose": "Data visualization and analysis",
                    "how_to_read": "Interpret the data based on the chart type",
                    "interactive_features": ["Click to filter", "Hover for details"],
                    "common_actions": ["Filter", "Drill down", "Export"]
                }
                for viz in structure.visualizations
            ],
            "filters_and_parameters": {
                "available_filters": ["Various data filters available"],
                "how_to_use_filters": "Select filter values to focus on specific data segments",
                "parameter_guidance": "Use parameters to customize the dashboard view"
            },
            "troubleshooting": [
                {
                    "issue": "Dashboard loading slowly",
                    "solution": "Check your internet connection and refresh the page"
                },
                {
                    "issue": "No data showing",
                    "solution": "Check if filters are too restrictive"
                }
            ]
        }
    
    def _generate_fallback_use_cases(self, structure: DashboardStructure) -> List[Dict[str, str]]:
        """Generate fallback use cases if AI analysis fails."""
        return [
            {
                "scenario": "Monthly performance review",
                "user_role": "Manager",
                "steps": ["Open the dashboard", "Select the current month", "Review key metrics", "Identify trends"],
                "expected_outcome": "Understanding of monthly performance",
                "tips": ["Compare with previous months", "Look for patterns"]
            },
            {
                "scenario": "Data exploration",
                "user_role": "Analyst",
                "steps": ["Navigate to different views", "Apply filters", "Drill down into details", "Export data if needed"],
                "expected_outcome": "Detailed insights into data patterns",
                "tips": ["Use multiple filters", "Cross-reference different charts"]
            }
        ]
    
    def _generate_fallback_best_practices(self) -> Dict[str, List[str]]:
        """Generate fallback best practices if AI analysis fails."""
        return {
            "data_interpretation": [
                "Always check the data refresh date",
                "Understand the context behind the numbers",
                "Look for trends rather than single data points"
            ],
            "navigation_efficiency": [
                "Bookmark frequently used views",
                "Use keyboard shortcuts when available",
                "Keep filters relevant to your analysis"
            ],
            "performance_optimization": [
                "Avoid applying too many filters simultaneously",
                "Close unused browser tabs",
                "Use the dashboard during off-peak hours"
            ],
            "decision_making": [
                "Combine dashboard insights with domain knowledge",
                "Validate unusual patterns before taking action",
                "Consider multiple data points for important decisions"
            ],
            "collaboration": [
                "Share specific views with relevant stakeholders",
                "Document insights for future reference",
                "Schedule regular dashboard reviews with your team"
            ],
            "maintenance": [
                "Report data quality issues promptly",
                "Provide feedback on dashboard usability",
                "Stay updated on new features and capabilities"
            ]
        }