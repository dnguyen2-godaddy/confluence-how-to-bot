#!/usr/bin/env python3
"""
Agent 1: Dashboard Intelligence Agent

Specialized agent for analyzing dashboard images and extracting structured information.
This agent focuses purely on visual analysis, data extraction, and pattern recognition.
"""

import json
import logging
from typing import List, Optional

from utils import config, ImageProcessor

logger = logging.getLogger(__name__)


def create_agent1_analysis_prompt() -> str:
    """Create prompt for Agent 1: Dashboard Intelligence Agent that analyzes images and extracts structured data."""
    
    return """You are a specialized Dashboard Intelligence Agent. Your job is to analyze dashboard images and extract comprehensive, structured information.

ANALYSIS REQUIREMENTS:
- Carefully examine ALL visible elements in the dashboard images
- Extract EXACT metrics, numbers, and data points visible
- Identify ALL interactive elements (filters, dropdowns, buttons, controls)
- Map the visual hierarchy and layout structure
- Recognize chart types and visualization patterns
- Document data relationships and patterns
- Note color coding and visual indicators
- Create in-depth analysis of the dashboard and the key components
- Provide detailed explanation of the dashboard and the key components
- Provide in-depth explanation of use-cases and purpose of the key components
- Analyze functionalities of the dashboard and the key components
- Identify data quality indicators and confidence levels
- Extract business context and strategic implications
- Note performance trends and anomalies

EXTRACTION FOCUS:
1. METRICS & DATA:
   - Exact numbers, percentages, values
   - Chart data points and trends
   - KPI indicators and measurements
   - Time periods and date ranges
   - Data freshness indicators
   - Confidence intervals if visible

2. INTERACTIVE ELEMENTS:
   - Filter names and available options
   - Dropdown menus and selections
   - Button labels and functions
   - Navigation controls and breadcrumbs
   - Drill down and drill up controls
   - Date range picker and selection
   - Sorting and filtering options
   - Download and export options
   - Refresh and update options
   - Search boxes and input fields
   - Any other interactive elements visible

3. VISUAL STRUCTURE:
   - Chart types (bar, line, pie, scatter, etc.)
   - Layout organization and sections
   - Color schemes and visual patterns
   - Data hierarchy and relationships
   - Navigation flow and user paths
   - Responsive design elements

4. BUSINESS CONTEXT:
   - Dashboard purpose and objectives
   - Target audience indicators
   - Business metrics and KPIs
   - Use-cases and purpose of the key components
   - Functionalities of the dashboard and the key components
   - Performance indicators and thresholds
   - Strategic business value
   - Operational impact

5. DATA QUALITY & INSIGHTS:
   - Data freshness and update frequency
   - Completeness indicators
   - Performance trends and patterns
   - Anomalies or outliers
   - Comparative analysis opportunities
   - Actionable insights visible

OUTPUT FORMAT - STRUCTURED DATA ONLY (EXAMPLE, MAKE MORE COMPREHENSIVE AND DETAILED BASE ON THE IMAGES PROCESSED, YOU MAY ADD MORE SECTIONS, COMPONENTS, AND ELEMENTS BASED ON THE IMAGES PROCESSED):
{
  "dashboard_purpose": "Brief description of dashboard objective",
  "target_audience": "Who this dashboard is for",
  "business_value": "Strategic importance and business impact",
  "data_freshness": "How current the data is",
  "update_frequency": "How often data is refreshed",
  "sections": [
    {
      "section_name": "Name of this section/view",
      "section_type": "Type of visualization or data display",
      "business_purpose": "Why this section exists and what it enables",
      "metrics": [
        {
          "name": "Metric name",
          "value": "Exact value shown",
          "unit": "Unit of measurement",
          "trend": "Trend indicator if visible",
          "context": "What this metric means in business terms",
          "threshold": "Performance thresholds if visible"
        }
      ],
      "interactive_elements": [
        {
          "type": "filter/dropdown/button/etc",
          "name": "Element name/label",
          "options": ["Available options if visible"],
          "location": "Where in the section",
          "purpose": "What this control enables users to do"
        }
      ],
      "chart_details": {
        "type": "Chart type",
        "data_points": "Number of data points visible",
        "color_scheme": "Color patterns used",
        "annotations": "Any labels or notes visible",
        "effectiveness": "Why this visualization type works for the data"
      },
      "functionality": "Functionality of the section/view",
      "performance_indicators": "Performance indicators of the section/view",
      "thresholds": "Thresholds of the section/view",
      "detailed_explanation": "Detailed explanation of the section/view",
      "in_depth_explanation": "In-depth explanation of the use-cases and purpose of the key components",
      "data_source": "Data source of the section/view",
      "key_insights": "Key business insights visible in this view",
      "actionable_items": "Specific actions users can take based on this view"
    }
  ],
  "global_controls": [
    {
      "type": "Global filter/control type",
      "name": "Control name",
      "purpose": "What it controls",
      "location": "Where it's positioned",
      "impact": "How it affects the entire dashboard view"
    }
  ],
  "data_quality_indicators": {
    "freshness": "How current the data appears",
    "completeness": "How complete the data coverage is",
    "accuracy": "Any accuracy indicators visible",
    "reliability": "Data reliability factors"
  },
  "performance_trends": {
    "overall_trend": "Overall performance direction",
    "key_drivers": "Main factors driving performance",
    "anomalies": "Any unusual patterns or outliers",
    "opportunities": "Visible improvement opportunities"
  }
}

CRITICAL: Output ONLY the structured JSON data. No explanations, no additional text. Just the JSON object with all extracted information."""


def analyze_dashboard_with_agent1(image_paths: List[str], bedrock_client) -> Optional[str]:
    """Agent 1: Analyze dashboard images and extract structured data."""
    try:
        # Prepare images for analysis
        image_data_list, valid_image_paths = ImageProcessor.prepare_multiple_images_for_bedrock(image_paths)
        
        if not image_data_list:
            return None
            
        # Agent 1 prompt for structured data extraction
        agent1_prompt = create_agent1_analysis_prompt()
        
        # Prepare messages for Agent 1
        content_list = image_data_list + [{
            "type": "text",
            "text": agent1_prompt
        }]
        
        messages = [{
            "role": "user",
            "content": content_list
        }]
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 8000,
            "messages": messages,
            "temperature": 0.1
        }
        
        # Call Bedrock API
        response = bedrock_client.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=json.dumps(body),
            contentType='application/json'
        )
        
        # Parse Agent 1 response
        response_body = json.loads(response['body'].read())
        analysis_data = response_body['content'][0]['text']
        
        return analysis_data
        
    except Exception as e:
        logger.error(f"Agent 1 analysis failed: {e}")
        return None


if __name__ == "__main__":
    # Test the agent
    print("Agent 1: Dashboard Intelligence Agent")
    print("This agent analyzes dashboard images and extracts structured data.")
    print("It should be used as part of the multi-agent workflow.")
