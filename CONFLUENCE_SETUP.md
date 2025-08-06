# 🔗 Confluence API Setup Guide

Complete guide to integrate your Dashboard Analyzer with Confluence for automatic documentation publishing.

## 📋 Prerequisites

- Confluence Cloud or Server/Data Center access
- Admin or space permissions to create/edit pages
- Basic understanding of API tokens

## 🚀 Quick Setup (5 minutes)

### **Step 1: Get Your Confluence Information**

1. **Confluence URL**: Your Atlassian site
   ```
   https://yourcompany.atlassian.net
   ```

2. **Space Key**: Find this in your Confluence space
   - Go to your space → Space Settings → General
   - Look for "Space Key" (usually 2-10 uppercase letters)

### **Step 2: Create API Token**

1. **Go to Atlassian Account Settings**:
   ```
   https://id.atlassian.com/manage-profile/security/api-tokens
   ```

2. **Create Token**:
   - Click "Create API token"
   - Name: "Dashboard Documentation Bot"
   - Copy the token immediately (you can't see it again!)

### **Step 3: Update .env File**

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

### **Step 4: Test Connection**

```bash
python dashboard_analyzer.py
# Choose option 2: "Generate how-to + publish to Confluence"
```

## 🛠️ Advanced Configuration

### **Confluence Server/Data Center**

For on-premise Confluence:

```env
CONFLUENCE_URL=https://confluence.yourcompany.com
CONFLUENCE_USERNAME=your-username
CONFLUENCE_API_TOKEN=your-password-or-token
```

### **Custom Space Configuration**

Different spaces for different dashboard types:

```env
# Main dashboard documentation space
CONFLUENCE_SPACE_KEY=DASHBOARDS

# Or department-specific spaces
# CONFLUENCE_SPACE_KEY=FINANCE
# CONFLUENCE_SPACE_KEY=SALES
```

## 📚 Confluence REST API Reference

### **Key API Endpoints Used**

```bash
# Authentication Test
GET /rest/api/user/current

# Find Existing Pages
GET /rest/api/content?title={title}&spaceKey={space}

# Create New Page
POST /rest/api/content

# Update Existing Page
PUT /rest/api/content/{id}
```

### **Content Format**

The uploader converts Markdown to Confluence Storage Format:

```markdown
# Header → <h1>Header</h1>
## Subheader → <h2>Subheader</h2>
**Bold** → <strong>Bold</strong>
- List item → <li>List item</li>
```

## 🔧 Troubleshooting

### **Common Issues**

#### **❌ "Failed to connect to Confluence"**
- Check your CONFLUENCE_URL (no trailing slash)
- Verify your username and API token
- Test manually: `curl -u email:token https://yoursite.atlassian.net/rest/api/user/current`

#### **❌ "Space not found"**
- Verify CONFLUENCE_SPACE_KEY is correct
- Check space permissions (you need create/edit access)
- Try browsing to: `https://yoursite.atlassian.net/spaces/YOURSPACEKEY`

#### **❌ "Permission denied"**
- Your user needs space admin or page creation permissions
- Contact your Confluence admin for access

#### **❌ "Page already exists"**
- The tool will update existing pages automatically
- Check for duplicate page titles in the space

### **Testing Your Setup**

```bash
# Quick connection test
python -c "
from utils.confluence_uploader import ConfluenceUploader
uploader = ConfluenceUploader()
print('✅ Connected!' if uploader.test_connection() else '❌ Failed!')
"
```

## 🎯 Usage Examples

### **Basic Documentation Publishing**

```bash
python dashboard_analyzer.py
# 1. Upload dashboard image
# 2. Choose option 2: "Generate how-to + publish to Confluence"
# 3. Enter custom title or use auto-generated
# 4. Documentation is automatically published!
```

### **Batch Processing Multiple Dashboards**

```bash
# Analyze multiple screenshots
for image in ~/dashboard-images/*.png; do
    echo "Processing: $image"
    python dashboard_analyzer.py <<< "$image"
done
```

## 📖 Official Documentation

- **Confluence Cloud REST API**: https://developer.atlassian.com/cloud/confluence/rest/v2/
- **Authentication Guide**: https://developer.atlassian.com/cloud/confluence/basic-auth-for-rest-apis/
- **Content API**: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/
- **API Tokens**: https://confluence.atlassian.com/cloud/api-tokens-938839638.html

## 🔐 Security Best Practices

### **API Token Security**

- ✅ Store tokens in `.env` file (never commit to git)
- ✅ Use descriptive token names
- ✅ Rotate tokens regularly (every 90 days)
- ✅ Limit token permissions to minimum required

### **Access Control**

- ✅ Create dedicated service account for automation
- ✅ Grant only necessary space permissions
- ✅ Monitor token usage in Atlassian admin

### **Content Safety**

- ✅ Review generated documentation before publishing
- ✅ Use staging space for testing
- ✅ Keep backups of important pages

## 🚀 Pro Tips

### **Organize Your Documentation**

1. **Create a Dashboard Documentation Space**
   - Space Key: `DASHBOARDS` or `DASH`
   - Template: Business Intelligence knowledge base

2. **Use Consistent Naming**
   - Format: `[Department] - [Dashboard Name] - User Guide`
   - Example: `Finance - Revenue Scorecard - User Guide`

3. **Create Parent Pages**
   - Main page: "Dashboard User Guides"
   - Child pages: Individual dashboard guides

### **Automation Ideas**

- **Scheduled Documentation Updates**: Run analyzer weekly for critical dashboards
- **Slack Notifications**: Alert teams when new documentation is published
- **Version Control**: Keep documentation in sync with dashboard changes

---

*Need help? Check the troubleshooting section or contact your Confluence administrator.*