# QuickSight Dashboard Image Analyzer

An AI-powered tool that analyzes QuickSight dashboard screenshots and generates comprehensive documentation for GoDaddy stakeholders.

## Features

- **Image Analysis**: Upload QuickSight dashboard screenshots for AI analysis
- **Multi-Agent Workflow**: Sequential analysis using specialized AI agents
- **Documentation Generation**: Create comprehensive how-to guides and user documentation
- **Confluence Integration**: Automatically upload documentation to Confluence
- **QuickSight API Integration**: Direct access to dashboard metadata and structure
- **Image Optimization**: Compress and optimize images before upload
- **Multi-Platform Support**: Windows batch files and Unix shell scripts

## QuickSight API Integration 🆕

The tool now includes direct integration with the AWS QuickSight API, allowing you to access dashboard metadata, structure, and technical details without relying solely on image analysis.

### What You Can Access

- **Dashboard Metadata**: Names, IDs, creation dates, versions, and status
- **Structure Analysis**: Number of sheets, visuals, filters, and calculated fields
- **Dataset Information**: Data sources, types, and relationships
- **Technical Insights**: Complexity scores, performance considerations, and best practices
- **Raw Definitions**: Complete JSON structure of dashboard definitions

### Quick Start with QuickSight API

1. **Test the API Client**:
   ```bash
   python test_quicksight_api.py
   ```

2. **Use the Metadata Analyzer**:
   ```bash
   python quicksight_metadata_analyzer.py
   ```

3. **Direct API Usage**:
   ```python
   from utils.quicksight_client import QuickSightClient
   
   # Initialize client
   client = QuickSightClient(region_name='us-west-2', profile_name='your-profile')
   
   # List all dashboards
   dashboards = client.list_dashboards()
   
   # Get detailed metadata for a specific dashboard
   metadata = client.get_dashboard_metadata_summary('dashboard-id')
   
   # Export metadata to JSON
   client.export_dashboard_metadata('dashboard-id')
   ```

### Benefits of API Integration

- **Real-time Data**: Access current dashboard information, not just screenshots
- **Structured Information**: Get organized metadata instead of parsing images
- **Performance Insights**: Understand dashboard complexity and optimization opportunities
- **Automation Ready**: Integrate with CI/CD pipelines and automated workflows
- **Comprehensive Analysis**: Combine API data with image analysis for better insights

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/confluence-how-to-bot.git
   cd confluence-how-to-bot
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your credentials
   ```


### Option 1: Using Shell Scripts (Recommended)

#### For macOS/Linux:
```bash
# Make script executable (first time only)
chmod +x run_dashboard_analyzer.sh

# Run the dashboard analyzer
./run_dashboard_analyzer.sh

# Check environment only
./run_dashboard_analyzer.sh --check-only

# Show help
./run_dashboard_analyzer.sh --help
```

#### For Windows:
```cmd
# Run the dashboard analyzer
run_dashboard_analyzer.bat
```

### Option 2: Manual Execution

#### 1. Activate Virtual Environment
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate.bat
```

#### 2. Run the Program
```bash
python3 dashboard_analyzer.py
```

### User Experience

The program provides a **seamless, single-process experience**:

1. **Image Selection**: Choose one or multiple dashboard screenshots
2. **AI Analysis**: Automatic analysis happens in the background
3. **Documentation**: Comprehensive documentation is generated
4. **Confluence Upload**: Optional direct upload to Confluence

**No technical complexity** - users simply select images and get professional documentation!

### 🔧 Technical Architecture

Behind the scenes, the system uses a specialized AI workflow:

- **Agent 1: Dashboard Intelligence** - Analyzes images and extracts structured data
- **Agent 2: Documentation Architect** - Creates comprehensive documentation from analysis data

The agents work sequentially and automatically, providing users with a smooth, professional experience.

## How It Works

1. **Upload Screenshot**: Select dashboard image from recent files or enter path
2. **AI Analysis**: Comprehensive dashboard analysis with AWS Bedrock
3. **Generate Documentation**: Professional how-to guide creation
4. **Publish to Confluence**: Automatic publishing with custom titles (optional)

## Supported Formats

### Supported Formats

- PNG (recommended)
- JPG/JPEG
- GIF
- WebP
- BMP
- Maximum file size: 10MB

## Analysis Includes

### Dashboard Overview
- Title, purpose, and objectives
- Design quality and visual hierarchy
- Layout and visualization arrangement

### Visualization Breakdown
- Chart types and data analysis
- KPIs and performance indicators
- Time ranges and filters
- Data sources identification

### Business Insights

- Dashboard purpose and business objectives
- Key performance indicators (KPIs) identification
- Business context and stakeholder value
- Actionable recommendations for improvement

### Interactive Features

- Filter and control analysis
- Drill-down capabilities
- Navigation patterns
- User interaction workflows

### Technical Assessment

- Performance metrics evaluation
- Data source identification
- Refresh schedule analysis
- Technical improvement suggestions

### Improvement Recommendations

- Dashboard optimization suggestions
- User experience enhancements
- Performance improvements
- Best practices recommendations

## Project Structure

```
confluence-how-to-bot/
├── dashboard_analyzer.py      # Main application
├── utils/
│   ├── config.py             # Configuration management
│   ├── image_utils.py        # Image processing utilities
│   └── confluence_uploader.py # Confluence integration
├── outputs/                  # Generated documentation
├── requirements.txt          # Python dependencies
└── .env                     # Environment configuration
```

## Confluence Setup Guide

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

#### **Expired AWS Credentials**
```
Error: InvalidClientTokenId
Solution: Refresh your AWS credentials in Okta
```

#### **Image Not Found**
```
Error: NoSuchKey or file not found
Solution: Verify the image file path exists
```

#### **Unsupported Format**
```
Error: Unsupported format
Solution: Use PNG, JPG, JPEG, GIF, WebP, or BMP
```

#### **File Too Large**
```
Error: File size exceeds 10MB
Solution: Compress or resize the image
```

#### **"Failed to connect to Confluence"**
```
Error: Connection timeout or authentication failure
Solution: Check your Confluence URL and API token
```

#### **"Space not found"**
```
Error: Confluence space key is invalid
Solution: Verify the space key in your .env file
```

#### **"Permission denied"**
```
Error: Insufficient permissions
Solution: Check your Confluence user permissions
```

### Testing Your Setup

Test your Confluence connection:
```python
from utils.confluence_uploader import ConfluenceUploader
uploader = ConfluenceUploader()
print('Connected!' if uploader.test_connection() else 'Failed!')
```

## Tips for Best Results

- **Image Quality**: Use high-resolution screenshots (PNG recommended)
- **Full Context**: Capture entire dashboard views, not just sections
- **Text Readability**: Ensure all text and labels are clearly visible
- **Multiple Views**: Include different dashboard perspectives for comprehensive analysis
- **Recent Data**: Use current dashboard screenshots for up-to-date analysis

## Example Output

```markdown
# Dashboard User Guide: Sales Performance Scorecard

## Purpose & Overview
This dashboard tracks key sales metrics and KPIs for the sales organization...

## Getting Started
### Accessing the Dashboard
1. Navigate to QuickSight in your browser
2. Select the "Sales Performance" dashboard
...

## Understanding the Visualizations
### Revenue Trend Chart
- **What it shows:** Monthly revenue progression
- **How to read it:** Green indicates growth, red shows decline
...
```

## Use Cases

- **Business Intelligence Teams**: Analyze dashboard effectiveness
- **Training & Documentation**: Create user guides for dashboards  
- **Dashboard Audits**: Technical assessment and improvement recommendations
- **Knowledge Management**: Centralized dashboard documentation in Confluence

## Advanced Features

- **Multi-Image Analysis**: Analyze multiple dashboard views simultaneously
- **Confluence Integration**: Direct publishing with proper formatting
- **AWS SSO Integration**: Seamless authentication with Okta
- **Professional Output**: Business-ready documentation generation

## Security Best Practices

### Environment Variables
- Store credentials in `.env` file (never commit to git)
- Use environment-based credential management
- No hardcoded credentials in code
- Follow AWS IAM best practices

## Troubleshooting

### GoDaddy Okta SSO Issues

**Problem: "ExpiredTokenException" or authentication errors**
```
Solution: Your Okta session has expired (1 hour limit)
1. Re-run any AWS command to trigger automatic re-authentication
2. Enter your Okta credentials when prompted
3. Use YubiKey for MFA when requested
```

**Problem: "aws-okta-processor not found"**
```
Solution: Contact GoDaddy IT to install aws-okta-processor
- Usually pre-installed on corporate laptops
- Required for GoDaddy AWS access
```

**Problem: "Access Denied" for Bedrock**
```
Solution: Verify you're using the correct role
1. Check: aws sts get-caller-identity --profile default
2. Should show: GD-AWS-USA-GD-AISummerCa-Dev-Private-PowerUser
3. Contact AI team if using different role
```

**Problem: YubiKey not working**
```
Solution: YubiKey hardware token issues
1. Ensure YubiKey is properly inserted
2. Try different USB port
3. Contact IT if YubiKey is damaged
```

### API Token Security
- Store tokens in `.env` file (never commit to git)
- Use descriptive token names
- Rotate tokens regularly (every 90 days)
- Limit token permissions to minimum required

### Access Control
- Create dedicated service account for automation
- Grant only necessary space permissions
- Monitor token usage in Atlassian admin

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