"""
Confluence API Integration for Dashboard Documentation

Uploads markdown documentation to Confluence using the REST API.
Supports both Confluence Cloud and Server/Data Center.
"""

import json
import logging
import os
import requests
from base64 import b64encode
from typing import Optional, Dict, Any
from urllib.parse import urljoin

from . import config

logger = logging.getLogger(__name__)


class ConfluenceUploader:
    """Upload documentation to Confluence via REST API."""
    
    def __init__(self):
        """Initialize Confluence API client."""
        self.confluence_url = getattr(config, 'confluence_url', None)
        self.username = getattr(config, 'confluence_username', None)
        self.api_token = getattr(config, 'confluence_api_token', None)
        self.space_key = getattr(config, 'confluence_space_key', None)
        
        # Validate configuration
        if not all([self.confluence_url, self.username, self.api_token, self.space_key]):
            missing = []
            if not self.confluence_url: missing.append('CONFLUENCE_URL')
            if not self.username: missing.append('CONFLUENCE_USERNAME')
            if not self.api_token: missing.append('CONFLUENCE_API_TOKEN')
            if not self.space_key: missing.append('CONFLUENCE_SPACE_KEY')
            
            logger.warning(f"Confluence configuration incomplete. Missing: {', '.join(missing)}")
            print(f"⚠️ Confluence not configured. Missing: {', '.join(missing)}")
            print("💡 Check your .env file and add the required Confluence settings.")
        
        # Setup authentication
        auth_string = f"{self.username}:{self.api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # API base URL - ensure we're using the wiki endpoint
        if '/wiki' not in self.confluence_url:
            wiki_url = urljoin(self.confluence_url, '/wiki/')
        else:
            wiki_url = self.confluence_url
        self.api_base = urljoin(wiki_url, 'rest/api/')
        
        logger.info(f"🔗 Confluence uploader initialized for: {self.confluence_url}")
    
    def test_connection(self) -> bool:
        """Test Confluence API connection."""
        try:
            response = requests.get(
                urljoin(self.api_base, 'user/current'),
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_info = response.json()
                logger.info(f"✅ Confluence connection successful. User: {user_info.get('displayName', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ Confluence connection failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Confluence connection error: {e}")
            return False
    
    def find_page_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Find an existing page by title in the configured space."""
        try:
            params = {
                'title': title,
                'spaceKey': self.space_key,
                'expand': 'version'
            }
            
            response = requests.get(
                urljoin(self.api_base, 'content'),
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    return results[0]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding page: {e}")
            return None
    
    def convert_markdown_to_confluence(self, markdown_content: str) -> str:
        """Convert markdown to Confluence storage format."""
        # Basic markdown to Confluence conversion
        # You might want to use a proper markdown->confluence converter library
        
        confluence_content = markdown_content
        
        # Convert headers
        confluence_content = confluence_content.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
        confluence_content = confluence_content.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
        confluence_content = confluence_content.replace('### ', '<h3>').replace('\n### ', '</h3>\n<h3>')
        confluence_content = confluence_content.replace('#### ', '<h4>').replace('\n#### ', '</h4>\n<h4>')
        
        # Convert bold and italic
        confluence_content = confluence_content.replace('**', '<strong>').replace('**', '</strong>')
        confluence_content = confluence_content.replace('*', '<em>').replace('*', '</em>')
        
        # Convert lists (basic conversion)
        lines = confluence_content.split('\n')
        converted_lines = []
        in_list = False
        
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    converted_lines.append('<ul>')
                    in_list = True
                list_item = line.strip()[2:]  # Remove '- '
                converted_lines.append(f'<li>{list_item}</li>')
            else:
                if in_list:
                    converted_lines.append('</ul>')
                    in_list = False
                converted_lines.append(line)
        
        if in_list:
            converted_lines.append('</ul>')
        
        confluence_content = '\n'.join(converted_lines)
        
        # Convert code blocks (basic)
        confluence_content = confluence_content.replace('```', '<code>')
        confluence_content = confluence_content.replace('`', '<code>').replace('`', '</code>')
        
        # Add basic structure
        confluence_content = f'<p>{confluence_content}</p>'
        confluence_content = confluence_content.replace('\n\n', '</p><p>')
        
        return confluence_content
    
    def create_page(self, title: str, content: str) -> Optional[str]:
        """Create a new Confluence page."""
        try:
            # Convert markdown to Confluence storage format
            if content.startswith('#') or '##' in content:
                storage_content = self.convert_markdown_to_confluence(content)
            else:
                # Assume it's already in storage format
                storage_content = content
            
            page_data = {
                'type': 'page',
                'title': title,
                'space': {
                    'key': self.space_key
                },
                'body': {
                    'storage': {
                        'value': storage_content,
                        'representation': 'storage'
                    }
                }
            }
            
            response = requests.post(
                urljoin(self.api_base, 'content'),
                headers=self.headers,
                data=json.dumps(page_data),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                page_url = urljoin(self.confluence_url, result['_links']['webui'])
                logger.info(f"✅ Page created successfully: {title}")
                return page_url
            else:
                logger.error(f"❌ Failed to create page: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating page: {e}")
            return None
    
    def update_page(self, page_id: str, title: str, content: str, version: int) -> Optional[str]:
        """Update an existing Confluence page."""
        try:
            # Convert markdown to Confluence storage format
            if content.startswith('#') or '##' in content:
                storage_content = self.convert_markdown_to_confluence(content)
            else:
                storage_content = content
            
            page_data = {
                'id': page_id,
                'type': 'page',
                'title': title,
                'space': {
                    'key': self.space_key
                },
                'body': {
                    'storage': {
                        'value': storage_content,
                        'representation': 'storage'
                    }
                },
                'version': {
                    'number': version + 1
                }
            }
            
            response = requests.put(
                urljoin(self.api_base, f'content/{page_id}'),
                headers=self.headers,
                data=json.dumps(page_data),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                page_url = urljoin(self.confluence_url, result['_links']['webui'])
                logger.info(f"✅ Page updated successfully: {title}")
                return page_url
            else:
                logger.error(f"❌ Failed to update page: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error updating page: {e}")
            return None
    
    def upload_content(self, title: str, content: str, content_type: str = 'markdown') -> Optional[str]:
        """Upload or update content to Confluence."""
        if not all([self.confluence_url, self.username, self.api_token, self.space_key]):
            print("❌ Confluence not properly configured")
            return None
        
        try:
            # Test connection first
            print("🔗 Testing Confluence connection...")
            if not self.test_connection():
                print("❌ Failed to connect to Confluence")
                return None
            
            print(f"📝 Processing content: {title}")
            
            # Check if page already exists
            existing_page = self.find_page_by_title(title)
            
            if existing_page:
                print(f"📄 Updating existing page: {title}")
                page_url = self.update_page(
                    existing_page['id'],
                    title,
                    content,
                    existing_page['version']['number']
                )
            else:
                print(f"✨ Creating new page: {title}")
                page_url = self.create_page(title, content)
            
            return page_url
            
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            print(f"❌ Upload failed: {e}")
            return None


def get_confluence_setup_guide() -> str:
    """Return setup instructions for Confluence integration."""
    return """
## 🔧 Confluence API Setup Guide

### 1. Get Your Confluence Information
- **Confluence URL**: Your Atlassian site (e.g., https://yourcompany.atlassian.net)
- **Username**: Your Atlassian email address
- **Space Key**: The space where you want to publish (find in space settings)

### 2. Create API Token
1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "Dashboard Documentation")
4. Copy the token (save it securely!)

### 3. Update Your .env File
Add these lines to your .env file:

```env
# Confluence Configuration
CONFLUENCE_URL=https://yourcompany.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_TOKEN=your_api_token_here
CONFLUENCE_SPACE_KEY=YOURSPACEKEY
```

### 4. Test Connection
Run the dashboard analyzer and try option 2 (Confluence publishing).

### 📚 API Documentation
- **Confluence Cloud REST API**: https://developer.atlassian.com/cloud/confluence/rest/v2/
- **Authentication Guide**: https://developer.atlassian.com/cloud/confluence/basic-auth-for-rest-apis/
- **Create Content API**: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-post
"""


if __name__ == "__main__":
    # Test the uploader
    uploader = ConfluenceUploader()
    print(get_confluence_setup_guide())