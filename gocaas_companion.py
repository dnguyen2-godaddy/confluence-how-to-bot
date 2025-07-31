#!/usr/bin/env python3
"""
GoCaas Companion - AI-Powered QuickSight Dashboard Analyzer

This module provides AI-powered analysis of QuickSight dashboards,
offering insights, trend analysis, and recommendations.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
from utils.config import config
from utils.quicksight_manager import QuickSightManager
from query_redshift import run_scorecard_query

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GoCaasCompanion:
    """AI-powered companion for analyzing QuickSight dashboards."""
    
    def __init__(self):
        """Initialize the GoCaas companion."""
        self.quicksight = QuickSightManager()
        # Configure OpenAI (you'll need to add OPENAI_API_KEY to your .env)
        openai.api_key = getattr(config, 'openai_api_key', None)
        
    def analyze_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """
        Comprehensive AI analysis of a QuickSight dashboard.
        
        Args:
            dashboard_id: The QuickSight dashboard ID to analyze
            
        Returns:
            Analysis results with insights, trends, and recommendations
        """
        logger.info(f"Starting GoCaas analysis for dashboard: {dashboard_id}")
        
        try:
            # Step 1: Get dashboard metadata
            dashboard_data = self.quicksight.export_dashboard_data(dashboard_id)
            
            # Step 2: Get fresh data from Redshift
            raw_data = run_scorecard_query()
            
            # Step 3: Perform AI analysis
            analysis_results = {
                'dashboard_info': dashboard_data,
                'data_summary': self._summarize_data(raw_data),
                'trend_analysis': self._analyze_trends(raw_data),
                'performance_insights': self._analyze_performance(raw_data),
                'ai_recommendations': self._generate_ai_recommendations(raw_data),
                'anomaly_detection': self._detect_anomalies(raw_data),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            logger.info("GoCaas analysis completed successfully")
            return analysis_results
            
        except Exception as e:
            logger.error(f"GoCaas analysis failed: {e}")
            raise
    
    def _summarize_data(self, data) -> Dict[str, Any]:
        """Generate data summary statistics."""
        if data.empty:
            return {"status": "no_data", "message": "No data available for analysis"}
        
        summary = {
            "total_records": len(data),
            "date_range": {
                "start": data['metric_report_mst_month'].min(),
                "end": data['metric_report_mst_month'].max()
            },
            "business_units": data['business_unit'].unique().tolist(),
            "regions": data['region_name'].unique().tolist(),
            "metrics": data['metric_name'].unique().tolist(),
            "total_metric_value": float(data['metric_value'].sum()),
            "average_metric_value": float(data['metric_value'].mean()),
            "metric_value_std": float(data['metric_value'].std())
        }
        
        return summary
    
    def _analyze_trends(self, data) -> Dict[str, Any]:
        """Analyze trends in the data."""
        if data.empty:
            return {"status": "no_data"}
        
        # Group by month and calculate trends
        monthly_trends = data.groupby('metric_report_mst_month')['metric_value'].sum().sort_index()
        
        # Calculate month-over-month growth
        growth_rates = monthly_trends.pct_change().dropna()
        
        trends = {
            "monthly_totals": monthly_trends.to_dict(),
            "growth_rates": growth_rates.to_dict(),
            "average_growth_rate": float(growth_rates.mean()),
            "trend_direction": "increasing" if growth_rates.mean() > 0 else "decreasing",
            "volatility": float(growth_rates.std()),
            "best_month": monthly_trends.idxmax(),
            "worst_month": monthly_trends.idxmin()
        }
        
        return trends
    
    def _analyze_performance(self, data) -> Dict[str, Any]:
        """Analyze performance by different dimensions."""
        if data.empty:
            return {"status": "no_data"}
        
        performance = {
            "by_region": data.groupby('region_name')['metric_value'].agg(['sum', 'mean', 'count']).to_dict(),
            "by_metric": data.groupby('metric_name')['metric_value'].agg(['sum', 'mean', 'count']).to_dict(),
            "by_entry_type": data.groupby('entry_type')['metric_value'].agg(['sum', 'mean', 'count']).to_dict(),
            "top_performers": {
                "regions": data.groupby('region_name')['metric_value'].sum().nlargest(5).to_dict(),
                "metrics": data.groupby('metric_name')['metric_value'].sum().nlargest(5).to_dict()
            }
        }
        
        return performance
    
    def _detect_anomalies(self, data) -> List[Dict[str, Any]]:
        """Detect anomalies in the data."""
        if data.empty:
            return []
        
        anomalies = []
        
        # Detect outliers using IQR method
        Q1 = data['metric_value'].quantile(0.25)
        Q3 = data['metric_value'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = data[(data['metric_value'] < lower_bound) | (data['metric_value'] > upper_bound)]
        
        for _, row in outliers.iterrows():
            anomalies.append({
                "type": "outlier",
                "metric_name": row['metric_name'],
                "region_name": row['region_name'],
                "metric_value": float(row['metric_value']),
                "month": row['metric_report_mst_month'],
                "severity": "high" if row['metric_value'] > upper_bound else "low"
            })
        
        return anomalies
    
    def _generate_ai_recommendations(self, data) -> List[str]:
        """Generate AI-powered recommendations based on the data."""
        if data.empty:
            return ["No data available for recommendations"]
        
        try:
            # Prepare data summary for AI analysis
            summary = self._summarize_data(data)
            trends = self._analyze_trends(data)
            performance = self._analyze_performance(data)
            
            prompt = f"""
            As a business intelligence expert, analyze this scorecard data and provide actionable recommendations:

            Data Summary:
            - Total Records: {summary['total_records']}
            - Date Range: {summary['date_range']['start']} to {summary['date_range']['end']}
            - Business Units: {summary['business_units']}
            - Regions: {summary['regions']}
            - Total Metric Value: {summary['total_metric_value']}
            - Average Growth Rate: {trends['average_growth_rate']:.2%}
            - Trend Direction: {trends['trend_direction']}

            Top Performing Regions: {list(performance['top_performers']['regions'].keys())[:3]}
            
            Please provide 3-5 specific, actionable recommendations to improve performance.
            Focus on:
            1. Areas for improvement
            2. Growth opportunities
            3. Risk mitigation
            4. Operational efficiency
            
            Format as a bulleted list.
            """
            
            if openai.api_key:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a business intelligence expert providing data-driven recommendations."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                recommendations = response.choices[0].message.content.strip().split('\n')
                return [rec.strip('• -') for rec in recommendations if rec.strip()]
            else:
                # Fallback recommendations based on data patterns
                return self._generate_fallback_recommendations(summary, trends, performance)
                
        except Exception as e:
            logger.error(f"Failed to generate AI recommendations: {e}")
            return self._generate_fallback_recommendations(summary, trends, performance)
    
    def _generate_fallback_recommendations(self, summary, trends, performance) -> List[str]:
        """Generate basic recommendations when AI is not available."""
        recommendations = []
        
        if trends['trend_direction'] == 'decreasing':
            recommendations.append("📉 Investigate declining trend and implement corrective measures")
        
        if trends['volatility'] > 0.2:
            recommendations.append("📊 High volatility detected - consider stabilization strategies")
        
        # Find underperforming regions
        region_performance = performance['by_region']['sum']
        if region_performance:
            avg_performance = sum(region_performance.values()) / len(region_performance)
            underperformers = [region for region, value in region_performance.items() if value < avg_performance * 0.7]
            if underperformers:
                recommendations.append(f"🎯 Focus improvement efforts on underperforming regions: {', '.join(underperformers[:3])}")
        
        recommendations.append("📈 Monitor month-over-month growth rates to maintain positive trajectory")
        recommendations.append("🔍 Regular review of top-performing regions to identify best practices")
        
        return recommendations
    
    def generate_executive_summary(self, dashboard_id: str) -> str:
        """Generate an executive summary of the dashboard analysis."""
        analysis = self.analyze_dashboard(dashboard_id)
        
        summary = f"""
# 📊 Executive Dashboard Summary

**Analysis Date:** {analysis['analysis_timestamp']}
**Dashboard:** {analysis['dashboard_info']['name']}

## 📈 Key Metrics
- **Total Records:** {analysis['data_summary']['total_records']:,}
- **Total Metric Value:** ${analysis['data_summary']['total_metric_value']:,.2f}
- **Average Monthly Growth:** {analysis['trend_analysis']['average_growth_rate']:.2%}
- **Trend Direction:** {analysis['trend_analysis']['trend_direction'].title()}

## 🎯 Top Performing Regions
{chr(10).join([f"- {region}: ${value:,.2f}" for region, value in list(analysis['performance_insights']['top_performers']['regions'].items())[:3]])}

## ⚠️ Anomalies Detected
{len(analysis['anomaly_detection'])} anomalies requiring attention

## 💡 AI Recommendations
{chr(10).join([f"• {rec}" for rec in analysis['ai_recommendations'][:5]])}

---
*Generated by GoCaas Companion*
        """
        
        return summary.strip()


def main():
    """Main function for testing the GoCaas companion."""
    companion = GoCaasCompanion()
    
    # For testing, analyze the data directly
    try:
        logger.info("Testing GoCaas Companion with direct data analysis...")
        data = run_scorecard_query()
        
        analysis = {
            'data_summary': companion._summarize_data(data),
            'trend_analysis': companion._analyze_trends(data),
            'performance_insights': companion._analyze_performance(data),
            'anomaly_detection': companion._detect_anomalies(data),
            'ai_recommendations': companion._generate_ai_recommendations(data)
        }
        
        print("\n" + "="*60)
        print("🤖 GoCaas Companion Analysis Results")
        print("="*60)
        print(json.dumps(analysis, indent=2, default=str))
        
    except Exception as e:
        logger.error(f"Testing failed: {e}")


if __name__ == "__main__":
    main()