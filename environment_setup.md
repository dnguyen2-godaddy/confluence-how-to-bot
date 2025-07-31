# Environment Setup Guide

## Configuration File Setup

⚠️ **Important**: Create a `.env` file in the project root with your actual credentials. You can copy the template:

```bash
cp env.example .env
# Then edit .env with your actual credentials
```

The `.env` file will be ignored by git for security.

```bash
# ========================================
# Confluence How-To Bot Configuration
# ========================================
# Copy this template to .env and fill in your actual values
# Never commit your .env file to version control!

# ========================================
# AWS Configuration (Required)
# ========================================
# AWS credentials for QuickSight dashboard access
# Get these from AWS IAM Console
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-west-2

# Required IAM Permissions:
# - quicksight:DescribeDashboard
# - quicksight:DescribeDashboardDefinition
# - quicksight:ListDashboards
# - quicksight:DescribeDataSet
# - quicksight:GetDashboardEmbedUrl (optional, for embedding)

# ========================================
# OpenAI Configuration (Required)
# ========================================
# OpenAI API key for AI-powered analysis
# Get this from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your_openai_api_key_here

# Note: The bot uses GPT-4 for intelligent analysis
# Ensure your account has sufficient credits and API access

# ========================================
# Confluence Configuration (Required)
# ========================================
# Confluence instance URL (Cloud or Server)
# For Confluence Cloud: https://your-company.atlassian.net
# For Confluence Server: https://confluence.your-company.com
CONFLUENCE_URL=https://your-company.atlassian.net

# Confluence username (usually your email address)
CONFLUENCE_USERNAME=your-email@company.com

# Confluence API Token (not your password!)
# For Cloud: Generate at https://id.atlassian.com/manage-profile/security/api-tokens
# For Server: Use your password or generate app password
CONFLUENCE_API_TOKEN=your_confluence_api_token_here

# Confluence Space Key where documentation will be uploaded
# Find this in your space settings (e.g., "DOCS", "KB", "HELP")
CONFLUENCE_SPACE_KEY=your_space_key

# Required Confluence Permissions:
# - Space: Create/Edit pages
# - Space: Add/Remove labels
# - Space: View space

# ========================================
# Optional: Redshift Configuration
# ========================================
# Only required if using the legacy scorecard query functionality
# Remove or leave empty if not using Redshift features

# Redshift cluster endpoint
REDSHIFT_HOST=your-redshift-cluster.region.redshift.amazonaws.com

# Database name
REDSHIFT_DATABASE=your_database_name

# Port (usually 5439)
REDSHIFT_PORT=5439

# Database username
REDSHIFT_USER=your_db_username

# Database password
REDSHIFT_PASSWORD=your_db_password
```

## Getting API Keys and Tokens

### AWS Credentials
1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Create a new user or use existing user
3. Attach policy with QuickSight permissions
4. Generate Access Key ID and Secret Access Key
5. Ensure QuickSight is enabled in your AWS account

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in to your account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Ensure your account has GPT-4 access and sufficient credits

### Confluence API Token
1. For **Confluence Cloud**:
   - Go to [Atlassian Account Security](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Click "Create API token"
   - Give it a descriptive name
   - Copy the generated token

2. For **Confluence Server**:
   - Use your regular password or create an app password
   - Check with your administrator for API access

### Finding Your Confluence Space Key
1. Go to your Confluence space
2. Click "Space settings" (gear icon)
3. Look for "Space details" section
4. The space key is usually 2-10 uppercase letters (e.g., "DOCS", "KB")

## Configuration Validation

Test your configuration by running:

```bash
python -c "from how_to_bot import HowToBot; bot = HowToBot(); print(bot.validate_configuration())"
```

Or use the interactive validator:

```bash
python how_to_bot.py
# Select option to test integrations
```

## Security Best Practices

### Environment File Security
- **Never commit `.env` files** to version control
- Add `.env` to your `.gitignore` file
- Use different configurations for dev/staging/production
- Store production secrets in secure secret management systems

### API Key Management
- **Rotate keys regularly** (quarterly recommended)
- **Use least-privilege access** - only grant necessary permissions
- **Monitor usage** and set up billing alerts
- **Revoke unused keys** immediately

### Access Control
- **AWS**: Use IAM roles with minimal QuickSight permissions
- **OpenAI**: Monitor API usage and set usage limits
- **Confluence**: Use dedicated service account with space-specific permissions

## Troubleshooting Common Issues

### Configuration Errors
```bash
# Check individual configurations
python -c "from utils.config import config; print('AWS:', config.validate_aws_config())"
python -c "from utils.config import config; print('AI:', config.validate_ai_config())"
python -c "from utils.config import config; print('Confluence:', config.validate_confluence_config())"
```

### API Connection Issues

**AWS/QuickSight**:
- Verify credentials have QuickSight permissions
- Check if QuickSight is enabled in your AWS account
- Confirm dashboard IDs exist and are accessible
- Ensure correct AWS region

**OpenAI**:
- Verify API key format (starts with `sk-`)
- Check account has sufficient credits
- Ensure GPT-4 model access
- Test with simple API call

**Confluence**:
- Verify URL format (include `https://`)
- Check API token is not expired
- Confirm space key exists and is accessible
- Test with simple page creation

### Permission Issues

**AWS IAM Policy Example**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "quicksight:DescribeDashboard",
                "quicksight:DescribeDashboardDefinition",
                "quicksight:ListDashboards",
                "quicksight:DescribeDataSet"
            ],
            "Resource": "*"
        }
    ]
}
```

**Confluence Permissions Needed**:
- View space
- Create page
- Edit page
- Add labels

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | Yes | AWS access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS secret key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | Yes | AWS region | `us-west-2` |
| `OPENAI_API_KEY` | Yes | OpenAI API key | `sk-...` |
| `CONFLUENCE_URL` | Yes | Confluence base URL | `https://company.atlassian.net` |
| `CONFLUENCE_USERNAME` | Yes | Confluence username | `user@company.com` |
| `CONFLUENCE_API_TOKEN` | Yes | Confluence API token | `ATATT3xFfGF0T...` |
| `CONFLUENCE_SPACE_KEY` | Yes | Target space key | `DOCS` |
| `REDSHIFT_HOST` | No | Redshift cluster host | `cluster.region.redshift.amazonaws.com` |
| `REDSHIFT_DATABASE` | No | Database name | `analytics` |
| `REDSHIFT_PORT` | No | Database port | `5439` |
| `REDSHIFT_USER` | No | Database username | `analyst` |
| `REDSHIFT_PASSWORD` | No | Database password | `password123` |

## Getting Started Checklist

- [ ] Copy template: `cp env.example .env`
- [ ] Add AWS credentials with QuickSight access
- [ ] Add OpenAI API key with GPT-4 access  
- [ ] Configure Confluence URL and credentials
- [ ] Set Confluence space key for uploads
- [ ] Test configuration: `python how_to_bot.py`
- [ ] Validate with a sample dashboard ID
- [ ] Review generated documentation
- [ ] Set up monitoring and alerts (optional)

For additional help, see the main [README.md](README.md) or run the troubleshooting commands above.