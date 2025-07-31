"""
Confluence Integration

This module handles uploading generated documentation to Confluence,
including page creation, updates, and attachment management.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from atlassian import Confluence
from utils.config import config

logger = logging.getLogger(__name__)


class ConfluenceUploader:
    """Handles uploading documentation to Confluence."""
    
    def __init__(self):
        """Initialize Confluence connection."""
        try:
            if not config.validate_confluence_config():
                raise ValueError("Confluence configuration is incomplete. Please check your .env file for Confluence settings.")
            
            self.confluence = Confluence(
                url=config.confluence_url,
                username=config.confluence_username,
                password=config.confluence_api_token,
                cloud=True  # Set to False for Confluence Server
            )
            
            self.space_key = config.confluence_space_key
            
            # Test connection
            self._test_connection()
            
            logger.info(f"Successfully connected to Confluence space: {self.space_key}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Confluence connection: {e}")
            raise
    
    def upload_documentation(self, 
                           documentation: Dict[str, str],
                           parent_page_title: Optional[str] = None,
                           update_existing: bool = True) -> Dict[str, Any]:
        """
        Upload documentation to Confluence.
        
        Args:
            documentation: Generated documentation dictionary
            parent_page_title: Title of parent page (if creating under a parent)
            update_existing: Whether to update existing pages with same title
            
        Returns:
            Dictionary with upload results
        """
        try:
            logger.info("Starting Confluence upload process")
            
            page_title = documentation['title']
            page_content = documentation['confluence_html']
            
            # Check if page already exists
            existing_page = self._find_existing_page(page_title)
            
            if existing_page and update_existing:
                # Update existing page
                result = self._update_page(existing_page, page_content)
                action = "updated"
            elif existing_page and not update_existing:
                # Create with unique title
                unique_title = self._generate_unique_title(page_title)
                result = self._create_page(unique_title, page_content, parent_page_title)
                action = "created_new"
            else:
                # Create new page
                result = self._create_page(page_title, page_content, parent_page_title)
                action = "created"
            
            # Add labels for organization
            if result.get('success'):
                self._add_page_labels(result['page_id'], ['quicksight', 'dashboard', 'how-to', 'ai-generated'])
            
            upload_result = {
                'success': result.get('success', False),
                'action': action,
                'page_id': result.get('page_id'),
                'page_url': result.get('page_url'),
                'title': result.get('title'),
                'space_key': self.space_key,
                'error': result.get('error')
            }
            
            if upload_result['success']:
                logger.info(f"Successfully {action} Confluence page: {upload_result['title']}")
            else:
                logger.error(f"Failed to upload to Confluence: {upload_result['error']}")
            
            return upload_result
            
        except Exception as e:
            logger.error(f"Confluence upload failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'action': 'failed'
            }
    
    def _test_connection(self):
        """Test Confluence connection and permissions."""
        try:
            # Try to get space information
            space_info = self.confluence.get_space(self.space_key)
            if not space_info:
                raise Exception(f"Cannot access space '{self.space_key}' - check permissions")
            
            logger.info(f"Connection test successful - Space: {space_info.get('name', self.space_key)}")
            
        except Exception as e:
            raise Exception(f"Confluence connection test failed: {e}")
    
    def _find_existing_page(self, title: str) -> Optional[Dict]:
        """Find existing page with the given title."""
        try:
            # Search for pages with the exact title in the space
            results = self.confluence.get_page_by_title(
                space=self.space_key,
                title=title
            )
            
            return results if results else None
            
        except Exception as e:
            logger.warning(f"Error searching for existing page: {e}")
            return None
    
    def _create_page(self, 
                    title: str, 
                    content: str, 
                    parent_title: Optional[str] = None) -> Dict[str, Any]:
        """Create a new Confluence page."""
        try:
            parent_id = None
            
            # Get parent page ID if specified
            if parent_title:
                parent_page = self.confluence.get_page_by_title(
                    space=self.space_key,
                    title=parent_title
                )
                if parent_page:
                    parent_id = parent_page['id']
                else:
                    logger.warning(f"Parent page '{parent_title}' not found, creating at space root")
            
            # Create the page
            page = self.confluence.create_page(
                space=self.space_key,
                title=title,
                body=content,
                parent_id=parent_id,
                type='page',
                representation='storage'
            )
            
            page_url = f"{config.confluence_url}/spaces/{self.space_key}/pages/{page['id']}"
            
            return {
                'success': True,
                'page_id': page['id'],
                'page_url': page_url,
                'title': title
            }
            
        except Exception as e:
            logger.error(f"Failed to create page: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_page(self, existing_page: Dict, content: str) -> Dict[str, Any]:
        """Update an existing Confluence page."""
        try:
            page_id = existing_page['id']
            title = existing_page['title']
            
            # Update the page
            updated_page = self.confluence.update_page(
                page_id=page_id,
                title=title,
                body=content,
                parent_id=existing_page.get('parentId'),
                type='page',
                representation='storage'
            )
            
            page_url = f"{config.confluence_url}/spaces/{self.space_key}/pages/{page_id}"
            
            return {
                'success': True,
                'page_id': page_id,
                'page_url': page_url,
                'title': title
            }
            
        except Exception as e:
            logger.error(f"Failed to update page: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_unique_title(self, base_title: str) -> str:
        """Generate a unique title by appending timestamp."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_title} ({timestamp})"
    
    def _add_page_labels(self, page_id: str, labels: List[str]) -> bool:
        """Add labels to a Confluence page."""
        try:
            for label in labels:
                self.confluence.set_page_label(
                    page_id=page_id,
                    label=label
                )
            
            logger.info(f"Added labels to page {page_id}: {', '.join(labels)}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to add labels: {e}")
            return False
    
    def create_dashboard_directory_structure(self, dashboard_name: str) -> Dict[str, Any]:
        """
        Create a directory structure for dashboard documentation.
        
        Args:
            dashboard_name: Name of the dashboard
            
        Returns:
            Dictionary with created pages information
        """
        try:
            logger.info(f"Creating directory structure for {dashboard_name}")
            
            # Create main dashboard directory page
            main_page_title = f"📊 {dashboard_name} Documentation"
            main_page_content = f"""
            <h1>📊 {dashboard_name} Documentation</h1>
            
            <div class="panel" style="border-color: #3498db; border-width: 2px;">
                <div class="panelHeader" style="border-color: #3498db; background-color: #e8f4fd;">
                    <strong>📚 Documentation Hub</strong>
                </div>
                <div class="panelContent">
                    <p>This page contains all documentation related to the <strong>{dashboard_name}</strong> dashboard.</p>
                    
                    <h3>📖 Available Documentation:</h3>
                    <ul>
                        <li><strong>User Guide</strong> - Comprehensive how-to guide for end users</li>
                        <li><strong>Quick Reference</strong> - Quick tips and shortcuts</li>
                        <li><strong>Troubleshooting</strong> - Common issues and solutions</li>
                    </ul>
                    
                    <p><em>📝 This documentation hub was automatically generated by the Confluence How-To Bot.</em></p>
                </div>
            </div>
            """
            
            main_page = self._create_page(main_page_title, main_page_content)
            
            created_pages = {
                'main_page': main_page,
                'success': main_page.get('success', False)
            }
            
            return created_pages
            
        except Exception as e:
            logger.error(f"Failed to create directory structure: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_space_info(self) -> Dict[str, Any]:
        """Get information about the Confluence space."""
        try:
            space_info = self.confluence.get_space(self.space_key)
            
            return {
                'key': space_info.get('key'),
                'name': space_info.get('name'),
                'type': space_info.get('type'),
                'status': space_info.get('status'),
                'homepage_id': space_info.get('homepage', {}).get('id'),
                'url': f"{config.confluence_url}/spaces/{self.space_key}"
            }
            
        except Exception as e:
            logger.error(f"Failed to get space info: {e}")
            return {'error': str(e)}
    
    def list_existing_dashboard_docs(self) -> List[Dict[str, Any]]:
        """List existing dashboard documentation pages."""
        try:
            # Search for pages with dashboard-related labels
            results = self.confluence.get_all_pages_from_space(
                space=self.space_key,
                start=0,
                limit=100,
                status=None,
                expand='metadata.labels'
            )
            
            dashboard_pages = []
            
            for page in results:
                # Check if page has dashboard-related labels or title
                title = page.get('title', '')
                if any(keyword in title.lower() for keyword in ['dashboard', 'how-to', 'guide']):
                    dashboard_pages.append({
                        'id': page['id'],
                        'title': title,
                        'url': f"{config.confluence_url}/spaces/{self.space_key}/pages/{page['id']}",
                        'created': page.get('createdDate'),
                        'updated': page.get('lastModified')
                    })
            
            logger.info(f"Found {len(dashboard_pages)} existing dashboard documentation pages")
            return dashboard_pages
            
        except Exception as e:
            logger.error(f"Failed to list existing docs: {e}")
            return []
    
    def backup_page(self, page_id: str) -> Optional[Dict[str, Any]]:
        """Create a backup of a page before updating."""
        try:
            page_content = self.confluence.get_page_by_id(
                page_id=page_id,
                expand='body.storage,version'
            )
            
            backup_data = {
                'id': page_id,
                'title': page_content.get('title'),
                'content': page_content.get('body', {}).get('storage', {}).get('value'),
                'version': page_content.get('version', {}).get('number'),
                'backed_up_at': datetime.now().isoformat()
            }
            
            # Save backup to file
            backup_filename = f"confluence_backup_{page_id}_{backup_data['version']}.json"
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"Created backup: {backup_filename}")
            return backup_data
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None