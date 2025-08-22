"""
Confluence API Integration for Dashboard Documentation

Uploads dashboard documentation to Confluence using the atlassian-python-api library.
Based on working example_code.py implementation.
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

# Try to import atlassian library, fallback to requests if not available
ATLASSIAN_AVAILABLE = False
try:
    from atlassian import Confluence
    ATLASSIAN_AVAILABLE = True
except ImportError:
    ATLASSIAN_AVAILABLE = False
    print("Warning: atlassian-python-api not available, falling back to REST API")

logger = logging.getLogger(__name__)


class ConfluenceUploader:
    """Upload documentation to Confluence using atlassian-python-api library."""
    
    def __init__(self):
        """Initialize Confluence API client."""
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
            
            print(f"Confluence not configured. Missing: {', '.join(missing)}")
            print("Check your .env file and add the required Confluence settings.")
            return
        
        # Initialize Confluence client using atlassian library if available
        self.confluence = None
        if ATLASSIAN_AVAILABLE:
            try:
                self.confluence = Confluence(
                    url=self.confluence_url,
                    username=self.username,
                    password=self.api_token,
                    cloud=True
                )
                logger.info(f"🔗 Confluence client initialized using atlassian library: {self.confluence_url}")
            except Exception as e:
                logger.error(f"Failed to initialize atlassian Confluence client: {e}")
                self.confluence = None
        
        # Always setup REST API fallback
        auth_string = f"{self.username}:{self.api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # API base URL - ensure we're using the wiki endpoint
        if self.confluence_url and '/wiki' not in self.confluence_url:
            wiki_url = urljoin(self.confluence_url, '/wiki/')
        elif self.confluence_url:
            wiki_url = self.confluence_url
        else:
            wiki_url = 'http://localhost/wiki/'  # Fallback for testing
        
        self.api_base = urljoin(wiki_url, 'rest/api/')
        
        if self.confluence:
            logger.info(f"🔗 Confluence uploader initialized using atlassian library: {self.confluence_url}")
        else:
            logger.info(f"🔗 Confluence uploader initialized using REST API: {self.confluence_url}")
    
    def test_connection(self) -> bool:
        """Test Confluence API connection."""
        try:
            if hasattr(self, 'confluence') and self.confluence:
                # Use atlassian library if available
                try:
                    user_info = self.confluence.get_user_info_by_username(self.username)
                    if user_info:
                        logger.info(f"Confluence connection successful using atlassian library. User: {user_info.get('displayName', 'Unknown')}")
                        return True
                    else:
                        logger.error("Confluence connection failed using atlassian library")
                        return False
                except Exception as e:
                    logger.warning(f"atlassian library search failed, falling back to REST API: {e}")
                    # Fall through to REST API
            
            # Use REST API (either as fallback or primary)
            response = requests.get(
                urljoin(self.api_base, 'user/current'),
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_info = response.json()
                logger.info(f"Confluence connection successful using REST API. User: {user_info.get('displayName', 'Unknown')}")
                return True
            else:
                logger.error(f"Confluence connection failed using REST API: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Confluence connection error: {e}")
            return False
    
    def find_page_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Find an existing page by title in the configured space."""
        try:
            if hasattr(self, 'confluence') and self.confluence:
                # Use atlassian library if available
                try:
                    page = self.confluence.get_page_by_title(self.space_key, title, expand='version')
                    if page:
                        logger.info(f"Found existing page using atlassian library: {title} (ID: {page['id']})")
                        return page
                    else:
                        logger.info(f"No existing page found with title: {title}")
                        return None
                except Exception as e:
                    logger.warning(f"atlassian library search failed, falling back to REST API: {e}")
                    # Fall through to REST API
            
            # Use REST API (either as fallback or primary)
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
                    logger.info(f"Found existing page using REST API: {title} (ID: {page['id']})")
                    return page
                else:
                    logger.info(f"No existing page found with title: {title}")
                    return None
            else:
                logger.error(f"Failed to search for page using REST API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding page: {e}")
            return None
    
    def convert_markdown_to_confluence(self, markdown_content: str) -> str:
        """Convert markdown to Confluence storage format using proper markdown library."""
        try:
            import markdown
            from markdown.extensions import codehilite, tables, fenced_code
            
            # Configure markdown extensions for better conversion
            extensions = [
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'markdown.extensions.nl2br',
                'markdown.extensions.sane_lists'
            ]
            
            # Convert markdown to HTML
            html_content = markdown.markdown(markdown_content, extensions=extensions)
            
            # Post-process HTML for Confluence compatibility
            confluence_content = self._post_process_html_for_confluence(html_content)
            
            return confluence_content
            
        except ImportError:
            # Fallback to basic conversion if markdown library not available
            return self._basic_markdown_conversion(markdown_content)
    
    def _post_process_html_for_confluence(self, html_content: str) -> str:
        """Post-process HTML to ensure Confluence compatibility."""
        # Debug: Log what we're processing
        logger.info(f"Processing HTML content: {html_content[:200]}...")
        
        # For view content from dashboard analyzer, preserve the CSS styling
        if '<div style="text-align: left; max-width: 800px; margin: 0 auto;">' in html_content:
            logger.info(f"Detected view content with centering styling - preserving for view content type: {html_content[:200]}...")
            # When using content_type='view', preserve the CSS styling
            return html_content
        
        # For other HTML content, ensure proper structure
        if html_content.startswith('<div') or '<h2>' in html_content or '<h3>' in html_content or '<strong>' in html_content:
            logger.info(f"Detected HTML content - ensuring proper structure: {html_content[:200]}...")
            # Ensure proper spacing around headers for Confluence recognition
            html_content = html_content.replace('><h', '>\n<h')
            html_content = html_content.replace('</h>', '</h>\n')
            html_content = html_content.replace('\n\n\n', '\n\n')
            return html_content
        
        # Fallback to original processing for backward compatibility
        # Ensure proper paragraph structure
        if not html_content.startswith('<'):
            html_content = f'<p>{html_content}</p>'
        
        # Fix common HTML issues for Confluence
        html_content = html_content.replace('<p></p>', '')  # Remove empty paragraphs
        html_content = html_content.replace('\n\n', '</p><p>')  # Proper paragraph breaks
        
        return html_content
    
    def _process_inner_content(self, content: str) -> str:
        """Process inner content for Confluence compatibility."""
        # Don't wrap HTML content in paragraph tags - preserve existing HTML structure
        if not content.startswith('<'):
            # Only wrap plain text in paragraphs
            content = f'<p>{content}</p>'
        else:
            # Content already has HTML tags, preserve them
            # Just clean up any empty paragraphs
            content = content.replace('<p></p>', '')
            
            # Handle line breaks between HTML elements properly
            content = content.replace('\n\n', '\n')
        
        return content
    
    def _basic_markdown_conversion(self, markdown_content: str) -> str:
        """Basic markdown conversion as fallback (original implementation)."""
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
    
    def _convert_html_to_confluence_storage(self, html_content: str) -> str:
        """Convert HTML content to proper Confluence Storage Format for better rendering."""
        try:
            # Extract content from the centered container if it exists
            if '<div style="max-width: 800px; margin: 0 auto; text-align: left;">' in html_content:
                content_start = html_content.find('<div style="max-width: 800px; margin: 0 auto; text-align: left;">')
                content_end = html_content.rfind('</div>')
                
                if content_start != -1 and content_end != -1:
                    # Get the content inside the div (skip the opening div tag)
                    inner_content = html_content[content_start + 58:content_end].strip()
                    
                    # Clean up the inner content
                    # Remove any extra wrapper divs
                    if inner_content.startswith('<div') and inner_content.endswith('</div>'):
                        inner_content = inner_content[5:-6].strip()
                    
                    # Ensure proper spacing around headers for Confluence recognition
                    inner_content = inner_content.replace('><h', '>\n<h')
                    inner_content = inner_content.replace('</h>', '</h>\n')
                    
                    # Clean up any double line breaks
                    inner_content = inner_content.replace('\n\n\n', '\n\n')
                    
                    # Ensure headers have proper spacing for Confluence recognition
                    inner_content = inner_content.replace('<h1>', '\n<h1>')
                    inner_content = inner_content.replace('<h2>', '\n<h2>')
                    inner_content = inner_content.replace('<h3>', '\n<h3>')
                    inner_content = inner_content.replace('</h1>', '</h1>\n')
                    inner_content = inner_content.replace('</h2>', '</h2>\n')
                    inner_content = inner_content.replace('</h3>', '</h3>\n')
                    
                    # Clean up any double line breaks again
                    inner_content = inner_content.replace('\n\n\n', '\n\n')
                    
                    # Ensure headers are properly formatted for Confluence Storage Format
                    # Add proper spacing and ensure clean structure
                    inner_content = inner_content.replace('<h1>', '\n<h1>')
                    inner_content = inner_content.replace('<h2>', '\n<h2>')
                    inner_content = inner_content.replace('<h3>', '\n<h3>')
                    
                    # Return the cleaned content - Confluence will handle the rest
                    logger.info(f"Converted HTML to Confluence Storage Format: {inner_content[:200]}...")
                    return inner_content
            
            # If no wrapper div found, return the content as-is but cleaned up
            cleaned_content = html_content.strip()
            cleaned_content = cleaned_content.replace('><h', '>\n<h')
            cleaned_content = cleaned_content.replace('</h>', '</h>\n')
            cleaned_content = cleaned_content.replace('\n\n\n', '\n\n')
            
            # Ensure headers have proper spacing for Confluence recognition
            cleaned_content = cleaned_content.replace('<h1>', '\n<h1>')
            cleaned_content = cleaned_content.replace('<h2>', '\n<h2>')
            cleaned_content = cleaned_content.replace('<h3>', '\n<h3>')
            cleaned_content = cleaned_content.replace('</h1>', '</h1>\n')
            cleaned_content = cleaned_content.replace('</h2>', '</h2>\n')
            cleaned_content = cleaned_content.replace('</h3>', '</h3>\n')
            
            # Clean up any double line breaks again
            cleaned_content = cleaned_content.replace('\n\n\n', '\n\n')
            
            # Ensure headers are properly formatted for Confluence Storage Format
            # Add proper spacing and ensure clean structure
            cleaned_content = cleaned_content.replace('<h1>', '\n<h1>')
            cleaned_content = cleaned_content.replace('<h2>', '\n<h2>')
            cleaned_content = cleaned_content.replace('<h3>', '\n<h3>')
            
            logger.info(f"Cleaned HTML content: {cleaned_content[:200]}...")
            return cleaned_content
            
        except Exception as e:
            logger.error(f"Error converting HTML to Confluence Storage Format: {e}")
            return html_content  # Fallback to original content
    
    def _prepare_page_data(self, title: str, content: str, page_id: str = None, version: int = None) -> dict:
        """Prepare page data for Confluence API requests."""
        # Debug: Log what type of content we're processing
        logger.info(f"Preparing page data for title: {title}")
        logger.info(f"Content starts with: {content[:100]}...")
        
        # Content is now clean HTML from dashboard analyzer - ensure proper Confluence storage format
        if content.startswith('<div') or content.startswith('<h1>') or '<h2>' in content:
            logger.info("Detected clean HTML content - ensuring proper Confluence storage format")
            # Clean up content and ensure proper header formatting for anchor links
            storage_content = content.strip()
            
            # Ensure proper spacing around headers for Confluence anchor link generation
            storage_content = storage_content.replace('<h1>', '\n<h1>')
            storage_content = storage_content.replace('<h2>', '\n<h2>')
            storage_content = storage_content.replace('<h3>', '\n<h3>')
            storage_content = storage_content.replace('</h1>', '</h1>\n')
            storage_content = storage_content.replace('</h2>', '</h2>\n')
            storage_content = storage_content.replace('</h3>', '</h3>\n')
            
            # Add proper paragraph breaks after headers for Confluence processing
            storage_content = storage_content.replace('</h1>\n', '</h1>\n\n')
            storage_content = storage_content.replace('</h2>\n', '</h2>\n\n')
            storage_content = storage_content.replace('</h3>\n', '</h3>\n\n')
            
            # Clean up any extra line breaks
            storage_content = storage_content.replace('\n\n\n\n', '\n\n')
            storage_content = storage_content.replace('\n\n\n', '\n\n').strip()
        else:
            # Fallback processing for other content types
            logger.info("Processing other content types")
            storage_content = self._post_process_html_for_confluence(content)
        
        # Debug: Log final storage content
        logger.info(f"Final storage content: {storage_content[:200]}...")
        
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
                    'editor': {
                        'value': 'fabric'
                    },
                    'content-appearance-draft': {
                        'value': 'fixed-width'
                    },
                    'content-appearance-published': {
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
    
    def _create_page_raw_api(self, title: str, content: str) -> Optional[str]:
        """Create a Confluence page using raw REST API calls like example_code.py."""
        try:
            # Get parent page information (we'll use the space root)
            url = f"{self.confluence_url}/wiki/rest/api/content"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            auth = (self.username, self.api_token)
            
            # Create page data using the same structure as example_code.py
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
                        "editor": {
                            "value": "fabric"
                        },
                        "content-appearance-draft": {
                            "value": "fixed-width"
                        },
                        "content-appearance-published": {
                            "value": "fixed-width"
                        }
                    }
                }
            }
            
            logger.info("Making raw API page creation request like example_code.py")
            
            response = requests.post(url, headers=headers, auth=auth, data=json.dumps(create_page_data))
            
            if response.status_code == 200:
                result = response.json()
                page_url = urljoin(self.confluence_url, result['_links']['webui'])
                logger.info(f"Page created successfully using raw API: {title}")
                return page_url
            else:
                logger.error(f"Failed to create page using raw API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating page using raw API: {e}")
            return None
    
    def _make_page_request(self, method: str, url: str, page_data: dict, title: str) -> Optional[str]:
        """Make HTTP request to Confluence API for page operations."""
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
                logger.info(f"Page {method.lower()}ed successfully: {title}")
                return page_url
            else:
                logger.error(f"Failed to {method.lower()} page: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error {method.lower()}ing page: {e}")
            return None

    def create_page(self, title: str, content: str) -> Optional[str]:
        """Create a new Confluence page."""
        if hasattr(self, 'confluence') and self.confluence:
            # Use atlassian library if available
            try:
                # Use modern Confluence editor for proper header anchor generation
                response = self.confluence.create_page(
                    self.space_key,
                    title,
                    content,
                    parent_id=None,
                    type='page',
                    representation='storage',
                    editor='fabric'
                )
                if response:
                    page_url = response.get('_links', {}).get('webui', '')
                    if page_url:
                        # Convert relative URL to absolute
                        if page_url.startswith('/'):
                            page_url = f"{self.confluence_url}{page_url}"
                        logger.info(f"Page created successfully using atlassian library: {title}")
                        return page_url
                    else:
                        logger.error("Page created but no URL returned")
                        return None
                else:
                    logger.error("Failed to create page using atlassian library")
                    return None
            except Exception as e:
                logger.warning(f"atlassian library page creation failed, falling back to REST API: {e}")
                # Fall through to REST API
        
        # Fallback to REST API - try using the same approach as example_code.py
        try:
            # Use the raw API approach like example_code.py for better header processing
            return self._create_page_raw_api(title, content)
        except Exception as e:
            logger.warning(f"Raw API approach failed, falling back to standard REST API: {e}")
            page_data = self._prepare_page_data(title, content)
            return self._make_page_request('POST', urljoin(self.api_base, 'content'), page_data, title)
    
    def update_page(self, page_id: str, title: str, content: str, version: int) -> Optional[str]:
        """Update an existing Confluence page."""
        if hasattr(self, 'confluence') and self.confluence:
            # Use atlassian library if available
            try:
                response = self.confluence.update_page(
                    page_id,
                    title,
                    content,
                    type='page',
                    representation='storage',
                    editor='fabric'
                )
                if response:
                    page_url = response.get('_links', {}).get('webui', '')
                    if page_url:
                        # Convert relative URL to absolute
                        if page_url.startswith('/'):
                            page_url = f"{self.confluence_url}{page_url}"
                        logger.info(f"Page updated successfully using atlassian library: {title}")
                        return page_url
                    else:
                        logger.error("Page updated but no URL returned")
                        return None
                else:
                    logger.error("Failed to update page using atlassian library")
                    return None
            except Exception as e:
                logger.warning(f"atlassian library page update failed, falling back to REST API: {e}")
                # Fall through to REST API
        
        # Fallback to REST API
        page_data = self._prepare_page_data(title, content, page_id, version)
        return self._make_page_request('PUT', urljoin(self.api_base, f'content/{page_id}'), page_data, title)
    
    def upload_image(self, image_path: str, page_id: str) -> Optional[str]:
        """Upload an image as an attachment to a Confluence page."""
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
                    logger.error(f"Failed to upload image: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error uploading image {image_path}: {e}")
            return None

    def upload_content(self, title: str, content: str, content_type: str = 'markdown', images: list = None) -> Optional[str]:
        """Upload or update content to Confluence with embedded images."""
        if not all([self.confluence_url, self.username, self.api_token, self.space_key]):
            print("Confluence not properly configured")
            return None
        
        try:
            # Test connection first
            print("Testing Confluence connection...")
            if not self.test_connection():
                print("Failed to connect to Confluence")
                return None
            
            print(f"Processing content: {title}")
            
            # For new pages, we need to create the page first to get an ID for image uploads
            # Check if page already exists
            existing_page = self.find_page_by_title(title)
            
            if existing_page:
                page_id = existing_page['id']
                print(f"Updating existing page: {title}")
            else:
                print(f"Creating new page: {title}")
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
                print(f"Uploading {len(images)} images...")
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
                                print(f"Uploaded: {original_filename}")
                                print(f"Image URL: {image_url}")
                                print(f"Unique filename: {unique_filename}")
                                
                                # Extract the actual filename from the image URL
                                actual_filename = image_url.split('/')[-1]
                                print(f"Actual uploaded filename: {actual_filename}")
                                
                                # Create Confluence image macro for embedding using actual filename
                                image_embed = f'<ac:image ac:width="800"><ri:attachment ri:filename="{actual_filename}" /></ac:image>'
                                print(f"Image embed macro: {image_embed}")
                                image_embeds.append({
                                    'section': f"**Dashboard View {i}**",
                                    'embed': image_embed,
                                    'filename': actual_filename
                                })
                            else:
                                print(f"Failed to upload: {original_filename}")
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
            logger.error(f"Upload failed: {e}")
            print(f"Upload failed: {e}")
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
                    clean_filename = img_info['filename'].replace('.png', '').replace('.jpg', '').replace('.jpeg', '').replace('Screenshot ', '')
                    print(f"DEBUG: Processing image {j}: {clean_filename}")
                    print(f"DEBUG: Image embed macro: {img_info['embed']}")
                    
                    insert_point += f'  <h3>View {j}: {clean_filename}</h3>\n'
                    insert_point += f'  <div style="text-align: center;">\n'
                    insert_point += f'    {img_info["embed"]}\n'
                    insert_point += f'  </div>\n\n'
                
                print(f"DEBUG: Final content length: {len(insert_point)}")
                print(f"DEBUG: Final content ends with: {insert_point[-200:]}...")
                logger.info(f"Embedded {len(image_embeds)} images into content")
                return insert_point
            
            return content
            
        except Exception as e:
            logger.error(f"Error embedding images in content: {e}")
            print(f"DEBUG: Error in _embed_images_in_content: {e}")
            return content  # Return original content if embedding fails


def get_confluence_setup_guide() -> str:
    """Return setup instructions for Confluence integration."""
    return """
## Confluence API Setup Guide

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