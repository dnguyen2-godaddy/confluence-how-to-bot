# 🚀 QuickSight Dashboard Image Analyzer

AI-powered tool for analyzing QuickSight dashboard screenshots and automatically generating professional documentation with Confluence integration.

## ✨ Features

- 🧠 **AI-Powered Analysis**: Advanced dashboard analysis using AWS Bedrock Claude 3.5 Sonnet
- 📊 **Business Insights**: Comprehensive business intelligence and recommendations
- 📈 **Visualization Breakdown**: Detailed analysis of charts, KPIs, and data patterns
- ⚡ **Technical Assessment**: Performance evaluation and improvement suggestions
- 📝 **Auto-Documentation**: AI-generated professional how-to guides
- 🔗 **Confluence Integration**: Direct publishing to Confluence spaces
- 🔍 **Smart File Detection**: Automatically finds recent images in common locations

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

```bash
# Copy environment template
cp env.example .env

# Edit .env with your credentials
nano .env
```

Required settings:
- **AWS Credentials**: For Bedrock AI analysis
- **Confluence Settings**: For documentation publishing

### 3. Run the Analyzer

```bash
python dashboard_analyzer.py
```

## 📋 Supported Formats

- ✅ PNG (recommended)
- ✅ JPG/JPEG
- ✅ GIF
- ✅ WebP
- ✅ BMP
- ✅ Maximum file size: 10MB

## 🎯 Workflow

1. **📸 Upload Screenshot**: Drag & drop or select dashboard image
2. **🤖 AI Analysis**: Comprehensive dashboard analysis with AI
3. **📝 Generate Documentation**: Professional how-to guide creation
4. **🔗 Publish to Confluence**: Automatic publishing with custom titles

## 📊 Analysis Includes

### 📈 Dashboard Overview
- Title, purpose, and objectives
- Design quality and visual hierarchy
- Layout and visualization arrangement

### 📊 Visualization Breakdown
- Chart types and data analysis
- KPIs and performance indicators
- Time ranges and filters
- Data sources identification

### 💡 Business Insights
- Domain analysis (sales, finance, ops, etc.)
- Trends, patterns, and anomalies
- Performance indicators
- Key business metrics

### 🔧 Interactive Features
- Filter controls and parameters
- Navigation and drill-down capabilities
- Cross-filtering relationships

### 🎯 Business Value
- Target audience identification
- Decision-making scenarios
- Use case recommendations

### ⚠️ Technical Assessment
- Data quality indicators
- Performance considerations
- Error detection
- Mobile responsiveness

### 🚀 Improvement Recommendations
- Missing visualizations
- Layout enhancements
- Additional interactivity
- Accessibility improvements

## 📁 Project Structure

```
confluence-how-to-bot/
├── dashboard_analyzer.py           # Main application
├── utils/                         # Supporting utilities
│   ├── __init__.py
│   ├── config.py                  # Configuration management
│   ├── confluence_uploader.py     # Confluence API integration
│   └── quicksight_manager.py      # QuickSight API utilities
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── env.example                    # Environment template
├── DASHBOARD_ANALYZER_README.md   # Detailed usage guide
├── CONFLUENCE_SETUP.md           # Confluence integration guide
└── venv/                         # Virtual environment

```

## 🔧 Configuration Files

### AWS Credentials
```env
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_SESSION_TOKEN=your_aws_session_token_here  # For Okta/SAML
AWS_REGION=us-west-2
```

### Confluence Integration
```env
CONFLUENCE_URL=https://your-company.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_TOKEN=your_confluence_api_token_here
CONFLUENCE_SPACE_KEY=YOUR_SPACE_KEY
```

## 📚 Documentation

- **[Dashboard Analyzer Guide](DASHBOARD_ANALYZER_README.md)** - Detailed usage instructions
- **[Confluence Setup Guide](CONFLUENCE_SETUP.md)** - Complete Confluence integration setup

## 🛠️ Dependencies

- **boto3** - AWS SDK for Bedrock AI
- **requests** - HTTP library for Confluence API
- **python-dotenv** - Environment variable management

## 🎯 Use Cases

- **Business Intelligence Teams**: Analyze dashboard effectiveness
- **Training & Documentation**: Create user guides for dashboards  
- **Dashboard Audits**: Technical assessment and improvement recommendations
- **Knowledge Management**: Centralized dashboard documentation in Confluence

## 🔐 Security

- Environment-based credential management
- Secure API token handling
- No hardcoded credentials in code
- AWS IAM best practices

## 📈 Example Output

```markdown
# 📊 Dashboard User Guide: Sales Performance Scorecard

## 🎯 Purpose & Overview
This dashboard tracks key sales metrics and KPIs for the sales organization...

## 🚀 Getting Started
### Accessing the Dashboard
1. Navigate to QuickSight in your browser
2. Select the "Sales Performance" dashboard
...

## 📊 Understanding the Visualizations
### Revenue Trend Chart
- **What it shows:** Monthly revenue progression
- **How to read it:** Green indicates growth, red shows decline
...
```

## 🚀 Advanced Features

- **Smart Recent File Detection**: Automatically finds images in Desktop, Downloads, Pictures
- **Interactive Selection**: Choose from numbered list or enter custom path
- **Enhanced Error Handling**: Helpful error messages with solutions
- **Rich Output**: Professional reports with emojis and structured sections
- **Batch Processing**: Analyze multiple dashboards efficiently

## 💡 Tips for Best Results

- **Capture full dashboard view** including titles and legends
- **Ensure text is readable** at screenshot resolution
- **Use PNG format** for best quality
- **Include interactive elements** (filters, controls) in screenshot
- **Take screenshots at full resolution** for detailed analysis

## 📞 Support

For issues or questions:
1. Check the troubleshooting sections in documentation files
2. Verify your AWS credentials and Confluence permissions
3. Ensure image files meet format and size requirements

---

*Powered by AWS Bedrock and Claude 3.5 Sonnet AI*