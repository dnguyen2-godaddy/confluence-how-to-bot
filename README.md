# Confluence How-To Bot

A Python application for querying Redshift data and potentially creating Confluence documentation.

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd confluence-how-to-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the project root with your database credentials:
   ```
   REDSHIFT_HOST=your-redshift-host
   REDSHIFT_DATABASE=your-database
   REDSHIFT_PORT=5439
   REDSHIFT_USER=your-username
   REDSHIFT_PASSWORD=your-password
   ```

5. **Run the application**
   ```bash
   python query_redshift.py
   ```

## Project Structure

```
confluence-how-to-bot/
├── main.py              # Main application entry point
├── query_redshift.py    # Redshift query functionality
├── utils/               # Utility functions
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
└── README.md           # This file
```

## Security

- Never commit the `.env` file to version control
- Keep database credentials secure
- Review `.gitignore` to ensure sensitive files are excluded

## QuickSight + GoCaas Integration

This application now includes **QuickSight dashboard creation** and **AI-powered analysis** through the **GoCaas companion**.

### Features

🔹 **Automated Dashboard Creation**: Programmatically create QuickSight dashboards from your Redshift data
🔹 **AI-Powered Analysis**: GoCaas companion provides intelligent insights and recommendations
🔹 **Trend Analysis**: Automated detection of patterns and anomalies in your data
🔹 **Executive Summaries**: Generate comprehensive business intelligence reports
🔹 **Embedded Dashboards**: Get embeddable URLs for integration into other applications

### QuickSight Setup

1. **Prerequisites**
   ```bash
   # Ensure AWS credentials are configured
   aws configure
   
   # Enable QuickSight in your AWS account
   # Visit: https://quicksight.aws.amazon.com/
   ```

2. **Environment Configuration**
   Add these variables to your `.env` file:
   ```
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_REGION=us-west-2
   OPENAI_API_KEY=your-openai-api-key  # Optional, for enhanced AI analysis
   ```

3. **Create QuickSight Dashboard**
   ```bash
   python setup_quicksight.py
   ```

4. **Analyze with GoCaas Companion**
   ```bash
   python gocaas_companion.py
   ```

### Usage Examples

```python
from gocaas_companion import GoCaasCompanion

# Initialize companion
companion = GoCaasCompanion()

# Analyze a dashboard
analysis = companion.analyze_dashboard('scorecard-dashboard')

# Generate executive summary
summary = companion.generate_executive_summary('scorecard-dashboard')
print(summary)
```

### GoCaas Analysis Features

- **📊 Data Summary**: Comprehensive statistics and metrics
- **📈 Trend Analysis**: Month-over-month growth patterns
- **🎯 Performance Insights**: Regional and metric-based performance analysis
- **⚠️ Anomaly Detection**: Automated identification of outliers
- **💡 AI Recommendations**: Business intelligence suggestions
- **📋 Executive Reports**: Professional summary documents