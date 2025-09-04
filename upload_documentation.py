#!/usr/bin/env python3
"""
Standalone script to upload program documentation to Confluence
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.confluence_uploader import ConfluenceUploader

def main():
    """Upload the program documentation to Confluence."""
    
    # Load environment variables
    load_dotenv()
    
    print("Confluence How-To Bot Documentation Uploader")
    print("=" * 50)
    
    # Check if documentation file exists
    doc_file = "outputs/Program_User_Guide.md"
    if not os.path.exists(doc_file):
        print(f"Error: Documentation file not found: {doc_file}")
        return
    
    # Read the documentation content
    try:
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✓ Loaded documentation from: {doc_file}")
    except Exception as e:
        print(f"Error reading documentation file: {e}")
        return
    
    # Initialize Confluence uploader
    try:
        uploader = ConfluenceUploader()
        print("✓ Confluence uploader initialized")
    except Exception as e:
        print(f"Error initializing Confluence uploader: {e}")
        return
    
    # Test connection
    print("Testing Confluence connection...")
    if not uploader.test_connection():
        print("❌ Failed to connect to Confluence. Please check your configuration.")
        return
    print("✓ Connected to Confluence successfully")
    
    # Create page title
    page_title = "Confluence How-To Bot: Complete User Guide"
    
    # Check if page already exists
    existing_page = uploader.find_page_by_title(page_title)
    
    if existing_page:
        print(f"Page already exists with ID: {existing_page['id']}")
        update_choice = input("Do you want to update the existing page? (y/n): ").lower().strip()
        if update_choice != 'y':
            print("Upload cancelled.")
            return
        
        # Update existing page
        try:
            version = existing_page['version']['number'] + 1
            result = uploader.update_page(existing_page['id'], page_title, content, version)
            print(f"✓ Page updated successfully!")
            print(f"Page URL: {result}")
        except Exception as e:
            print(f"Error updating page: {e}")
            return
    else:
        # Create new page
        try:
            result = uploader.create_page(page_title, content)
            print(f"✓ Page created successfully!")
            print(f"Page URL: {result}")
        except Exception as e:
            print(f"Error creating page: {e}")
            return
    
    print("\nDocumentation upload completed successfully!")
    print("The user guide is now available in Confluence.")

if __name__ == "__main__":
    main()
