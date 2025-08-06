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
    
    def upload_image(self, image_path: str, page_id: str) -> Optional[str]:
        """Upload an image as an attachment to a Confluence page."""
        try:
            import mimetypes
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(image_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Prepare file for upload
            filename = os.path.basename(image_path)
            
            with open(image_path, 'rb') as f:
                files = {
                    'file': (filename, f, content_type)
                }
                
                headers = {
                    'X-Atlassian-Token': 'no-check'
                }
                
                url = f"{self.api_base}content/{page_id}/child/attachment"
                
                response = requests.post(
                    url,
                    files=files,
                    headers=headers,
                    auth=(self.username, self.api_token),
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    if 'results' in result and len(result['results']) > 0:
                        attachment_id = result['results'][0]['id']
                        # Return the attachment URL for embedding
                        return f"/wiki/download/attachments/{page_id}/{filename}"
                    return None
                else:
                    logger.error(f"Failed to upload image: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error uploading image {image_path}: {e}")
            return None

    def upload_content(self, title: str, content: str, content_type: str = 'markdown', images: list = None) -> Optional[str]:
        """Upload or update content to Confluence with embedded images."""
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
            
            # For new pages, we need to create the page first to get an ID for image uploads
            # Check if page already exists
            existing_page = self.find_page_by_title(title)
            
            if existing_page:
                page_id = existing_page['id']
                print(f"📄 Updating existing page: {title}")
            else:
                print(f"✨ Creating new page: {title}")
                # Create page with initial content
                page_url = self.create_page(title, content)
                if page_url and '/pages/' in page_url:
                    page_id = page_url.split('/pages/')[-1].split('/')[0]
                else:
                    return None
            
            # Upload images and get their attachment URLs
            image_embeds = []
            if images and page_id:
                print(f"📸 Uploading {len(images)} images...")
                for i, image_path in enumerate(images, 1):
                    if os.path.exists(image_path):
                        image_url = self.upload_image(image_path, page_id)
                        if image_url:
                            filename = os.path.basename(image_path)
                            print(f"✅ Uploaded: {filename}")
                            # Create Confluence image macro for embedding
                            image_embed = f'<ac:image ac:width="800"><ri:attachment ri:filename="{filename}" /></ac:image>'
                            image_embeds.append({
                                'section': f"**Dashboard View {i}**",
                                'embed': image_embed,
                                'filename': filename
                            })
                        else:
                            print(f"❌ Failed to upload: {os.path.basename(image_path)}")
                    else:
                        print(f"❌ Image not found: {image_path}")
            
            # Embed images into content if we have them
            if image_embeds:
                enhanced_content = self._embed_images_in_content(content, image_embeds)
            else:
                enhanced_content = content
            
            # Update page with embedded images
            if existing_page:
                page_url = self.update_page(
                    page_id,
                    title, 
                    enhanced_content,
                    existing_page['version']['number']
                )
            else:
                # Update the page we just created with image-embedded content
                temp_page = self.find_page_by_title(title)
                if temp_page:
                    page_url = self.update_page(
                        page_id,
                        title,
                        enhanced_content,
                        temp_page['version']['number']
                    )
            
            return page_url
            
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            print(f"❌ Upload failed: {e}")
            return None
    
    def _embed_images_in_content(self, content: str, image_embeds: list) -> str:
        """Embed images into the content at appropriate locations."""
        try:
            # Convert content to lines for easier manipulation
            lines = content.split('\n')
            enhanced_lines = []
            
            # Add images at the beginning after the Objective section
            image_section_added = False
            
            for i, line in enumerate(lines):
                enhanced_lines.append(line)
                
                # Add images section after the Objective section
                if not image_section_added and line.strip() and not line.startswith('**') and i > 0:
                    if lines[i-1].strip() == '**Objective**' or 'objective' in line.lower():
                        # Add a dashboard screenshots section
                        enhanced_lines.extend([
                            '',
                            '**Dashboard Screenshots**',
                            ''
                        ])
                        
                        # Add each image with a descriptive header
                        for j, img_info in enumerate(image_embeds, 1):
                            enhanced_lines.extend([
                                f"**View {j}: {img_info['filename'].replace('.png', '').replace('Screenshot ', '')}**",
                                '',
                                img_info['embed'],
                                ''
                            ])
                        
                        image_section_added = True
                        enhanced_lines.append('')  # Add spacing
            
            # If we didn't find a good place to insert, add at the end before any footer
            if not image_section_added and image_embeds:
                # Find the last substantive content line
                insert_index = len(enhanced_lines)
                for i in range(len(enhanced_lines) - 1, -1, -1):
                    if enhanced_lines[i].strip() and not enhanced_lines[i].startswith('**Documentation Information**'):
                        insert_index = i + 1
                        break
                
                # Insert images section
                enhanced_lines.insert(insert_index, '')
                enhanced_lines.insert(insert_index + 1, '**Dashboard Screenshots**')
                enhanced_lines.insert(insert_index + 2, '')
                
                insert_pos = insert_index + 3
                for j, img_info in enumerate(image_embeds, 1):
                    enhanced_lines.insert(insert_pos, f"**View {j}: {img_info['filename'].replace('.png', '').replace('Screenshot ', '')}**")
                    enhanced_lines.insert(insert_pos + 1, '')
                    enhanced_lines.insert(insert_pos + 2, img_info['embed'])
                    enhanced_lines.insert(insert_pos + 3, '')
                    insert_pos += 4
            
            return '\n'.join(enhanced_lines)
            
        except Exception as e:
            logger.error(f"Error embedding images in content: {e}")
            return content  # Return original content if embedding fails


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