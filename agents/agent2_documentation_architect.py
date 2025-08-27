#!/usr/bin/env python3
"""
Agent 2: Documentation Architect Agent

Specialized agent for creating comprehensive, professional documentation from structured analysis data.
This agent focuses purely on documentation creation, formatting, and business insights.
"""

import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def create_agent2_documentation_prompt(analysis_data: str) -> str:
    """Create prompt for Agent 2: Documentation Architect Agent that creates comprehensive documentation from structured analysis data."""
    
    return f"""You are a specialized Documentation Architect Agent. Your job is to create comprehensive, professional documentation from the structured analysis data provided by Agent 1.

ANALYSIS DATA FROM AGENT 1:
{analysis_data}

INSTRUCTIONS:
Create comprehensive, in-depth documentation that data analysts at GoDaddy will use to help their stakeholders understand how to use their dashboards. Focus on practical usage and navigation guidance for business users. Always provide detailed, thorough analysis with comprehensive insights.

CRITICAL FORMATTING REQUIREMENTS - FOLLOW EXACTLY:
- MANDATORY: Use ONLY the exact structure provided below - NO other sections allowed
- REQUIRED SECTIONS ONLY: Executive Summary, Objective, Dashboard Views, Detailed Overview, Dashboard Controls, How to Use, Key Insights & Recommendations, Data Quality & Reliability
- Use <h2 style="font-weight: bold;"> for main sections
- Use <h3 style="font-weight: bold;"> for numbered detailed views - DYNAMIC COUNTING based on actual content (1., 2., 3., etc.)
- Use <strong>bold text</strong> for subsection names
- CRITICAL: Follow the template structure word-for-word - do not add extra sections
- Write in professional business language for GoDaddy stakeholders
- MANDATORY: Use proper HTML tags for ALL formatting - <strong>, <h2 style="font-weight: bold;">, <h3 style="font-weight: bold;">, <ul>, <li>
- MANDATORY: Create proper numbered lists using <ol><li> for all numbered items
- MANDATORY: Create proper bullet lists using <ul><li> for all bullet points
- MANDATORY: Use <strong> tags around ALL subsection headers

OUTPUT FORMAT (copy this structure - NO SPACING between headers and content, YOU MAY ADD MORE SECTIONS, COMPONENTS, AND ELEMENTS BASED ON THE ANALYSIS DATA, MAKE THE DOCUMENTATION DETAILED AND COMPREHENSIVE):

<h2 style="font-weight: bold;">Executive Summary</h2>
[Provide a concise 2-3 sentence overview highlighting the dashboard's key purpose, most important metrics, and primary business value. Focus on what stakeholders need to know immediately.]

<h2 style="font-weight: bold;">Objective</h2>
[Based on the analysis data, provide a comprehensive 4-6 sentence overview explaining the dashboard's strategic purpose, business context, target audience, key performance indicators, and how it enables data-driven decision making for GoDaddy stakeholders. Use the dashboard_purpose, target_audience, and business_value from the analysis data.]

<h2 style="font-weight: bold;">Dashboard Views</h2>
<ol>
[Based on the sections data, list each view with brief 1-3 word descriptions]
</ol>

<h2 style="font-weight: bold;">Detailed Overview of Each View</h2>
[Create exactly the number of <h3 style="font-weight: bold;"> sections that match the sections identified in the analysis data. Each view should have comprehensive, in-depth analysis based on the extracted data:]

<h3 style="font-weight: bold;">1. [Section Name from Analysis]</h3>
[Provide a detailed 3-4 sentence description based on the analysis data. Explain what this view displays, its business purpose, target audience, and strategic importance. Use the chart_details and metrics information from the analysis.]

<strong>Business Purpose</strong>
[Based on the business_purpose from the analysis data, explain why this view exists and what business decisions it enables. Connect it to GoDaddy's strategic objectives.]

<strong>Metrics Reported</strong>
<ol>
[Based on the metrics array from the analysis data, list ALL metrics with specific names, units, and brief explanations of what each metric measures. Include context and thresholds if available.]
</ol>

<strong>Data Visualization Type</strong>
[Based on the chart_details.type and effectiveness from the analysis data, describe the specific chart type, graph style, or visualization method used. Explain why this visualization choice is effective for the data being presented.]

<strong>Business Context & Interpretation</strong>
[Provide 2-4 sentences explaining what these metrics mean in business terms, how to interpret trends, what good vs. poor performance looks like, and what actions stakeholders should take based on the data. Use the key_insights and actionable_items from the analysis data.]

<strong>Interactive Controls & Drill-Down Options</strong>
[Based on the interactive_elements array from the analysis data, describe in detail the available drill-down options, filters, and interactive controls visible in this view. Include specific names, locations, and how users can navigate deeper into the data.]

<strong>Key Insights & Actions</strong>
[Based on the key_insights and actionable_items from the analysis data, provide 2-3 specific business insights and recommended actions users can take based on this view.]

[CONTINUE WITH ADDITIONAL VIEWS - Create exactly the number you identified, numbered sequentially with the same comprehensive detail level]

<h2 style="font-weight: bold;">Dashboard Controls & Filters</h2>
[Based on the global_controls array from the analysis data, provide a comprehensive overview of ALL interactive elements including filters, dropdowns, date selectors, search boxes, and navigation controls. For each control, specify its exact name, location, purpose, available options, and how it affects the dashboard view. Include any global vs. view-specific controls.]

<h2 style="font-weight: bold;">How to Use This Dashboard</h2>
[Based on the analysis data, provide detailed, step-by-step instructions for using THIS specific dashboard. Include exact filter names, button locations, navigation paths, and specific features visible in the screenshots. Make this practical and actionable with real examples. Include troubleshooting tips for common issues users might encounter.]

<h2 style="font-weight: bold;">Key Insights & Recommendations</h2>
[Based on the key_insights and performance_trends from the analysis data, provide 4-5 actionable business insights and recommendations. Focus on what the data reveals about performance, trends, opportunities, and areas for improvement. Make these specific to GoDaddy's business context and include specific actions stakeholders can take.]

<h2 style="font-weight: bold;">Data Quality & Reliability</h2>
[Based on the data_quality_indicators from the analysis data, provide information about data freshness, completeness, accuracy, and reliability. Include any caveats about data limitations, update schedules, and factors that might affect data interpretation.]

<h2 style="font-weight: bold;">Performance Monitoring & Alerts</h2>
[Based on the performance_trends and thresholds from the analysis data, provide guidance on what performance levels to watch for, when to escalate issues, and how to monitor trends over time. Include specific thresholds and warning signs if visible in the data.]

[Include all images used, in-lined with text and document.]"""


def create_documentation_with_agent2(analysis_data: str, bedrock_client) -> Optional[str]:
    """Agent 2: Create comprehensive documentation from structured analysis data."""
    try:
        # Agent 2 prompt for documentation creation
        agent2_prompt = create_agent2_documentation_prompt(analysis_data)
        
        # Prepare messages for Agent 2
        messages = [{
            "role": "user",
            "content": agent2_prompt
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
        
        # Parse Agent 2 response
        response_body = json.loads(response['body'].read())
        documentation_text = response_body['content'][0]['text']
        
        return documentation_text
        
    except Exception as e:
        logger.error(f"Agent 2 documentation failed: {e}")
        return None


if __name__ == "__main__":
    # Test the agent
    print("Agent 2: Documentation Architect Agent")
    print("This agent creates comprehensive documentation from structured analysis data.")
    print("It should be used as part of the multi-agent workflow.")
