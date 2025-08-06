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

#### AWS Credentials (Required)
```env
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_SESSION_TOKEN=your_aws_session_token_here  # For Okta/SAML
AWS_REGION=us-west-2
```

#### Confluence Integration (Optional)
```env
CONFLUENCE_URL=https://your-company.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_TOKEN=your_confluence_api_token_here
CONFLUENCE_SPACE_KEY=YOUR_SPACE_KEY
```

### 3. Run the Analyzer

```bash
python dashboard_analyzer.py
```

## 🎯 How It Works

1. **📸 Upload Screenshot**: Select dashboard image from recent files or enter path
2. **🤖 AI Analysis**: Comprehensive dashboard analysis with AWS Bedrock
3. **📝 Generate Documentation**: Professional how-to guide creation
4. **🔗 Publish to Confluence**: Automatic publishing with custom titles (optional)

## 📋 Supported Formats

- ✅ PNG (recommended)
- ✅ JPG/JPEG
- ✅ GIF
- ✅ WebP
- ✅ BMP
- ✅ Maximum file size: 10MB

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
│   └── confluence_uploader.py     # Confluence API integration
├── outputs/                       # Generated analysis files
│   ├── .gitkeep                   # Keeps directory in git
│   ├── dashboard_analysis_*.md    # AI analysis reports
│   └── dashboard_howto_*.md       # Generated documentation
├── README.md                      # Complete documentation (this file)
├── requirements.txt               # Python dependencies
├── env.example                    # Environment template
└── venv/                         # Virtual environment
```

## 🔗 Confluence Setup Guide

### Prerequisites
- Confluence Cloud or Server/Data Center access
- Admin or space permissions to create/edit pages
- Basic understanding of API tokens

### Step 1: Get Your Confluence Information

1. **Confluence URL**: Your Atlassian site
   ```
   https://yourcompany.atlassian.net
   ```

2. **Space Key**: Find this in your Confluence space
   - Go to your space → Space Settings → General
   - Look for "Space Key" (usually 2-10 uppercase letters)

### Step 2: Create API Token

1. **Go to Atlassian Account Settings**:
   ```
   https://id.atlassian.com/manage-profile/security/api-tokens
   ```

2. **Create Token**:
   - Click "Create API token"
   - Name: "Dashboard Documentation Bot"
   - Copy the token immediately (you can't see it again!)

### Step 3: Update .env File

Add to your `.env` file:

```env
# ========================================
# Confluence Configuration
# ========================================
CONFLUENCE_URL=https://yourcompany.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_TOKEN=ATATT3xFfGF0T2... # Your API token
CONFLUENCE_SPACE_KEY=DASH # Your space key
```

### Step 4: Test Connection

```bash
python dashboard_analyzer.py
# Choose option 2: "Generate how-to + publish to Confluence"
```

## 🛠️ Troubleshooting

### Common Issues

#### ❌ **Expired AWS Credentials**
- **Solution**: Refresh your Okta AWS credentials
- Update the `.env` file with new `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN`

#### ❌ **Image Not Found**
- **Solution**: Check the file path
- Use absolute paths
- Remove quotes around paths
- Select from the numbered recent files list

#### ❌ **Unsupported Format**
- **Solution**: Convert to PNG, JPG, or other supported formats
- Check file extension

#### ❌ **File Too Large**
- **Solution**: Compress image (max 10MB)
- Reduce resolution if needed

#### ❌ **"Failed to connect to Confluence"**
- Check your CONFLUENCE_URL (no trailing slash)
- Verify your username and API token
- Test manually: `curl -u email:token https://yoursite.atlassian.net/rest/api/user/current`

#### ❌ **"Space not found"**
- Verify CONFLUENCE_SPACE_KEY is correct
- Check space permissions (you need create/edit access)
- Try browsing to: `https://yoursite.atlassian.net/spaces/YOURSPACEKEY`

#### ❌ **"Permission denied"**
- Your user needs space admin or page creation permissions
- Contact your Confluence admin for access

### Testing Your Setup

```bash
# Quick Confluence connection test
python -c "
from utils.confluence_uploader import ConfluenceUploader
uploader = ConfluenceUploader()
print('✅ Connected!' if uploader.test_connection() else '❌ Failed!')
"
```

## 💡 Tips for Best Results

- **Capture full dashboard view** including titles and legends
- **Ensure text is readable** at screenshot resolution
- **Use PNG format** for best quality
- **Include interactive elements** (filters, controls) in screenshot
- **Take screenshots at full resolution** for detailed analysis

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

## 🎯 Use Cases

- **Business Intelligence Teams**: Analyze dashboard effectiveness
- **Training & Documentation**: Create user guides for dashboards  
- **Dashboard Audits**: Technical assessment and improvement recommendations
- **Knowledge Management**: Centralized dashboard documentation in Confluence

## 🚀 Advanced Features

- **Smart Recent File Detection**: Automatically finds images in Desktop, Downloads, Pictures
- **Interactive Selection**: Choose from numbered list or enter custom path
- **Enhanced Error Handling**: Helpful error messages with solutions
- **Rich Output**: Professional reports with emojis and structured sections
- **Batch Processing**: Analyze multiple dashboards efficiently

## 🔐 Security Best Practices

### Environment Variables
- ✅ Store credentials in `.env` file (never commit to git)
- ✅ Use environment-based credential management
- ✅ No hardcoded credentials in code
- ✅ Follow AWS IAM best practices

### API Token Security
- ✅ Store tokens in `.env` file (never commit to git)
- ✅ Use descriptive token names
- ✅ Rotate tokens regularly (every 90 days)
- ✅ Limit token permissions to minimum required

### Access Control
- ✅ Create dedicated service account for automation
- ✅ Grant only necessary space permissions
- ✅ Monitor token usage in Atlassian admin

## 🛠️ Dependencies

- **boto3** - AWS SDK for Bedrock AI
- **requests** - HTTP library for Confluence API
- **python-dotenv** - Environment variable management

## 📖 Additional Resources

### Confluence API Documentation
- **Confluence Cloud REST API**: https://developer.atlassian.com/cloud/confluence/rest/v2/
- **Authentication Guide**: https://developer.atlassian.com/cloud/confluence/basic-auth-for-rest-apis/
- **Content API**: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/
- **API Tokens**: https://confluence.atlassian.com/cloud/api-tokens-938839638.html

### AWS Documentation
- **AWS Bedrock**: https://docs.aws.amazon.com/bedrock/
- **AWS IAM Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your AWS credentials and Confluence permissions
3. Ensure image files meet format and size requirements
4. Test connection using the provided test commands

---

*Powered by AWS Bedrock and Claude 3.5 Sonnet AI*