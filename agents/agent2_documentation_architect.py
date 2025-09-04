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
    
    return f"""You are a specialized Documentation Architect Agent. Your job is to create comprehensive, professional dashboard documentation using the structured analysis data provided by Agent 1.

ANALYSIS DATA FROM AGENT 1:
{analysis_data}

CRITICAL INSTRUCTIONS - READ CAREFULLY:
Create comprehensive, in-depth dashboard documentation that follows the EXACT template structure provided below. This documentation will be used by GoDaddy data analysts and stakeholders to understand and use their dashboards effectively.

MANDATORY REQUIREMENTS - VIOLATION WILL RESULT IN INCOMPLETE DOCUMENTATION:
- CRITICAL: Generate COMPLETE documentation for ALL 10 sections - NO EXCEPTIONS
- CRITICAL: NEVER use placeholders like "[Additional metrics continued...]" or "[Continued with remaining sections...]"
- CRITICAL: NEVER use notes like "[Note: I've provided a partial response due to length limitations...]"
- CRITICAL: Complete EVERY section fully before moving to the next
- CRITICAL: If you hit token limits, prioritize completing all sections over detailed explanations
- CRITICAL: Generate ALL metrics, ALL views, ALL business questions - COMPLETE LISTS ONLY

CRITICAL FORMATTING REQUIREMENTS - FOLLOW EXACTLY:
- MANDATORY: Use ONLY the exact 10-section structure provided below - NO other sections allowed
- REQUIRED SECTIONS ONLY: The 10 numbered sections in the template
- Use <h2 style="font-weight: bold;"> for main sections (1-10)
- Use <h3 style="font-weight: bold;"> for subsections within each main section
- Use <strong>bold text</strong> for subsection names
- CRITICAL: Follow the template structure word-for-word - do not add extra sections
- Write in professional business language for GoDaddy stakeholders
- MANDATORY: Use proper HTML tags for ALL formatting - <strong>, <h2 style="font-weight: bold;">, <h3 style="font-weight: bold;">, <ul>, <li>, <ol>
- MANDATORY: Create proper numbered lists using <ol><li> for all numbered items
- MANDATORY: Create proper bullet lists using <ul><li> for all bullet points
- MANDATORY: Use <strong> tags around ALL subsection headers

OUTPUT FORMAT - COPY THIS EXACT STRUCTURE (NO SPACING between headers and content):

<h2 style="font-weight: bold;">1. Dashboard Name & High-Level Summary</h2>

<strong>Dashboard Title:</strong>
[Based on the analysis data, provide the dashboard title or suggest a descriptive name]

<strong>Short Description:</strong>
[Provide 2-3 sentences about what this dashboard does and why it's useful, based on the dashboard_purpose and business_value from the analysis]

<strong>Link to Dashboard:</strong>
[If available in the analysis data, provide the dashboard URL. Otherwise, note "Dashboard URL to be provided by administrator"]

<h2 style="font-weight: bold;">2. Purpose & Business Context</h2>

<strong>Business Questions This Dashboard Answers:</strong>
<ul>
[Based on the analysis data, list 3-5 specific business questions this dashboard helps answer. Use the key_insights and business_purpose from the analysis. COMPLETE ALL QUESTIONS - NO PLACEHOLDERS]
</ul>

<strong>Key Use Cases:</strong>
<ul>
[Based on the target_audience and business_value from the analysis, list 3-4 key use cases for this dashboard. COMPLETE ALL USE CASES - NO PLACEHOLDERS]
</ul>

<strong>Domains:</strong>
<ul>
[Based on the analysis data, identify which business domains this dashboard serves (e.g., Care, Customer Market, Finance, Domains, etc.). COMPLETE ALL DOMAINS - NO PLACEHOLDERS]
</ul>

<h2 style="font-weight: bold;">3. Dashboard Views</h2>

[Based on the sections data from the analysis, create a detailed view for each identified section. Each view should follow this structure. COMPLETE ALL VIEWS - NO PLACEHOLDERS:]

<h3 style="font-weight: bold;">[Section Name from Analysis]</h3>

<strong>Description:</strong>
[Provide a detailed 2-3 sentence description of what this view displays, based on the chart_details and metrics from the analysis]

<strong>Key Metrics in View:</strong>
<ul>
[Based on the metrics array from the analysis, list the key metrics with brief definitions. COMPLETE ALL METRICS - NO PLACEHOLDERS]
</ul>

<strong>Intended Audience/Use Case:</strong>
[Based on the target_audience from the analysis, specify who should use this view and for what purpose]

<strong>Navigation Walkthrough:</strong>
[Based on the interactive_elements from the analysis, provide step-by-step navigation instructions]

<strong>Common Workflows & Tips:</strong>
<ul>
[Based on the analysis data, provide 2-3 practical tips for using this view effectively. COMPLETE ALL TIPS - NO PLACEHOLDERS]
</ul>

[CONTINUE WITH ADDITIONAL VIEWS - Create exactly the number you identified, numbered sequentially with the same comprehensive detail level. COMPLETE ALL VIEWS - NO PLACEHOLDERS]

<h2 style="font-weight: bold;">4. Key Metric Definitions</h2>

[Based on the metrics array from the analysis, create detailed definitions for each key metric. COMPLETE ALL METRICS - NO PLACEHOLDERS:]

<strong>[Metric Name]:</strong>
<ul>
<li><strong>Definition:</strong> [Full definition of what this metric measures]</li>
<li><strong>Data Governance Link:</strong> [Note if there's an Alation DG link or similar data governance reference]</li>
<li><strong>Calculation Logic:</strong> [Based on the analysis data, explain how this metric is calculated]</li>
</ul>

[Continue for all metrics identified in the analysis. COMPLETE ALL METRICS - NO PLACEHOLDERS]

<h2 style="font-weight: bold;">5. Data Refresh & Update Cadence</h2>

<strong>Schedule:</strong>
[Based on the data_quality_indicators from the analysis, specify the refresh schedule if available, otherwise note "To be confirmed with data team"]

<strong>Data Pipeline:</strong>
[Based on the analysis data, specify the data source or pipeline if identifiable, otherwise note "To be confirmed with data team"]

<strong>Dependencies:</strong>
<ul>
[Based on the analysis data, list any data dependencies if identifiable, otherwise note "To be confirmed with data team". COMPLETE ALL DEPENDENCIES - NO PLACEHOLDERS]
</ul>

<h2 style="font-weight: bold;">6. Ownership & Contacts</h2>

<strong>Primary Owner:</strong>
[Note "To be assigned by GoDaddy Analytics Team"]

<strong>Slack Channel:</strong>
[Note "To be established by GoDaddy Analytics Team"]

<strong>Stakeholders:</strong>
<ul>
[Based on the target_audience and business_value from the analysis, identify the key stakeholder groups. COMPLETE ALL STAKEHOLDERS - NO PLACEHOLDERS]
</ul>

<h2 style="font-weight: bold;">7. Known Limitations & Assumptions</h2>

<strong>Limitations:</strong>
<ul>
[Based on the data_quality_indicators and any limitations identified in the analysis, list known limitations. COMPLETE ALL LIMITATIONS - NO PLACEHOLDERS]
</ul>

<strong>Workarounds:</strong>
<ul>
[Based on the analysis data, suggest workarounds for any identified limitations. COMPLETE ALL WORKAROUNDS - NO PLACEHOLDERS]
</ul>

<h2 style="font-weight: bold;">8. Frequently Asked Questions (FAQ)</strong>

[Based on the analysis data, create 3-4 relevant FAQs. COMPLETE ALL FAQS - NO PLACEHOLDERS:]

<strong>Question:</strong> [Common question users might have about this dashboard]
<strong>Answer:</strong> [Clear answer based on the analysis data]

[Continue with additional FAQs based on the analysis. COMPLETE ALL FAQS - NO PLACEHOLDERS]

<h2 style="font-weight: bold;">9. Relevant Links / References</strong>

<strong>Related Dashboards:</strong>
<ul>
[Based on the analysis data, suggest related dashboards if applicable, otherwise note "To be identified by analytics team". COMPLETE ALL REFERENCES - NO PLACEHOLDERS]
</ul>

<strong>Documentation on Data Sources:</strong>
<ul>
[Based on the analysis data, note any data source documentation if available. COMPLETE ALL REFERENCES - NO PLACEHOLDERS]
</ul>

<strong>Training / Video Tutorials:</strong>
<ul>
[Note "To be developed by GoDaddy Analytics Team"]
</ul>

<h2 style="font-weight: bold;">10. Change Log & Version History</h2>

<strong>Initial Documentation:</strong>
<ul>
<li><strong>Date:</strong> [Current date]</strong></li>
<li><strong>Change Description:</strong> Initial dashboard documentation created based on AI analysis</li>
<li><strong>Changed By:</strong> AI Documentation Agent</li>
<li><strong>Requester:</strong> GoDaddy Analytics Team</li>
</ul>

[Include all images used, in-lined with text and document. Ensure the documentation is comprehensive and actionable for GoDaddy stakeholders.]

FINAL CRITICAL INSTRUCTIONS:
- COMPLETE ALL 10 SECTIONS FULLY
- NO PLACEHOLDERS, NO INCOMPLETE SECTIONS, NO "CONTINUED..." NOTES
- IF YOU HIT TOKEN LIMITS, PRIORITIZE COMPLETING ALL SECTIONS OVER DETAILED EXPLANATIONS
- GENERATE COMPLETE, PRODUCTION-READY DOCUMENTATION
- CRITICAL: Output ONLY the HTML documentation. No explanations, no conversational text, no "I'll create..." statements. Just the pure HTML content starting with <h1>."""


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
            "max_tokens": 16000,
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
