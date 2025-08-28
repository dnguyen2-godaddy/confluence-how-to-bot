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
            'X-Atlassian-Token': 'no-check',
            # Force Cloud Editor usage
            'X-Editor-Version': '2',
            'X-Content-Appearance': 'fixed-width'
        }
        
        # API base URL - ensure we're using the Confluence Cloud wiki endpoint consistently
        if self.confluence_url and '/wiki' not in self.confluence_url:
            wiki_url = urljoin(self.confluence_url, '/wiki/')
        elif self.confluence_url:
            wiki_url = self.confluence_url
        else:
            wiki_url = 'https://your-company.atlassian.net/wiki/'  # Fallback for testing
        
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
    
    def _get_cloud_editor_metadata(self) -> dict:
        """Get standardized Cloud Editor metadata properties."""
        return {
            "properties": {
                # Core Cloud Editor properties
                "content-appearance": {"value": "fixed-width"},
                "editor": {"value": "v2"},
                "editor-version": {"value": "2"},
                
                # Draft and published versions
                "content-appearance-draft": {"value": "fixed-width"},
                "content-appearance-published": {"value": "fixed-width"},
                "editor-draft": {"value": "v2"},
                "editor-published": {"value": "v2"},
                "editor-version-draft": {"value": "2"},
                "editor-version-published": {"value": "2"},
                
                # Content type and status
                "content-type": {"value": "page"},
                "content-type-draft": {"value": "page"},
                "content-type-published": {"value": "page"},
                "status": {"value": "current"},
                "status-draft": {"value": "current"},
                "status-published": {"value": "current"}
            }
        }

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
        
        # Ensure Cloud Editor compatibility
        storage_content = self._ensure_cloud_editor_compatibility(storage_content)
        
        # Debug: Log final storage content
        logger.info(f"Final storage content for Confluence Cloud editor: {storage_content[:200]}...")
        
        # Force Cloud Editor usage with specific metadata properties
        logger.info("Forcing Confluence Cloud Editor usage with updated metadata structure")
        logger.info("Fixed-width appearance enforced for Cloud Editor compatibility")
        
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
            'metadata': self._get_cloud_editor_metadata()
        }
        
        # Add ID and version for updates
        if page_id:
            page_data['id'] = page_id
        if version is not None:
            page_data['version'] = {'number': version + 1}
        
        return page_data
    

    
    def _create_page_with_cloud_editor_v2(self, title: str, content: str) -> Optional[str]:
        """Create a Confluence Cloud page using the latest API approach for Cloud Editor."""
        try:
            # Use the standard Confluence Cloud API endpoint
            url = f"{self.confluence_url}/wiki/rest/api/content"
            
            logger.info("Using Confluence Cloud API with enhanced Cloud Editor forcing")
            
            # Ensure Cloud Editor compatibility
            storage_content = self._ensure_cloud_editor_compatibility(content)
            
            # Create page data with enhanced Cloud Editor properties
            create_page_data = {
                "type": "page",
                "title": title,
                "status": "current",
                "space": {
                    "key": self.space_key
                },
                "body": {
                    "storage": {
                        "value": storage_content,
                        "representation": "storage"
                    }
                },
                "metadata": self._get_cloud_editor_metadata()
            }
            
            logger.info("Making enhanced Confluence Cloud API request for Cloud Editor")
            logger.info(f"Enhanced metadata properties: {create_page_data['metadata']}")
            
            # Try with enhanced headers
            enhanced_headers = self.headers.copy()
            enhanced_headers.update({
                'X-Editor-Version': '2',
                'X-Content-Appearance': 'fixed-width',
                'X-Force-Cloud-Editor': 'true'
            })
            
            response = requests.post(url, headers=enhanced_headers, data=json.dumps(create_page_data))
            
            if response.status_code == 200:
                result = response.json()
                page_url = urljoin(self.confluence_url, result['_links']['webui'])
                logger.info(f"Page created successfully using enhanced Confluence Cloud API: {title}")
                
                # Verify Cloud Editor usage
                page_id = result.get('id')
                if page_id:
                    self._verify_cloud_editor_usage(page_id)
                
                return page_url
            else:
                logger.error(f"Enhanced API failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error in enhanced Cloud Editor creation: {e}")
            return None
    

    
    def _make_page_request(self, method: str, url: str, page_data: dict, title: str) -> Optional[str]:
        """Make HTTP request to Confluence Cloud API for page operations."""
        try:
            # Ensure Cloud Editor metadata is preserved in the page data
            if 'metadata' not in page_data:
                page_data['metadata'] = {}
            if 'properties' not in page_data['metadata']:
                page_data['metadata']['properties'] = {}
            
            # Force Cloud Editor properties if not already present
            cloud_editor_props = {
                'content-appearance': {'value': 'fixed-width'},
                'editor': {'value': 'v2'},
                'editor-version': {'value': '2'}
            }
            
            for prop, value in cloud_editor_props.items():
                if prop not in page_data['metadata']['properties']:
                    page_data['metadata']['properties'][prop] = value
            
            logger.info(f"Making {method} request with Cloud Editor metadata preserved")
            
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
                
                # Verify Cloud Editor usage for updates
                if method.upper() == 'PUT':
                    page_id = result.get('id')
                    if page_id:
                        self._verify_cloud_editor_usage(page_id)
                
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
        
        # Use the enhanced Cloud Editor approach
        try:
            logger.info("Attempting enhanced Cloud Editor creation...")
            page_url = self._create_page_with_cloud_editor_v2(title, content)
            if page_url:
                logger.info("Enhanced Cloud Editor creation successful!")
                return page_url
            else:
                logger.info("Enhanced approach failed, falling back to standard REST API...")
        except Exception as e:
            logger.warning(f"Enhanced Cloud Editor approach failed: {e}")
        
        # Fallback to standard REST API
        try:
            page_data = self._prepare_page_data(title, content)
            page_url = self._make_page_request('POST', urljoin(self.api_base, 'content'), page_data, title)
            
            # Verify Cloud Editor usage for fallback method
            if page_url and '/pages/' in page_url:
                page_id = page_url.split('/pages/')[-1].split('/')[0]
                self._verify_cloud_editor_usage(page_id)
            
            return page_url
        except Exception as e:
            logger.error(f"Failed to create page: {e}")
            return None
    
    def update_page(self, page_id: str, title: str, content: str, version: int) -> Optional[str]:
        """Update an existing Confluence Cloud page using modern REST API for cloud editor support."""
        logger.info("Using Confluence Cloud REST API directly for cloud editor support")
        
        # Use Confluence Cloud REST API directly for better cloud editor control
        page_data = self._prepare_page_data(title, content, page_id, version)
        return self._make_page_request('PUT', urljoin(self.api_base, f'content/{page_id}'), page_data, title)
    
    def _update_page_with_cloud_editor(self, page_id: str, title: str, content: str, version: int) -> Optional[str]:
        """Update a Confluence Cloud page while preserving Cloud Editor settings."""
        try:
            logger.info(f"Updating page {page_id} with Cloud Editor preservation")
            
            # Use the enhanced page data preparation
            page_data = self._prepare_page_data(title, content, page_id, version)
            
            # Ensure Cloud Editor compatibility
            if 'body' in page_data and 'storage' in page_data['body']:
                page_data['body']['storage']['value'] = self._ensure_cloud_editor_compatibility(
                    page_data['body']['storage']['value']
                )
            
            # Force Cloud Editor metadata
            if 'metadata' not in page_data:
                page_data['metadata'] = {}
            if 'properties' not in page_data['metadata']:
                page_data['metadata']['properties'] = {}
            
            # Set Cloud Editor properties
            cloud_editor_props = {
                'content-appearance': {'value': 'fixed-width'},
                'editor': {'value': 'v2'},
                'editor-version': {'value': '2'},
                'content-appearance-draft': {'value': 'fixed-width'},
                'editor-draft': {'value': 'v2'},
                'editor-version-draft': {'value': '2'},
                'content-appearance-published': {'value': 'fixed-width'},
                'editor-published': {'value': 'v2'},
                'editor-version-published': {'value': '2'}
            }
            
            for prop, value in cloud_editor_props.items():
                page_data['metadata']['properties'][prop] = value
            
            logger.info("Updated page data with Cloud Editor metadata")
            
            # Make the update request
            url = f"{self.confluence_url}/wiki/rest/api/content/{page_id}"
            response = requests.put(url, headers=self.headers, data=json.dumps(page_data), timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                page_url = urljoin(self.confluence_url, result['_links']['webui'])
                logger.info(f"Page updated successfully with Cloud Editor preservation: {title}")
                
                # Verify Cloud Editor usage
                self._verify_cloud_editor_usage(page_id)
                
                return page_url
            else:
                logger.error(f"Failed to update page with Cloud Editor: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error updating page with Cloud Editor: {e}")
            return None
    
    def upload_image(self, image_path: str, page_id: str, max_retries: int = 3) -> Optional[str]:
        """Upload an image as an attachment to a Confluence Cloud page with retry logic."""
        for attempt in range(max_retries):
            try:
                logger.info(f"Uploading image: {os.path.basename(image_path)} to page: {page_id} (attempt {attempt + 1}/{max_retries})")
                
                # Validate image using centralized utilities
                is_valid, message = ImageProcessor.validate_image_file(image_path)
                if not is_valid:
                    logger.warning(f"Skipping invalid image: {message}")
                    return None
                
                # Get content type using centralized utilities
                content_type = ImageProcessor.get_media_type(image_path)
                filename = os.path.basename(image_path)
                
                with open(image_path, 'rb') as f:
                    files = {
                        'file': (filename, f, content_type)
                    }
                    
                    headers = {
                        'X-Atlassian-Token': 'no-check'
                    }
                    
                    url = f"{self.api_base}content/{page_id}/child/attachment"
                    
                    # Increased timeout for image uploads (60 seconds)
                    response = requests.post(
                        url,
                        files=files,
                        headers=headers,
                        auth=(self.username, self.api_token),
                        timeout=60
                    )
                    
                    if response.status_code in [200, 201]:
                        result = response.json()
                        if 'results' in result and len(result['results']) > 0:
                            attachment_id = result['results'][0]['id']
                            # Return the attachment URL for embedding
                            attachment_url = f"/wiki/download/attachments/{page_id}/{filename}"
                            logger.info(f"Image uploaded successfully: {filename}")
                            return attachment_url
                        else:
                            logger.error(f"No results in upload response for: {filename}")
                            if attempt < max_retries - 1:
                                logger.info(f"Retrying upload in 2 seconds...")
                                import time
                                time.sleep(2)
                                continue
                            return None
                    else:
                        logger.error(f"Failed to upload image {filename}: {response.status_code} - {response.text}")
                        if attempt < max_retries - 1:
                            logger.info(f"Retrying upload in 2 seconds...")
                            import time
                            time.sleep(2)
                            continue
                        return None
                        
            except requests.exceptions.Timeout:
                logger.error(f"Image upload timeout for {os.path.basename(image_path)} - attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying upload in 2 seconds...")
                    import time
                    time.sleep(2)
                    continue
                return None
            except Exception as e:
                logger.error(f"Error uploading image {os.path.basename(image_path)} (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying upload in 2 seconds...")
                    import time
                    time.sleep(2)
                    continue
                return None
        
        logger.error(f"Failed to upload image {os.path.basename(image_path)} after {max_retries} attempts")
        return None

    def upload_content(self, title: str, content: str, content_type: str = None, images: list = None) -> Optional[str]:
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
            
            # Check if page already exists
            existing_page = self.find_page_by_title(title)
            
            if existing_page:
                page_id = existing_page['id']
                print(f"Found existing page: {title} (ID: {page_id})")
                print("⚠️  Forcing Cloud Editor usage by recreating page...")
                
                # Delete existing page to force Cloud Editor usage
                try:
                    delete_url = urljoin(self.api_base, f'content/{page_id}')
                    delete_response = requests.delete(delete_url, headers=self.headers)
                    if delete_response.status_code == 204:
                        print(f"✅ Existing page deleted successfully")
                    else:
                        print(f"⚠️  Could not delete existing page: {delete_response.status_code}")
                        # Continue with update if deletion fails
                        print(f"Updating existing page with Confluence Cloud editor: {title}")
                        page_url = self._update_page_with_cloud_editor(page_id, title, content, existing_page.get('version', {}).get('number', 1))
                        if page_url:
                            return page_url
                        else:
                            return None
                except Exception as e:
                    print(f"⚠️  Error deleting page: {e}")
                    # Continue with update if deletion fails
                    print(f"Updating existing page with Confluence Cloud editor: {title}")
                    page_url = self._update_page_with_cloud_editor(page_id, title, content, existing_page.get('version', {}).get('number', 1))
                    if page_url:
                        return page_url
                    else:
                        return None
            
            # Create new page with Cloud Editor (either fresh or after deletion)
            print(f"Creating new page with Confluence Cloud editor: {title}")
            page_url = self.create_page(title, content)
            if page_url and '/pages/' in page_url:
                page_id = page_url.split('/pages/')[-1].split('/')[0]
            else:
                return None
            
            # Upload images and get their attachment URLs
            image_embeds = []
            if images and page_id:
                print(f"Uploading {len(images)} images to Confluence Cloud...")
                for i, image_path in enumerate(images, 1):
                    # Clean and expand the image path
                    cleaned_path = os.path.expanduser(image_path.strip().strip('"').strip("'"))
                    
                    if os.path.exists(cleaned_path):
                        # Optimize image if it's too large
                        optimized_path = self._optimize_image_for_upload(cleaned_path)
                        is_optimized = optimized_path != cleaned_path
                        
                        # Create unique filename to avoid conflicts
                        original_filename = os.path.basename(cleaned_path)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        unique_filename = f"{timestamp}_{i}_{original_filename}"
                        
                        # Create a temporary copy with unique name
                        import tempfile
                        import shutil
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(original_filename)[1]) as temp_file:
                            shutil.copy2(optimized_path, temp_file.name)
                            temp_path = temp_file.name
                        
                        try:
                            # Upload the temporary file
                            image_url = self.upload_image(temp_path, page_id)
                            if image_url:
                                print(f"Uploaded to Confluence Cloud: {original_filename}")
                                if is_optimized:
                                    print(f"  → Image was optimized for faster upload")
                                
                                # Extract the actual filename from the image URL
                                actual_filename = image_url.split('/')[-1]
                                
                                # Create Confluence Cloud image macro for embedding using actual filename
                                image_embed = f'<ac:image ac:width="800"><ri:attachment ri:filename="{actual_filename}" /></ac:image>'
                                image_embeds.append({
                                    'section': f"**Dashboard View {i}**",
                                    'embed': image_embed,
                                    'filename': actual_filename,
                                    'original_name': original_filename
                                })
                            else:
                                print(f"Failed to upload to Confluence Cloud: {original_filename}")
                        finally:
                            # Clean up temporary files
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)
                            if is_optimized and os.path.exists(optimized_path):
                                os.unlink(optimized_path)
                    else:
                        print(f"Image not found: {cleaned_path}")
            
            # Embed images into content if we have them
            if image_embeds:
                # Add image embeds to content
                final_content = self._embed_images_in_content(content, image_embeds)
                
                # Update the page with embedded images
                print("Updating page with embedded images...")
                print("Using Cloud Editor update method to preserve editor settings...")
                
                # Use our Cloud Editor update method to preserve editor settings
                page_url = self._update_page_with_cloud_editor(page_id, title, final_content, 1)
                if page_url:
                    print("✅ Page updated with embedded images and Cloud Editor preservation")
                    return page_url
                else:
                    print("❌ Failed to update page with Cloud Editor preservation")
                    return None
            else:
                # No images to embed, return the page URL
                return page_url
                
        except Exception as e:
            logger.error(f"Error in upload_content: {e}")
            print(f"❌ Error uploading content: {e}")
            return None
    
    def _embed_images_in_content(self, content: str, image_embeds: list) -> str:
        """Embed images into the content at the very end with proper formatting."""
        try:
            if image_embeds:
                # Add a clear section header with proper spacing
                insert_point = content + '\n\n<h2 style="margin-top: 2em; padding-top: 1em; border-top: 2px solid #dfe1e6;">Dashboard Screenshots</h2>\n\n'
                
                # Add each image with improved formatting
                for j, img_info in enumerate(image_embeds, 1):
                    # Use original filename for better naming, fallback to actual filename if needed
                    display_name = img_info.get('original_name', img_info['filename'])
                    # Clean up the display name for better readability
                    clean_name = display_name.replace('.png', '').replace('.jpg', '').replace('.jpeg', '').replace('Screenshot ', '').replace('_', ' ').replace('-', ' ')
                    # Capitalize words for better appearance
                    clean_name = ' '.join(word.capitalize() for word in clean_name.split())
                    
                    # Create a well-formatted image section
                    insert_point += f'<div style="margin: 1.5em 0; padding: 1em; background: #f8f9fa; border-radius: 6px; border: 1px solid #dfe1e6;">\n'
                    insert_point += f'  <h3 style="margin: 0 0 1em 0; color: #172B4D; font-size: 1.2em;">View {j}: {clean_name}</h3>\n'
                    insert_point += f'  <div style="text-align: center; margin: 1em 0;">\n'
                    insert_point += f'    {img_info["embed"]}\n'
                    insert_point += f'  </div>\n'
                    insert_point += f'</div>\n\n'
                
                logger.info(f"Embedded {len(image_embeds)} images into content for Confluence Cloud with improved formatting")
                return insert_point
            
            return content
            
        except Exception as e:
            logger.error(f"Error embedding images in content for Confluence Cloud: {e}")
            return content  # Return original content if embedding fails

    def _ensure_cloud_editor_compatibility(self, content: str) -> str:
        """Ensure content is compatible with Confluence Cloud Editor with proper formatting."""
        try:
            logger.info("Ensuring content compatibility with Confluence Cloud Editor")
            
            # Remove any legacy editor specific elements that might trigger legacy mode
            content = content.replace('<ac:structured-macro', '<div class="macro"')
            content = content.replace('</ac:structured-macro>', '</div>')
            
            # Improve HTML structure and readability
            content = self._improve_content_structure(content)
            
            # Enhance document styling for better visual appeal
            content = self._enhance_document_styling(content)
            
            # Ensure proper HTML structure for Cloud Editor
            if not content.startswith('<'):
                content = f'<div class="content">{content}</div>'
            
            logger.info("Content formatted for Cloud Editor compatibility with improved structure and styling")
            return content
            
        except Exception as e:
            logger.error(f"Error ensuring Cloud Editor compatibility: {e}")
            return content  # Return original content if formatting fails

    def _verify_cloud_editor_usage(self, page_id: str) -> bool:
        """Verify that the page is using Cloud Editor."""
        try:
            logger.info(f"Verifying Cloud Editor usage for page: {page_id}")
            
            # Get the page details to check metadata
            url = f"{self.confluence_url}/wiki/rest/api/content/{page_id}?expand=metadata.properties"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                page_data = response.json()
                metadata = page_data.get('metadata', {}).get('properties', {})
                
                logger.info(f"Page metadata: {json.dumps(metadata, indent=2)}")
                
                # Check for Cloud Editor indicators
                editor_version = metadata.get('editor-version', {}).get('value')
                content_appearance = metadata.get('content-appearance', {}).get('value')
                
                if editor_version == '2' and content_appearance == 'fixed-width':
                    logger.info("Page confirmed to be using Cloud Editor")
                    return True
                else:
                    logger.warning(f"Page may not be using Cloud Editor. Editor version: {editor_version}, Content appearance: {content_appearance}")
                    return False
            else:
                logger.error(f"Failed to verify Cloud Editor usage: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying Cloud Editor usage: {e}")
            return False

    def _optimize_image_for_upload(self, image_path: str, max_size_mb: int = 5) -> str:
        """Optimize image for upload to prevent timeouts and improve reliability."""
        try:
            import tempfile
            from PIL import Image
            
            # Check if image is already small enough
            file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
            if file_size_mb <= max_size_mb:
                return image_path
            
            logger.info(f"Optimizing large image: {os.path.basename(image_path)} ({file_size_mb:.1f}MB)")
            
            # Open and optimize the image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Calculate new dimensions while maintaining aspect ratio
                width, height = img.size
                if width > 1920 or height > 1080:
                    # Scale down large images
                    ratio = min(1920/width, 1080/height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Create temporary file for optimized image
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                temp_path = temp_file.name
                temp_file.close()
                
                # Save optimized image with quality settings
                img.save(temp_path, 'JPEG', quality=85, optimize=True)
                
                # Check if optimization was successful
                optimized_size_mb = os.path.getsize(temp_path) / (1024 * 1024)
                logger.info(f"Image optimized: {file_size_mb:.1f}MB → {optimized_size_mb:.1f}MB")
                
                return temp_path
                
        except ImportError:
            logger.warning("PIL/Pillow not available, skipping image optimization")
            return image_path
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return image_path

    def _improve_content_structure(self, content: str) -> str:
        """Improve HTML content structure for better readability in Confluence."""
        try:
            # Split content into lines for processing
            lines = content.split('\n')
            improved_lines = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Handle headings - keep as-is
                if line.startswith('<h1>') or line.startswith('<h2>') or line.startswith('<h3>'):
                    improved_lines.append(line)
                    continue
                
                # Handle lists - keep as-is
                if line.startswith('<ul>') or line.startswith('<ol>') or line.startswith('<li>') or line.startswith('</ul>') or line.startswith('</ol>') or line.startswith('</li>'):
                    improved_lines.append(line)
                    continue
                
                # Handle strong tags - keep as-is
                if line.startswith('<strong>') or line.startswith('</strong>'):
                    improved_lines.append(line)
                    continue
                
                # Handle horizontal rules - keep as-is
                if line.startswith('<hr/>'):
                    improved_lines.append(line)
                    continue
                
                # Handle paragraphs - keep as-is
                if line.startswith('<p>') or line.startswith('</p>'):
                    improved_lines.append(line)
                    continue
                
                # Handle div tags - keep as-is
                if line.startswith('<div') or line.startswith('</div>'):
                    improved_lines.append(line)
                    continue
                
                # For regular text content, wrap in paragraph tags if not already wrapped
                if not line.startswith('<'):
                    # Check if this line should be part of a paragraph
                    if line and not line.startswith('<'):
                        # If previous line was also text, add a line break
                        if improved_lines and not improved_lines[-1].startswith('<'):
                            improved_lines.append(f'<br/>{line}')
                        else:
                            improved_lines.append(f'<p>{line}</p>')
                    else:
                        improved_lines.append(line)
                else:
                    improved_lines.append(line)
            
            # Join lines back together
            improved_content = '\n'.join(improved_lines)
            
            # Add proper spacing between sections
            improved_content = improved_content.replace('</h2>\n<h3>', '</h2>\n\n<h3>')
            improved_content = improved_content.replace('</h3>\n<p>', '</h3>\n\n<p>')
            improved_content.replace('</p>\n<p>', '</p>\n\n<p>')
            
            # Ensure proper paragraph structure for text blocks
            # Find text blocks that aren't wrapped in paragraphs and wrap them
            import re
            
            # Simple pattern to find text that's not in HTML tags (avoiding complex look-behind)
            # Process line by line instead of using complex regex
            improved_lines = []
            for line in improved_content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # If line contains text but doesn't start with HTML tag, wrap it
                if line and not line.startswith('<') and not line.startswith('</') and len(line) > 10:
                    # Check if it's not already wrapped
                    if not (line.startswith('<p>') and line.endswith('</p>')):
                        improved_lines.append(f'<p>{line}</p>')
                    else:
                        improved_lines.append(line)
                else:
                    improved_lines.append(line)
            
            improved_content = '\n'.join(improved_lines)
            
            # Clean up any double paragraph tags
            improved_content = improved_content.replace('<p><p>', '<p>')
            improved_content = improved_content.replace('</p></p>', '</p>')
            
            # Add proper spacing between major sections
            improved_content = improved_content.replace('</h2>', '</h2>\n')
            improved_content = improved_content.replace('</h3>', '</h3>\n')
            
            logger.info("Content structure improved for better readability")
            return improved_content
            
        except Exception as e:
            logger.error(f"Error improving content structure: {e}")
            return content  # Return original content if improvement fails

    def _enhance_document_styling(self, content: str) -> str:
        """Enhance document styling for better visual appeal in Confluence."""
        try:
            # Enhance heading styles for better visual hierarchy
            content = content.replace('<h1>', '<h1 style="color: #172B4D; font-size: 2.5em; font-weight: 700; margin: 1.5em 0 1em 0; padding-bottom: 0.5em; border-bottom: 3px solid #0052CC;">')
            content = content.replace('<h2>', '<h2 style="color: #172B4D; font-size: 1.8em; font-weight: 600; margin: 1.5em 0 1em 0; padding-left: 0.5em; border-left: 4px solid #0052CC;">')
            content = content.replace('<h3>', '<h3 style="color: #172B4D; font-size: 1.4em; font-weight: 600; margin: 1.2em 0 0.8em 0; color: #42526E;">')
            
            # Enhance paragraph styling for better readability
            content = content.replace('<p>', '<p style="line-height: 1.6; margin-bottom: 1em; color: #42526E; text-align: justify;">')
            
            # Enhance list styling
            content = content.replace('<ul>', '<ul style="margin: 1em 0 1em 2em; line-height: 1.6;">')
            content = content.replace('<ol>', '<ol style="margin: 1em 0 1em 2em; line-height: 1.6;">')
            content = content.replace('<li>', '<li style="margin-bottom: 0.5em; color: #42526E;">')
            
            # Enhance strong tag styling
            content = content.replace('<strong>', '<strong style="color: #172B4D; font-weight: 600;">')
            
            # Add spacing between sections
            content = content.replace('</h2>', '</h2>\n<div style="margin: 1em 0;"></div>')
            content = content.replace('</h3>', '</h3>\n<div style="margin: 0.8em 0;"></div>')
            
            # Add subtle background to key sections
            content = content.replace('<h2 style="color: #172B4D; font-size: 1.8em; font-weight: 600; margin: 1.5em 0 1em 0; padding-left: 0.5em; border-left: 4px solid #0052CC;">', 
                                   '<h2 style="color: #172B4D; font-size: 1.8em; font-weight: 600; margin: 1.5em 0 1em 0; padding: 0.8em; padding-left: 1.2em; border-left: 4px solid #0052CC; background: linear-gradient(90deg, #f8f9fa 0%, #ffffff 100%); border-radius: 0 6px 6px 0;">')
            
            # Enhance the footer section
            if '<hr/>' in content:
                content = content.replace('<hr/>', '<hr style="margin: 2em 0; border: none; border-top: 2px solid #dfe1e6;"/>')
            
            # Style the footer information
            if 'Analysis Date:' in content:
                content = content.replace('<p><strong>Analysis Date:</strong>', '<p style="margin-top: 2em; padding: 1em; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #0052CC;"><strong style="color: #172B4D;">Analysis Date:</strong>')
                content = content.replace('<p><strong>Images Analyzed:</strong>', '<p style="padding: 0.5em 1em; background: #f8f9fa; border-radius: 0 0 6px 6px; margin: 0;"><strong style="color: #172B4D;">Images Analyzed:</strong>')
                content = content.replace('<p><strong>Analysis Method:</strong>', '<p style="padding: 0.5em 1em; background: #f8f9fa; border-radius: 0 0 6px 6px; margin: 0;"><strong style="color: #172B4D;">Analysis Method:</strong>')
                content = content.replace('<p>Generated using AI analysis for GoDaddy BI team</p>', '<p style="padding: 0.5em 1em; background: #f8f9fa; border-radius: 0 0 6px 6px; margin: 0; font-style: italic; color: #6B778C;">Generated using AI analysis for GoDaddy BI team</p>')
            
            logger.info("Document styling enhanced for better visual appeal")
            return content
            
        except Exception as e:
            logger.error(f"Error enhancing document styling: {e}")
            return content  # Return original content if enhancement fails


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