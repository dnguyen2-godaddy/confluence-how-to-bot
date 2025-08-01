# 🚀 QuickSight & Redshift AI Analytics Platform

A comprehensive Python application that integrates **AWS QuickSight**, **Redshift**, and **Bedrock** to provide AI-powered business intelligence and dashboard analysis.

## ✨ Features

### 🎯 **Complete Analytics Suite**
- **📊 Redshift Data Querying** - Direct SQL queries with pandas integration
- **🚀 QuickSight Dashboard Management** - Create, manage, and embed dashboards
- **🤖 AI Dashboard Analysis** - Analyze QuickSight dashboards with Claude 3.5 Sonnet
- **🧠 AI Direct Data Analysis** - AI insights directly from your Redshift data
- **🔧 Connection Testing** - Comprehensive diagnostics for all services

### 🏢 **Corporate Ready**
- ✅ **Works with shared corporate dashboards**
- ✅ **Temporary AWS credentials support** (ASIA keys + session tokens)
- ✅ **Enterprise QuickSight environments**
- ✅ **Cross-account dashboard access**

### 🤖 **AI-Powered Insights**
- **Claude 3.5 Sonnet** integration via AWS Bedrock
- **Comprehensive business analysis** with actionable recommendations
- **Custom analysis prompts** for focused insights
- **Detailed JSON reports** with timestamped analysis

## 🛠 **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AWS Redshift  │    │ AWS QuickSight  │    │  AWS Bedrock    │
│   Data Source   │────│   Dashboards    │────│   Claude AI     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Python App     │
                    │  Main Interface │
                    └─────────────────┘
```

## 🚀 **Quick Start**

### 1. **Environment Setup**
```bash
# Clone the repository
git clone <your-repo-url>
cd confluence-how-to-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configure Environment**
Copy `env.example` to `.env` and fill in your credentials:

```bash
cp env.example .env
```

**Required Configuration:**
```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_SESSION_TOKEN=your_session_token_here  # For temporary credentials
AWS_REGION=us-west-2

# Redshift Configuration
REDSHIFT_HOST=your-redshift-host
REDSHIFT_DATABASE=your_database
REDSHIFT_PORT=5439
REDSHIFT_USER=your_username
REDSHIFT_PASSWORD=your_password
```

### 3. **Run the Application**
```bash
python main.py
```

## 📊 **Usage Guide**

### **Main Menu Options:**

```
🎯 Available Operations:
1. 📊 Query Redshift data
2. 🚀 Manage QuickSight dashboards
3. 🤖 AI Dashboard Analysis (Bedrock)
4. 🧠 AI Direct Data Analysis (Bedrock)
5. 🔧 Test connections
6. ❌ Exit
```

### **Option 1: Query Redshift Data**
- Executes predefined scorecard queries
- Returns pandas DataFrame with results
- Displays data preview and statistics

### **Option 2: QuickSight Management**
- List all dashboards in your account
- Generate embed URLs for dashboards
- Corporate dashboard support

### **Option 3: AI Dashboard Analysis** ⭐
- **NEW FEATURE**: Works with corporate shared dashboards!
- Analyzes QuickSight dashboards using AI
- Provides optimization recommendations
- Generates detailed analysis reports

### **Option 4: AI Direct Data Analysis**
- Analyzes Redshift data directly with AI
- No dashboard required
- Custom analysis prompts supported
- Comprehensive business insights

### **Option 5: Connection Testing**
- Tests Redshift connectivity
- Validates QuickSight access
- Verifies Bedrock model availability

## 🔧 **Key Files**

| File | Purpose |
|------|---------|
| `main.py` | Main application interface |
| `fixed_dashboard_analyzer.py` | Corporate dashboard analyzer (NEW!) |
| `direct_data_analyzer.py` | Direct data analysis with AI |
| `query_redshift.py` | Redshift data querying |
| `quicksight_setup.py` | Dashboard creation utilities |
| `utils/` | Core utility modules |

## 🏢 **Corporate Environment Support**

This application is specifically designed for **corporate AWS environments**:

### ✅ **Supported Scenarios:**
- **Shared QuickSight dashboards** from other AWS accounts
- **Corporate SSO** with temporary credentials (ASIA keys)
- **Enterprise QuickSight** with namespace-based access
- **Cross-account IAM roles** and permissions

### 🔧 **Technical Approach:**
- Uses **embed API approach** for shared dashboards
- Handles **session tokens** for temporary credentials
- Supports **corporate user ARNs** automatically
- **Graceful fallbacks** when direct API access is blocked

## 🤖 **AI Analysis Examples**

### **Dashboard Analysis Output:**
```
📊 DASHBOARD ANALYSIS REPORT
================================================================================
🆔 Dashboard ID: 8c447a9b-b83c-4f80-b53c-0b9f1719c516
📅 Analysis Date: 2025-07-31T16:40:37
✅ Access Status: SUCCESS - Accessible via embed URL
🔧 Method: Corporate embed API approach

🤖 AI Analysis:
- Dashboard accessibility and configuration review
- Optimization recommendations for performance
- Security and governance best practices
- User experience improvement suggestions
```

### **Direct Data Analysis Output:**
```
📊 BUSINESS SCORECARD ANALYSIS
================================================================================
📈 Data Records: 245
📊 Business Units: 1 (CARE & SERVICES)
📋 Metrics: 9 key performance indicators

🤖 AI Analysis:
- Performance metrics and trends analysis
- Target vs actual comparison
- Cost optimization opportunities
- Strategic recommendations
```

## 🛡 **Security Features**

- **Environment variable protection** (`.env` excluded from git)
- **Credential rotation support** for temporary AWS credentials
- **Session token handling** for enterprise environments
- **Secure embed URL generation** with configurable timeouts
- **Access logging** and audit trail capabilities

## 📋 **Requirements**

### **AWS Services:**
- **AWS Redshift** (Serverless or Provisioned)
- **AWS QuickSight** (Author/Admin permissions recommended)
- **AWS Bedrock** (Claude model access required)

### **Python Dependencies:**
```
pandas==2.3.1
redshift_connector==2.1.8
python-dotenv==1.1.1
boto3==1.39.17
botocore==1.39.17
requests==2.32.4
openai==1.12.0
atlassian-python-api==3.41.14
jinja2==3.1.3
markdown==3.5.2
```

## 🚨 **Troubleshooting**

### **Common Issues:**

**❌ "Dashboard not found"**
- Check if you're using the correct dashboard ID
- Verify the dashboard is accessible via QuickSight web interface
- For shared dashboards, ensure you have embed permissions

**❌ "Invalid security token"**
- Refresh your AWS temporary credentials
- Ensure `AWS_SESSION_TOKEN` is included for ASIA keys
- Check credential expiration time

**❌ "Unable to route to Redshift"**
- Verify Redshift endpoint accessibility
- Check security group configurations
- Ensure QuickSight has network access to Redshift

### **Getting Help:**
1. Check the **connection testing** option (Option 5)
2. Review AWS IAM permissions
3. Verify network connectivity between services

## 🎯 **Next Steps**

1. **Explore AI Analysis**: Try both dashboard and direct data analysis
2. **Custom Prompts**: Experiment with specific analysis focuses
3. **Integration**: Embed insights into your business workflows
4. **Scaling**: Set up automated analysis schedules

## 📝 **License**

This project is designed for internal business intelligence use. Please ensure compliance with your organization's AWS usage policies.

---

**🚀 Ready to unlock AI-powered insights from your QuickSight dashboards and Redshift data!**