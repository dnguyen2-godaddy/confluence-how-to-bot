# 🚀 QuickSight Dashboard Image Analyzer

Upload and analyze QuickSight dashboard screenshots with AI-powered insights.

## ✨ Features

- 🧠 **AI-Powered Analysis**: Advanced dashboard analysis using AWS Bedrock Claude 3.5 Sonnet
- 📊 **Business Insights**: Comprehensive business intelligence and recommendations
- 📈 **Visualization Breakdown**: Detailed analysis of charts, KPIs, and data patterns
- ⚡ **Technical Assessment**: Performance evaluation and improvement suggestions
- 📝 **Detailed Reports**: Professional markdown reports with structured insights
- 🔍 **Smart File Finder**: Automatically finds recent images in common locations

## 🚀 Quick Start

1. **Run the analyzer:**
   ```bash
   source venv/bin/activate
   python dashboard_analyzer.py
   ```

2. **Upload your screenshot:**
   - Choose from recently found images (numbered options)
   - Or enter the file path directly
   - Drag & drop files from Finder

3. **Get AI insights:**
   - Comprehensive dashboard analysis
   - Business intelligence recommendations
   - Technical improvements
   - Detailed markdown report

## 📋 Supported Formats

- ✅ PNG (recommended)
- ✅ JPG/JPEG
- ✅ GIF
- ✅ WebP
- ✅ BMP
- ✅ Maximum file size: 10MB

## 💡 Tips for Best Results

- **Capture the full dashboard view**
- **Include chart titles and legends**
- **Ensure text is readable**
- **Use PNG format for best quality**
- **Take screenshots at full resolution**

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

## 🔧 Configuration

Make sure your `.env` file contains:

```env
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_SESSION_TOKEN=your_aws_session_token_here  # For Okta/SAML
AWS_REGION=us-west-2
```

## 📁 Output

Analysis reports are saved as markdown files:
- **Filename**: `dashboard_analysis_[image_name]_[timestamp].md`
- **Format**: Structured markdown with sections
- **Content**: Complete AI analysis with actionable insights

## 🛠️ Troubleshooting

### Common Issues

**❌ Expired AWS Credentials**
- Refresh your Okta AWS credentials
- Update the `.env` file with new tokens

**❌ Image Not Found**
- Check the file path
- Use absolute paths
- Remove quotes around paths

**❌ Unsupported Format**
- Convert to PNG, JPG, or other supported formats
- Check file extension

**❌ File Too Large**
- Compress image (max 10MB)
- Reduce resolution if needed

## 🎯 Example Usage

```bash
# Start the analyzer
python dashboard_analyzer.py

# Follow prompts to:
# 1. Select a recent image (1-5) or enter path
# 2. Wait for AI analysis
# 3. Review generated markdown report
# 4. Analyze more images or quit
```

## 🚀 Advanced Features

- **Smart Recent Files**: Automatically finds images in Desktop, Downloads, Pictures
- **Interactive Selection**: Choose from numbered list or enter custom path
- **Enhanced Error Handling**: Helpful error messages with solutions
- **Rich Output**: Professional reports with emojis and structured sections

---

*Powered by AWS Bedrock and Claude 3.5 Sonnet AI*