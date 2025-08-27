"""
Multi-Agent Dashboard Analysis Package

This package contains specialized AI agents for dashboard analysis:
- Agent 1: Dashboard Intelligence Agent (image analysis and data extraction)
- Agent 2: Documentation Architect Agent (documentation creation)

Each agent is designed to focus on a specific aspect of the analysis workflow.
"""

from .agent1_dashboard_intelligence import analyze_dashboard_with_agent1, create_agent1_analysis_prompt
from .agent2_documentation_architect import create_documentation_with_agent2, create_agent2_documentation_prompt

__all__ = [
    'analyze_dashboard_with_agent1',
    'create_agent1_analysis_prompt',
    'create_documentation_with_agent2',
    'create_agent2_documentation_prompt'
]
