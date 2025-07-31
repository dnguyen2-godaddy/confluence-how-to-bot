"""
Documentation Generator

This module generates comprehensive how-to documentation from AI analysis
of QuickSight dashboards, formatted for Confluence upload.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from jinja2 import Template
import markdown
from utils.dashboard_analyzer import DashboardStructure

logger = logging.getLogger(__name__)


class DocumentGenerator:
    """Generates structured documentation from dashboard analysis."""
    
    def __init__(self):
        """Initialize the document generator."""
        self.template_engine = self._setup_templates()
        logger.info("Initialized document generator")
    
    def generate_complete_documentation(self, 
                                      structure: DashboardStructure,
                                      purpose_analysis: Dict[str, str],
                                      navigation_guide: Dict[str, Any],
                                      use_cases: List[Dict[str, str]],
                                      best_practices: Dict[str, List[str]]) -> Dict[str, str]:
        """
        Generate complete documentation package.
        
        Args:
            structure: Dashboard structure from analyzer
            purpose_analysis: AI analysis of dashboard purpose
            navigation_guide: AI-generated navigation guide
            use_cases: AI-generated use cases
            best_practices: AI-generated best practices
            
        Returns:
            Dictionary with different documentation formats
        """
        try:
            logger.info(f"Generating documentation for dashboard: {structure.name}")
            
            # Prepare documentation context
            doc_context = self._prepare_documentation_context(
                structure, purpose_analysis, navigation_guide, use_cases, best_practices
            )
            
            # Generate different formats
            documentation = {
                'confluence_html': self._generate_confluence_html(doc_context),
                'markdown': self._generate_markdown(doc_context),
                'json_structure': json.dumps(doc_context, indent=2),
                'title': f"How to Use {structure.name} Dashboard",
                'summary': self._generate_summary(doc_context)
            }
            
            logger.info("Successfully generated complete documentation")
            return documentation
            
        except Exception as e:
            logger.error(f"Failed to generate documentation: {e}")
            raise
    
    def _prepare_documentation_context(self,
                                     structure: DashboardStructure,
                                     purpose_analysis: Dict[str, str],
                                     navigation_guide: Dict[str, Any],
                                     use_cases: List[Dict[str, str]],
                                     best_practices: Dict[str, List[str]]) -> Dict[str, Any]:
        """Prepare comprehensive context for documentation generation."""
        
        return {
            'dashboard': {
                'name': structure.name,
                'description': structure.description or "Business intelligence dashboard",
                'created_date': structure.created_time,
                'last_updated': structure.last_updated,
                'status': structure.status
            },
            'generation_info': {
                'generated_date': datetime.now().isoformat(),
                'generator': "Confluence How-To Bot",
                'version': "1.0"
            },
            'purpose': purpose_analysis,
            'structure_overview': {
                'total_sheets': len(structure.sheets),
                'total_visualizations': len(structure.visualizations),
                'total_datasets': len(structure.datasets),
                'has_parameters': len(structure.parameters or []) > 0,
                'has_filters': len(structure.filters or []) > 0
            },
            'navigation': navigation_guide,
            'use_cases': use_cases,
            'best_practices': best_practices,
            'visualizations': [
                {
                    'title': viz.title,
                    'type': viz.visual_type.replace('Visual', '').replace('Chart', ' Chart'),
                    'id': viz.visual_id
                }
                for viz in structure.visualizations
            ],
            'datasets': [
                {
                    'name': ds.name,
                    'type': ds.data_source_type,
                    'column_count': len(ds.columns)
                }
                for ds in structure.datasets
            ]
        }
    
    def _generate_confluence_html(self, context: Dict[str, Any]) -> str:
        """Generate HTML formatted for Confluence."""
        
        template = Template("""
<h1>📊 {{ dashboard.name }} - User Guide</h1>

<div class="panel" style="border-color: #3498db; border-width: 2px;">
    <div class="panelHeader" style="border-color: #3498db; background-color: #e8f4fd;">
        <strong>📋 Dashboard Overview</strong>
    </div>
    <div class="panelContent">
        <p><strong>Purpose:</strong> {{ purpose.purpose }}</p>
        <p><strong>Target Audience:</strong> {{ purpose.target_audience }}</p>
        <p><strong>Business Value:</strong> {{ purpose.business_value }}</p>
        <p><strong>Complexity Level:</strong> {{ purpose.complexity_level | title }}</p>
        <p><strong>Last Updated:</strong> {{ dashboard.last_updated }}</p>
    </div>
</div>

<h2>🎯 Key Insights</h2>
<p>{{ purpose.key_insights }}</p>

<h2>🧭 Navigation Guide</h2>

<h3>Dashboard Structure</h3>
<p>{{ navigation.overview.dashboard_structure }}</p>

<div class="panel" style="border-color: #27ae60; border-width: 1px;">
    <div class="panelHeader" style="border-color: #27ae60; background-color: #e8f5e8;">
        <strong>💡 Quick Navigation Tips</strong>
    </div>
    <div class="panelContent">
        <ul>
        {% for tip in navigation.overview.navigation_tips %}
            <li>{{ tip }}</li>
        {% endfor %}
        </ul>
    </div>
</div>

<h3>Interactive Features</h3>
<ul>
{% for feature in navigation.overview.key_interactions %}
    <li><strong>{{ feature }}</strong></li>
{% endfor %}
</ul>

{% if navigation.sheets_guide %}
<h3>📑 Sheet-by-Sheet Guide</h3>
{% for sheet in navigation.sheets_guide %}
<div class="panel" style="border-color: #9b59b6; border-width: 1px;">
    <div class="panelHeader" style="border-color: #9b59b6; background-color: #f4ecf7;">
        <strong>{{ sheet.sheet_name }}</strong>
    </div>
    <div class="panelContent">
        <p><strong>Purpose:</strong> {{ sheet.purpose }}</p>
        <p><strong>How to Use:</strong> {{ sheet.how_to_use }}</p>
        
        <p><strong>Key Visualizations:</strong></p>
        <ul>
        {% for viz in sheet.key_visualizations %}
            <li>{{ viz }}</li>
        {% endfor %}
        </ul>
        
        <p><strong>Insights to Look For:</strong></p>
        <ul>
        {% for insight in sheet.insights_to_look_for %}
            <li>{{ insight }}</li>
        {% endfor %}
        </ul>
    </div>
</div>
{% endfor %}
{% endif %}

<h2>📊 Visualization Guide</h2>
{% for viz in navigation.visualizations_guide %}
<div class="expand">
    <div class="expand-control">
        <span class="expand-control-text">{{ viz.visualization_title }} ({{ viz.type }})</span>
    </div>
    <div class="expand-content">
        <p><strong>Purpose:</strong> {{ viz.purpose }}</p>
        <p><strong>How to Read:</strong> {{ viz.how_to_read }}</p>
        
        {% if viz.interactive_features %}
        <p><strong>Interactive Features:</strong></p>
        <ul>
        {% for feature in viz.interactive_features %}
            <li>{{ feature }}</li>
        {% endfor %}
        </ul>
        {% endif %}
        
        {% if viz.common_actions %}
        <p><strong>Common Actions:</strong></p>
        <ul>
        {% for action in viz.common_actions %}
            <li>{{ action }}</li>
        {% endfor %}
        </ul>
        {% endif %}
    </div>
</div>
{% endfor %}

<h2>🔍 Filters and Parameters</h2>
<div class="panel" style="border-color: #f39c12; border-width: 1px;">
    <div class="panelHeader" style="border-color: #f39c12; background-color: #fdf2e9;">
        <strong>🎛️ Using Filters</strong>
    </div>
    <div class="panelContent">
        {% if navigation.filters_and_parameters.available_filters %}
        <p><strong>Available Filters:</strong></p>
        <ul>
        {% for filter in navigation.filters_and_parameters.available_filters %}
            <li>{{ filter }}</li>
        {% endfor %}
        </ul>
        {% endif %}
        
        <p><strong>How to Use Filters:</strong> {{ navigation.filters_and_parameters.how_to_use_filters }}</p>
        
        {% if navigation.filters_and_parameters.parameter_guidance %}
        <p><strong>Parameter Guidance:</strong> {{ navigation.filters_and_parameters.parameter_guidance }}</p>
        {% endif %}
    </div>
</div>

<h2>🎯 Common Use Cases</h2>
{% for use_case in use_cases %}
<div class="panel" style="border-color: #34495e; border-width: 1px;">
    <div class="panelHeader" style="border-color: #34495e; background-color: #ecf0f1;">
        <strong>{{ use_case.scenario }} ({{ use_case.user_role }})</strong>
    </div>
    <div class="panelContent">
        <p><strong>Steps:</strong></p>
        <ol>
        {% for step in use_case.steps %}
            <li>{{ step }}</li>
        {% endfor %}
        </ol>
        
        <p><strong>Expected Outcome:</strong> {{ use_case.expected_outcome }}</p>
        
        {% if use_case.tips %}
        <p><strong>💡 Tips:</strong></p>
        <ul>
        {% for tip in use_case.tips %}
            <li>{{ tip }}</li>
        {% endfor %}
        </ul>
        {% endif %}
    </div>
</div>
{% endfor %}

<h2>✅ Best Practices</h2>

{% for category, practices in best_practices.items() %}
<h3>{{ category.replace('_', ' ') | title }}</h3>
<ul>
{% for practice in practices %}
    <li>{{ practice }}</li>
{% endfor %}
</ul>
{% endfor %}

{% if navigation.troubleshooting %}
<h2>🔧 Troubleshooting</h2>
<div class="panel" style="border-color: #e74c3c; border-width: 1px;">
    <div class="panelHeader" style="border-color: #e74c3c; background-color: #fdedec;">
        <strong>⚠️ Common Issues and Solutions</strong>
    </div>
    <div class="panelContent">
        {% for item in navigation.troubleshooting %}
        <p><strong>Issue:</strong> {{ item.issue }}</p>
        <p><strong>Solution:</strong> {{ item.solution }}</p>
        <hr>
        {% endfor %}
    </div>
</div>
{% endif %}

<h2>📈 Dashboard Statistics</h2>
<div class="panel" style="border-color: #16a085; border-width: 1px;">
    <div class="panelHeader" style="border-color: #16a085; background-color: #e8f8f5;">
        <strong>📊 Technical Details</strong>
    </div>
    <div class="panelContent">
        <ul>
            <li><strong>Total Visualizations:</strong> {{ structure_overview.total_visualizations }}</li>
            <li><strong>Data Sources:</strong> {{ structure_overview.total_datasets }}</li>
            <li><strong>Interactive Parameters:</strong> {{ "Yes" if structure_overview.has_parameters else "No" }}</li>
            <li><strong>Filters Available:</strong> {{ "Yes" if structure_overview.has_filters else "No" }}</li>
        </ul>
    </div>
</div>

<hr>

<div style="font-size: 12px; color: #7f8c8d;">
    <p><em>📝 Documentation generated by {{ generation_info.generator }} on {{ generation_info.generated_date[:10] }}</em></p>
    <p><em>🔄 Dashboard last updated: {{ dashboard.last_updated[:10] if dashboard.last_updated else "Unknown" }}</em></p>
</div>
        """)
        
        return template.render(**context)
    
    def _generate_markdown(self, context: Dict[str, Any]) -> str:
        """Generate Markdown documentation."""
        
        template = Template("""
# 📊 {{ dashboard.name }} - User Guide

## 📋 Dashboard Overview

**Purpose:** {{ purpose.purpose }}
**Target Audience:** {{ purpose.target_audience }}
**Business Value:** {{ purpose.business_value }}
**Complexity Level:** {{ purpose.complexity_level | title }}
**Last Updated:** {{ dashboard.last_updated }}

## 🎯 Key Insights

{{ purpose.key_insights }}

## 🧭 Navigation Guide

### Dashboard Structure
{{ navigation.overview.dashboard_structure }}

### 💡 Quick Navigation Tips
{% for tip in navigation.overview.navigation_tips %}
- {{ tip }}
{% endfor %}

### Interactive Features
{% for feature in navigation.overview.key_interactions %}
- **{{ feature }}**
{% endfor %}

{% if navigation.sheets_guide %}
### 📑 Sheet-by-Sheet Guide
{% for sheet in navigation.sheets_guide %}
#### {{ sheet.sheet_name }}
**Purpose:** {{ sheet.purpose }}
**How to Use:** {{ sheet.how_to_use }}

**Key Visualizations:**
{% for viz in sheet.key_visualizations %}
- {{ viz }}
{% endfor %}

**Insights to Look For:**
{% for insight in sheet.insights_to_look_for %}
- {{ insight }}
{% endfor %}

{% endfor %}
{% endif %}

## 📊 Visualization Guide
{% for viz in navigation.visualizations_guide %}
### {{ viz.visualization_title }} ({{ viz.type }})
**Purpose:** {{ viz.purpose }}
**How to Read:** {{ viz.how_to_read }}

{% if viz.interactive_features %}
**Interactive Features:**
{% for feature in viz.interactive_features %}
- {{ feature }}
{% endfor %}
{% endif %}

{% if viz.common_actions %}
**Common Actions:**
{% for action in viz.common_actions %}
- {{ action }}
{% endfor %}
{% endif %}

{% endfor %}

## 🔍 Filters and Parameters

{% if navigation.filters_and_parameters.available_filters %}
**Available Filters:**
{% for filter in navigation.filters_and_parameters.available_filters %}
- {{ filter }}
{% endfor %}
{% endif %}

**How to Use Filters:** {{ navigation.filters_and_parameters.how_to_use_filters }}

{% if navigation.filters_and_parameters.parameter_guidance %}
**Parameter Guidance:** {{ navigation.filters_and_parameters.parameter_guidance }}
{% endif %}

## 🎯 Common Use Cases
{% for use_case in use_cases %}
### {{ use_case.scenario }} ({{ use_case.user_role }})

**Steps:**
{% for step in use_case.steps %}
1. {{ step }}
{% endfor %}

**Expected Outcome:** {{ use_case.expected_outcome }}

{% if use_case.tips %}
**💡 Tips:**
{% for tip in use_case.tips %}
- {{ tip }}
{% endfor %}
{% endif %}

{% endfor %}

## ✅ Best Practices

{% for category, practices in best_practices.items() %}
### {{ category.replace('_', ' ') | title }}
{% for practice in practices %}
- {{ practice }}
{% endfor %}

{% endfor %}

{% if navigation.troubleshooting %}
## 🔧 Troubleshooting

{% for item in navigation.troubleshooting %}
**Issue:** {{ item.issue }}
**Solution:** {{ item.solution }}

{% endfor %}
{% endif %}

## 📈 Dashboard Statistics
- **Total Visualizations:** {{ structure_overview.total_visualizations }}
- **Data Sources:** {{ structure_overview.total_datasets }}
- **Interactive Parameters:** {{ "Yes" if structure_overview.has_parameters else "No" }}
- **Filters Available:** {{ "Yes" if structure_overview.has_filters else "No" }}

---

*📝 Documentation generated by {{ generation_info.generator }} on {{ generation_info.generated_date[:10] }}*
*🔄 Dashboard last updated: {{ dashboard.last_updated[:10] if dashboard.last_updated else "Unknown" }}*
        """)
        
        return template.render(**context)
    
    def _generate_summary(self, context: Dict[str, Any]) -> str:
        """Generate a brief summary of the documentation."""
        
        summary_template = Template("""
        Comprehensive user guide for {{ dashboard.name }} dashboard. 
        This {{ purpose.complexity_level }} level dashboard is designed for {{ purpose.target_audience }}.
        
        Key features:
        - {{ structure_overview.total_visualizations }} interactive visualizations
        - {{ structure_overview.total_datasets }} data source{{ "s" if structure_overview.total_datasets != 1 else "" }}
        - {{ use_cases | length }} common use case{{ "s" if (use_cases | length) != 1 else "" }}
        - Comprehensive navigation and troubleshooting guidance
        
        Purpose: {{ purpose.purpose }}
        """)
        
        return summary_template.render(**context).strip()
    
    def _setup_templates(self):
        """Setup Jinja2 template environment."""
        # Could be expanded to load templates from files
        return None
    
    def save_documentation(self, documentation: Dict[str, str], output_dir: str = ".") -> List[str]:
        """
        Save documentation to files.
        
        Args:
            documentation: Generated documentation dictionary
            output_dir: Directory to save files
            
        Returns:
            List of saved file paths
        """
        try:
            import os
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            saved_files = []
            
            # Save HTML version
            html_path = os.path.join(output_dir, "dashboard_guide.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(documentation['confluence_html'])
            saved_files.append(html_path)
            
            # Save Markdown version
            md_path = os.path.join(output_dir, "dashboard_guide.md")
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(documentation['markdown'])
            saved_files.append(md_path)
            
            # Save JSON structure
            json_path = os.path.join(output_dir, "dashboard_structure.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(documentation['json_structure'])
            saved_files.append(json_path)
            
            logger.info(f"Saved documentation to {len(saved_files)} files")
            return saved_files
            
        except Exception as e:
            logger.error(f"Failed to save documentation: {e}")
            return []