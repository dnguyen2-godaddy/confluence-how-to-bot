# 🤖 Confluence How-To Bot

An AI-powered system that automatically analyzes QuickSight dashboards and generates comprehensive how-to documentation, then uploads it to Confluence. This bot uses advanced AI to understand dashboard structure, purpose, and usage patterns to create user-friendly guides.

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
├── how_to_bot.py        # AI-powered workflow orchestrator  
├── main.py              # Main application entry point
├── query_redshift.py    # Redshift query functionality
├── utils/               # Utility functions and modules
├── requirements.txt     # Python dependencies
├── env.example          # Environment configuration template
├── environment_setup.md # Detailed setup instructions
├── .env                 # Environment variables (not in git)
└── README.md           # This file
```

## Security

- Never commit the `.env` file to version control
- Keep database credentials secure
- Review `.gitignore` to ensure sensitive files are excluded

## 🌟 Core Features

### 🤖 AI-Powered Analysis
- **Dashboard Structure Analysis**: Deep analysis of QuickSight dashboard components
- **Purpose Identification**: AI determines dashboard purpose and target audience
- **Usage Pattern Recognition**: Identifies common use cases and workflows
- **Best Practice Generation**: Creates tailored recommendations

### 📝 Intelligent Documentation
- **Comprehensive User Guides**: Step-by-step how-to documentation
- **Interactive Navigation**: Clear guidance for dashboard navigation
- **Troubleshooting Guides**: Common issues and solutions
- **Multiple Formats**: HTML (Confluence), Markdown, and JSON outputs

### 🔗 Seamless Integration
- **QuickSight API**: Direct integration with AWS QuickSight
- **Confluence Upload**: Automatic upload to Confluence spaces
- **Local Export**: Save documentation locally for review
- **Version Control**: Track documentation versions and updates

### 🎯 Smart Workflow
- **One-Click Processing**: Complete workflow from dashboard ID to published documentation
- **Configuration Validation**: Automatic validation of all required settings
- **Error Recovery**: Graceful handling of failures with detailed logging
- **Batch Processing**: Support for multiple dashboards (future enhancement)

## 🛠️ Prerequisites

### Required Accounts & Services
1. **AWS Account** with QuickSight enabled
2. **OpenAI Account** for AI analysis capabilities
3. **Confluence Account** (Cloud or Server) for documentation upload
4. **QuickSight Dashboards** to analyze

### Required Permissions
- **AWS**: QuickSight read access, dashboard describe permissions
- **OpenAI**: API access for GPT-4 models
- **Confluence**: Space write permissions for documentation upload

## ⚙️ Environment Configuration

Create a `.env` file in the project root with your credentials. 

📋 **Quick Setup**: See **[Environment Setup Guide](environment_setup.md)** for detailed instructions including:
- How to get AWS credentials and QuickSight permissions
- How to obtain OpenAI API keys with GPT-4 access
- How to generate Confluence API tokens
- Troubleshooting common configuration issues

**Required Variables**:
```bash
# AWS (QuickSight access)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-west-2

# OpenAI (AI analysis)
OPENAI_API_KEY=sk-your_openai_api_key

# Confluence (documentation upload)
CONFLUENCE_URL=https://your-company.atlassian.net
CONFLUENCE_USERNAME=your_email@company.com
CONFLUENCE_API_TOKEN=your_confluence_api_token
CONFLUENCE_SPACE_KEY=your_space_key
```

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone <repository-url>
cd confluence-how-to-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create your `.env` file with the required credentials:

```bash
# Copy the example file and edit with your values
cp env.example .env
# Then fill in your actual credentials
```

See **[Environment Setup Guide](environment_setup.md)** for detailed configuration instructions and **`env.example`** for a quick template.

### 3. Launch the Bot
```bash
# Interactive mode with guided workflow
python how_to_bot.py

# Or use the main menu
python main.py
```

## 📋 Complete Workflow

### Automated Process
1. **Input**: Provide QuickSight Dashboard ID
2. **Analysis**: Bot analyzes dashboard structure and components
3. **AI Processing**: AI determines purpose, audience, and usage patterns
4. **Documentation**: Generates comprehensive how-to guide
5. **Upload**: Publishes to Confluence with proper formatting

### Example Usage
```python
from how_to_bot import HowToBot

# Initialize the bot
bot = HowToBot()

# Process a dashboard completely
results = bot.process_dashboard(
    dashboard_id='your-dashboard-id',
    upload_to_confluence=True,
    save_local=True
)

# Check results
if results['success']:
    print(f"Documentation available at: {results['stages']['confluence_upload']['page_url']}")
```

## 📊 What Gets Generated

### Documentation Includes:
- **📋 Dashboard Overview**: Purpose, audience, and business value
- **🧭 Navigation Guide**: Step-by-step navigation instructions
- **📊 Visualization Guide**: How to read and interact with each chart
- **🎯 Use Cases**: Real-world scenarios and workflows  
- **✅ Best Practices**: Tips for effective dashboard usage
- **🔧 Troubleshooting**: Common issues and solutions
- **📈 Technical Details**: Dashboard statistics and metadata

### Output Formats:
- **Confluence HTML**: Formatted for direct upload with panels and formatting
- **Markdown**: Clean markdown for documentation systems
- **JSON**: Structured data for programmatic use
- **Local Files**: Saved locally for review and backup

## 🔧 Advanced Usage

### Command Line Interface
```bash
# Direct workflow execution
python how_to_bot.py

# Dashboard analysis only (preview mode)
python -c "from how_to_bot import HowToBot; bot = HowToBot(); print(bot.analyze_dashboard_only('dashboard-id'))"
```

### API Integration
```python
from how_to_bot import HowToBot

bot = HowToBot()

# Validate configuration
validation = bot.validate_configuration()
if validation['all_valid']:
    # Test all integrations
    tests = bot.test_integrations()
    
    # Process dashboard
    results = bot.process_dashboard('your-dashboard-id')
```

### Batch Processing (Future Enhancement)
```python
# Process multiple dashboards
dashboard_ids = ['dash-1', 'dash-2', 'dash-3']
for dashboard_id in dashboard_ids:
    results = bot.process_dashboard(dashboard_id)
```

## 🎯 Example Output

Here's what the generated documentation looks like:

### Confluence Page Structure
```
📊 [Dashboard Name] - User Guide
├── 📋 Dashboard Overview
├── 🎯 Key Insights  
├── 🧭 Navigation Guide
│   ├── Dashboard Structure
│   ├── 💡 Quick Navigation Tips
│   ├── 📑 Sheet-by-Sheet Guide
│   └── 📊 Visualization Guide
├── 🔍 Filters and Parameters
├── 🎯 Common Use Cases
├── ✅ Best Practices
├── 🔧 Troubleshooting
└── 📈 Dashboard Statistics
```

## 🔍 Troubleshooting

### Common Issues

**Configuration Errors**
```bash
# Check your .env file
python -c "from utils.config import config; print(config.validate_aws_config())"
```

**API Connection Issues**
- Verify AWS credentials have QuickSight permissions
- Ensure OpenAI API key is valid and has credits
- Check Confluence API token and space permissions

**Dashboard Analysis Failures**
- Confirm dashboard ID exists and is accessible
- Verify dashboard is published (not in draft mode)
- Check AWS region configuration

### Logging
Detailed logs are available in the console output. For debugging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

This project uses several key technologies:
- **AWS QuickSight API** for dashboard analysis
- **OpenAI GPT-4** for intelligent documentation generation
- **Confluence API** for automated uploads
- **Jinja2** for template rendering
- **Python 3.8+** for core functionality

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs for detailed error messages
3. Verify all environment variables are correctly configured
4. Test each integration individually using the test functions

## 🔮 Future Enhancements

- **Batch Processing**: Process multiple dashboards simultaneously
- **Custom Templates**: User-defined documentation templates  
- **Multilingual Support**: Generate documentation in multiple languages
- **Version Tracking**: Track documentation versions and changes
- **Dashboard Monitoring**: Monitor dashboard changes and auto-update docs
- **Team Collaboration**: Multi-user workflows and approval processes