"""
Confluence API Integration for Dashboard Documentation

Uploads dashboard documentation to Confluence using the modern Confluence Cloud REST API.
Optimized for the updated Confluence Cloud editor with better formatting and structure.
"""

import json
import logging
import os
import requests
from base64 import b64encode
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urljoin

from . import config
from .image_utils import ImageProcessor

logger = logging.getLogger(__name__)


class ConfluenceUploader:
    """Upload documentation to Confluence using modern Confluence Cloud REST API."""
    
    def __init__(self):
        """Initialize Confluence Cloud API client."""
        self.confluence_url = getattr(config, 'confluence_url', None)
        self.username = getattr(config, 'confluence_username', None)
        self.api_token = getattr(config, 'confluence_api_token', None)
        self.space_key = getattr(config, 'confluence_space_key', None)
        
        # Validate configuration
        if not all([self.confluence_url, self.username, self.api_token, self.space_key]):
            missing = []
            if not self.confluence_url:
                missing.append("CONFLUENCE_URL")
            if not self.username:
                missing.append("CONFLUENCE_USERNAME")
            if not self.api_token:
                missing.append("CONFLUENCE_API_TOKEN")
            if not self.space_key:
                missing.append("CONFLUENCE_SPACE_KEY")
            
            print(f"Confluence Cloud not configured. Missing: {', '.join(missing)}")
            print("Check your .env file and add the required Confluence Cloud settings.")
            return
        
        # Setup modern Confluence Cloud REST API authentication
        auth_string = f"{self.username}:{self.api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Atlassian-Token': 'no-check'
        }
        
        # API base URL - ensure we're using the Confluence Cloud wiki endpoint
        if self.confluence_url and '/wiki' not in self.confluence_url:
            wiki_url = urljoin(self.confluence_url, '/wiki/')
        elif self.confluence_url:
            wiki_url = self.confluence_url
        else:
            wiki_url = 'http://localhost/wiki/'  # Fallback for testing
        
        # Use the newer Confluence Cloud API v2 for better Cloud Editor support
        self.api_base = urljoin(wiki_url, 'rest/api/')
        
        logger.info(f"Confluence Cloud uploader initialized with API v2: {self.confluence_url}")
    
    def test_connection(self) -> bool:
        """Test Confluence Cloud API connection."""
        try:
            # Use modern Confluence Cloud REST API
            response = requests.get(
                urljoin(self.api_base, 'user/current'),
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_info = response.json()
                logger.info(f"Confluence Cloud connection successful. User: {user_info.get('displayName', 'Unknown')}")
                return True
            else:
                logger.error(f"Confluence Cloud connection failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Confluence Cloud connection error: {e}")
            return False
    
    def find_page_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Find an existing page by title in the configured Confluence Cloud space."""
        try:
            # Use modern Confluence Cloud REST API
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
                    page = results[0]
                    logger.info(f"Found existing page in Confluence Cloud: {title} (ID: {page['id']})")
                    return page
                else:
                    logger.info(f"No existing page found with title: {title}")
                    return None
            else:
                logger.error(f"Failed to search for page in Confluence Cloud: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding page in Confluence Cloud: {e}")
            return None
    
    def _post_process_html_for_confluence(self, html_content: str) -> str:
        """Post-process HTML to ensure Confluence Cloud compatibility."""
        # Debug: Log what we're processing
        logger.info(f"Processing HTML content for Confluence Cloud: {html_content[:200]}...")
        
        # For view content from dashboard analyzer, preserve the CSS styling
        if '<div style="text-align: left; max-width: 800px; margin: 0 auto;">' in html_content:
            logger.info(f"Detected view content with centering styling - preserving for Confluence Cloud editor")
            # When using Confluence Cloud editor, preserve the CSS styling
            return html_content
        
        # Dashboard analyzer always provides clean HTML, so no structure manipulation needed
        return html_content
    
    def _prepare_page_data(self, title: str, content: str, page_id: str = None, version: int = None) -> dict:
        """Prepare page data for Confluence Cloud API requests."""
        # Debug: Log what type of content we're processing
        logger.info(f"Preparing page data for Confluence Cloud editor: {title}")
        logger.info(f"Content starts with: {content[:100]}...")
        
        # Content is now clean HTML from dashboard analyzer - ensure proper Confluence Cloud storage format
        if content.startswith('<div') or content.startswith('<h1>') or '<h2>' in content:
            logger.info("Detected clean HTML content - using as-is for Confluence Cloud storage format")
            # Dashboard analyzer provides clean HTML, use it directly
            storage_content = content.strip()
        else:
            # Fallback processing for other content types
            logger.info("Processing other content types for Confluence Cloud editor")
            storage_content = self._post_process_html_for_confluence(content)
        
        # Debug: Log final storage content
        logger.info(f"Final storage content for Confluence Cloud editor: {storage_content[:200]}...")
        
        # Force Cloud Editor usage with specific metadata properties
        logger.info("Forcing Confluence Cloud Editor usage with updated metadata structure")
        
        # Add CSS styling to ensure fixed-width for both title and content
        # This is needed because metadata properties only affect certain aspects
        if storage_content.startswith('<div'):
            # Content already has a wrapper div, add CSS to it
            storage_content = storage_content.replace(
                '<div style="text-align: left; max-width: 800px; margin: 0 auto;">',
                '<div style="text-align: left; max-width: 800px; margin: 0 auto; font-family: \'Monaco\', \'Menlo\', \'Ubuntu Mono\', monospace; font-size: 14px; line-height: 1.6;">'
            )
        else:
            # Wrap content in a styled div for fixed-width appearance
            storage_content = f'<div style="text-align: left; max-width: 800px; margin: 0 auto; font-family: \'Monaco\', \'Menlo\', \'Ubuntu Mono\', monospace; font-size: 14px; line-height: 1.6;">{storage_content}</div>'
        
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
            },
            'metadata': {
                'properties': {
                    # Force Cloud Editor - this is the key property
                    'editor': {
                        'value': 'fabric'
                    },
                    # Content appearance settings for Cloud Editor
                    'content-appearance-draft': {
                        'value': 'fixed-width'
                    },
                    'content-appearance-published': {
                        'value': 'fixed-width'
                    },
                    'content-type': {
                        'value': 'page'
                    },
                    'content-appearance': {
                        'value': 'fixed-width'
                    },
                    # Title appearance settings
                    'title-appearance': {
                        'value': 'fixed-width'
                    },
                    'title-appearance-draft': {
                        'value': 'fixed-width'
                    },
                    'title-appearance-published': {
                        'value': 'fixed-width'
                    }
                }
            }
        }
        
        # Add ID and version for updates
        if page_id:
            page_data['id'] = page_id
        if version is not None:
            page_data['version'] = {'number': version + 1}
        
        return page_data
    
    def _create_page_cloud_api(self, title: str, content: str) -> Optional[str]:
        """Create a Confluence Cloud page using modern REST API for cloud editor support."""
        try:
            # Use the newer Confluence Cloud API v2 for better Cloud Editor support
            url = f"{self.confluence_url}/wiki/rest/api/content"
            
            # Force Cloud Editor usage with correct metadata properties
            logger.info("Forcing Confluence Cloud Editor usage with updated metadata structure")
            
            # Create page data optimized for Confluence Cloud editor
            create_page_data = {
                "type": "page",
                "title": title,
                "status": "current",
                "space": {
                    "key": self.space_key
                },
                "body": {
                    "storage": {
                        "value": content,
                        "representation": "storage"
                    }
                },
                "metadata": {
                    "properties": {
                        # Force Cloud Editor - this is the key property
                        "editor": {
                            "value": "fabric"
                        },
                        # Content appearance settings for Cloud Editor
                        "content-appearance-draft": {
                            "value": "fixed-width"
                        },
                        "content-appearance-published": {
                            "value": "fixed-width"
                        },
                        "content-type": {
                            "value": "page"
                        },
                        "content-appearance": {
                            "value": "fixed-width"
                        },
                        # Title appearance settings
                        "title-appearance": {
                            "value": "fixed-width"
                        },
                        "title-appearance-draft": {
                            "value": "fixed-width"
                        },
                        "title-appearance-published": {
                            "value": "fixed-width"
                        }
                    }
                }
            }
            
            logger.info("Making Confluence Cloud API v2 page creation request for Cloud Editor")
            logger.info(f"Metadata properties: {create_page_data['metadata']}")
            logger.info(f"Full request data: {json.dumps(create_page_data, indent=2)}")
            
            response = requests.post(url, headers=self.headers, data=json.dumps(create_page_data))
            
            if response.status_code == 200:
                result = response.json()
                page_url = urljoin(self.confluence_url, result['_links']['webui'])
                logger.info(f"Page created successfully using Confluence Cloud API v2: {title}")
                logger.info(f"Response metadata: {result.get('metadata', 'No metadata in response')}")
                return page_url
            else:
                logger.error(f"Failed to create page using Confluence Cloud API v2: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating page using Confluence Cloud API v2: {e}")
            return None
    
    def _make_page_request(self, method: str, url: str, page_data: dict, title: str) -> Optional[str]:
        """Make HTTP request to Confluence Cloud API for page operations."""
        try:
            if method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, data=json.dumps(page_data), timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, data=json.dumps(page_data), timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code == 200:
                result = response.json()
                page_url = urljoin(self.confluence_url, result['_links']['webui'])
                logger.info(f"Page {method.lower()}ed successfully using Confluence Cloud API: {title}")
                return page_url
            else:
                logger.error(f"Failed to {method.lower()} page using Confluence Cloud API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error {method.lower()}ing page using Confluence Cloud API: {e}")
            return None

    def create_page(self, title: str, content: str) -> Optional[str]:
        """Create a new Confluence Cloud page using modern REST API for cloud editor support."""
        logger.info("Using Confluence Cloud REST API directly for cloud editor support")
        
        # Use the Confluence Cloud API approach for better cloud editor control
        try:
            return self._create_page_cloud_api(title, content)
        except Exception as e:
            logger.warning(f"Confluence Cloud API approach failed, falling back to standard REST API: {e}")
            page_data = self._prepare_page_data(title, content)
            return self._make_page_request('POST', urljoin(self.api_base, 'content'), page_data, title)
    
    def update_page(self, page_id: str, title: str, content: str, version: int) -> Optional[str]:
        """Update an existing Confluence Cloud page using modern REST API for cloud editor support."""
        logger.info("Using Confluence Cloud REST API directly for cloud editor support")
        
        # Use Confluence Cloud REST API directly for better cloud editor control
        page_data = self._prepare_page_data(title, content, page_id, version)
        return self._make_page_request('PUT', urljoin(self.api_base, f'content/{page_id}'), page_data, title)
    
    def upload_image(self, image_path: str, page_id: str) -> Optional[str]:
        """Upload an image as an attachment to a Confluence Cloud page."""
        try:
            # Validate image using centralized utilities
            is_valid, message = ImageProcessor.validate_image_file(image_path)
            if not is_valid:
                logger.warning(f"Skipping invalid image: {message}")
                return None
            
            # Get content type using centralized utilities
            content_type = ImageProcessor.get_media_type(image_path)
            
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
                    logger.error(f"Failed to upload image to Confluence Cloud: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error uploading image {image_path} to Confluence Cloud: {e}")
            return None

    def upload_content(self, title: str, content: str, content_type: str = 'markdown', images: list = None) -> Optional[str]:
        """Upload or update content to Confluence Cloud with embedded images using cloud editor."""
        if not all([self.confluence_url, self.username, self.api_token, self.space_key]):
            print("Confluence Cloud not properly configured")
            return None
        
        try:
            # Test connection first
            print("Testing Confluence Cloud connection...")
            if not self.test_connection():
                print("Failed to connect to Confluence Cloud")
                return None
            
            print(f"Processing content for Confluence Cloud editor: {title}")
            
            # For new pages, we need to create the page first to get an ID for image uploads
            # Check if page already exists
            existing_page = self.find_page_by_title(title)
            
            if existing_page:
                page_id = existing_page['id']
                print(f"Updating existing page with Confluence Cloud editor: {title}")
            else:
                print(f"Creating new page with Confluence Cloud editor: {title}")
                # Create page with initial content
                page_url = self.create_page(title, content)
                if page_url and '/pages/' in page_url:
                    page_id = page_url.split('/pages/')[-1].split('/')[0]
                else:
                    return None
            
            # Upload images and get their attachment URLs
            image_embeds = []
            print(f"DEBUG: images parameter: {images}")
            print(f"DEBUG: page_id: {page_id}")
            if images and page_id:
                print(f"Uploading {len(images)} images to Confluence Cloud...")
                for i, image_path in enumerate(images, 1):
                    # Clean and expand the image path
                    cleaned_path = os.path.expanduser(image_path.strip().strip('"').strip("'"))
                    
                    if os.path.exists(cleaned_path):
                        # Create unique filename to avoid conflicts
                        original_filename = os.path.basename(cleaned_path)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        unique_filename = f"{timestamp}_{i}_{original_filename}"
                        
                        # Create a temporary copy with unique name
                        import tempfile
                        import shutil
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(original_filename)[1]) as temp_file:
                            shutil.copy2(cleaned_path, temp_file.name)
                            temp_path = temp_file.name
                        
                        try:
                            # Upload the temporary file
                            image_url = self.upload_image(temp_path, page_id)
                            if image_url:
                                print(f"Uploaded to Confluence Cloud: {original_filename}")
                                print(f"Image URL: {image_url}")
                                print(f"Unique filename: {unique_filename}")
                                
                                # Extract the actual filename from the image URL
                                actual_filename = image_url.split('/')[-1]
                                print(f"Actual uploaded filename: {actual_filename}")
                                
                                # Create Confluence Cloud image macro for embedding using actual filename
                                image_embed = f'<ac:image ac:width="800"><ri:attachment ri:filename="{actual_filename}" /></ac:image>'
                                print(f"Image embed macro: {image_embed}")
                                image_embeds.append({
                                    'section': f"**Dashboard View {i}**",
                                    'embed': image_embed,
                                    'filename': actual_filename,
                                    'original_name': original_filename  # Add original filename for better naming
                                })
                            else:
                                print(f"Failed to upload to Confluence Cloud: {original_filename}")
                        finally:
                            # Clean up temporary file
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)
                    else:
                        print(f"Image not found: {cleaned_path}")
                        # Try to give more helpful information
                        if os.path.exists(image_path):
                            print(f"Note: Original path exists: {image_path}")
                        else:
                            print(f"Note: Original path also doesn't exist: {image_path}")
            
            # Embed images into content if we have them
            print(f"DEBUG: image_embeds count: {len(image_embeds) if image_embeds else 0}")
            if image_embeds:
                print(f"DEBUG: About to embed {len(image_embeds)} images")
                print(f"DEBUG: First image embed: {image_embeds[0] if image_embeds else 'None'}")
                enhanced_content = self._embed_images_in_content(content, image_embeds)
                print(f"DEBUG: Content length after embedding: {len(enhanced_content)}")
            else:
                print("DEBUG: No images to embed")
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
            logger.error(f"Upload to Confluence Cloud failed: {e}")
            print(f"Upload to Confluence Cloud failed: {e}")
            return None
    
    def _embed_images_in_content(self, content: str, image_embeds: list) -> str:
        """Embed images into the content at the very end."""
        try:
            print(f"DEBUG: _embed_images_in_content called with {len(image_embeds)} images")
            print(f"DEBUG: Content starts with: {content[:100]}...")
            
            # Always add images at the very end
            if image_embeds:
                # Simply append images at the end of the content
                insert_point = content + '\n\n  <h2>Dashboard Screenshots</h2>\n\n'
                print(f"DEBUG: Added Dashboard Screenshots header")
                
                # Add each image with simple formatting
                for j, img_info in enumerate(image_embeds, 1):
                    # Use original filename for better naming, fallback to actual filename if needed
                    display_name = img_info.get('original_name', img_info['filename'])
                    # Clean up the display name for better readability
                    clean_name = display_name.replace('.png', '').replace('.jpg', '').replace('.jpeg', '').replace('Screenshot ', '').replace('_', ' ').replace('-', ' ')
                    # Capitalize words for better appearance
                    clean_name = ' '.join(word.capitalize() for word in clean_name.split())
                    
                    print(f"DEBUG: Processing image {j}: {clean_name}")
                    print(f"DEBUG: Image embed macro: {img_info['embed']}")
                    
                    insert_point += f'  <h3>View {j}: {clean_name}</h3>\n'
                    insert_point += f'  <div style="text-align: center;">\n'
                    insert_point += f'    {img_info["embed"]}\n'
                    insert_point += f'  </div>\n\n'
                
                print(f"DEBUG: Final content length: {len(insert_point)}")
                print(f"DEBUG: Final content ends with: {insert_point[-200:]}...")
                logger.info(f"Embedded {len(image_embeds)} images into content for Confluence Cloud")
                return insert_point
            
            return content
            
        except Exception as e:
            logger.error(f"Error embedding images in content for Confluence Cloud: {e}")
            print(f"DEBUG: Error in _embed_images_in_content: {e}")
            return content  # Return original content if embedding fails


def get_confluence_setup_guide() -> str:
    """Return setup instructions for Confluence Cloud integration."""
    return """
## Confluence Cloud API Setup Guide

### 1. Get Your Confluence Cloud Information
- **Confluence Cloud URL**: Your Atlassian Cloud site (e.g., https://yourcompany.atlassian.net)
- **Username**: Your Atlassian Cloud email address
- **Space Key**: The space where you want to publish (find in space settings)

### 2. Create API Token
1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "Dashboard Documentation")
4. Copy the token (save it securely!)

### 3. Update Your .env File
Add these lines to your .env file:

```env
# Confluence Cloud Configuration
CONFLUENCE_URL=https://yourcompany.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_TOKEN=your_api_token_here
CONFLUENCE_SPACE_KEY=YOURSPACEKEY
```

### 4. Test Connection
Run the dashboard analyzer and try option 2 (Confluence Cloud publishing).

### 📚 Confluence Cloud API Documentation
- **Confluence Cloud REST API v2**: https://developer.atlassian.com/cloud/confluence/rest/v2/
- **Authentication Guide**: https://developer.atlassian.com/cloud/confluence/basic-auth-for-rest-apis/
- **Create Content API**: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-post
- **Cloud Editor Support**: Uses the updated Confluence Cloud editor with better formatting and structure
"""


if __name__ == "__main__":
    # Test the uploader
    uploader = ConfluenceUploader()
    print(get_confluence_setup_guide())