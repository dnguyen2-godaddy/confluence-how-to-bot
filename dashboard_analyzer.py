#!/usr/bin/env python3
"""
QuickSight Dashboard Image Analyzer

Upload and analyze QuickSight dashboard screenshots with AI-powered insights.
"""

import glob
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
import sys

import boto3
from dotenv import load_dotenv

from utils import config, ImageProcessor
from agents import analyze_dashboard_with_agent1, create_documentation_with_agent2
from utils.confluence_uploader import ConfluenceUploader

# Load environment variables
load_dotenv()

# Configuration - use config module for consistency

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_user_input(prompt: str, valid_options: list = None, default: str = None) -> str:
    """Get user input with better error handling and validation."""
    while True:
        try:
            user_input = input(prompt).strip()
            
            # Handle empty input with default
            if not user_input and default:
                return default
            
            # If no validation needed, return input
            if not valid_options:
                return user_input
            
            # Validate against valid options
            if user_input.lower() in [opt.lower() for opt in valid_options]:
                return user_input
            
            # Show valid options if validation fails
            print(f"Invalid input. Please choose from: {', '.join(valid_options)}")
            
        except KeyboardInterrupt:
            print("\n\nProcess interrupted. Goodbye!")
            sys.exit(0)
        except EOFError:
            print("\n\nInput error. Please try again.")
            continue


def get_bedrock_client():
    """Get a configured Bedrock client using AWS SSO profile."""
    # Use AWS SSO profile for authentication
    # This will automatically handle Okta authentication flow
    profile_name = config.aws_default_profile
    
    try:
        # Create session with the SSO profile
        session = boto3.Session(profile_name=profile_name)
        client = session.client('bedrock-runtime', region_name=config.aws_region)
        
        logger.info(f"Using AWS SSO profile: {profile_name}")
        return client
        
    except Exception as e:
        logger.error(f"Failed to create Bedrock client with SSO profile {profile_name}: {e}")
        logger.info("Falling back to credential chain method...")
        
        # Fallback to credential chain method
        client_kwargs = {
            'service_name': 'bedrock-runtime',
            'region_name': config.aws_region
        }
        
        # Only add explicit credentials if they're provided (for backward compatibility)
        if config.aws_access_key_id and config.aws_secret_access_key:
            client_kwargs.update({
                'aws_access_key_id': config.aws_access_key_id,
                'aws_secret_access_key': config.aws_secret_access_key,
                'aws_session_token': getattr(config, 'aws_session_token', None)
            })
        
        return boto3.client(**client_kwargs)


def get_bedrock_client_lazy():
    """Get a configured Bedrock client with lazy loading to improve UI responsiveness."""
    # Use AWS SSO profile for authentication
    # This will automatically handle Okta authentication flow
    profile_name = config.aws_default_profile
    
    try:
        # Create session with the SSO profile
        session = boto3.Session(profile_name=profile_name)
        client = session.client('bedrock-runtime', region_name=config.aws_region)
        
        logger.info(f"Using AWS SSO profile: {profile_name}")
        return client
        
    except Exception as e:
        logger.error(f"Failed to create Bedrock client with SSO profile {profile_name}: {e}")
        logger.info("Falling back to credential chain method...")
        
        # Fallback to credential chain method
        client_kwargs = {
            'service_name': 'bedrock-runtime',
            'region_name': config.aws_region
        }
        
        # Only add explicit credentials if they're provided (for backward compatibility)
        if config.aws_access_key_id and config.aws_secret_access_key:
            client_kwargs.update({
                'aws_access_key_id': config.aws_access_key_id,
                'aws_secret_access_key': config.aws_secret_access_key,
                'aws_session_token': getattr(config, 'aws_session_token', None)
            })
        
        return boto3.client(**client_kwargs)



def analyze_dashboard_images_multi_agent(image_paths: List[str], dashboard_name: str = "Dashboard User Guide") -> Optional[str]:
    """Sequential multi-agent dashboard analysis: Agent 1 analyzes, Agent 2 documents."""
    try:
        print("Starting AI analysis...")
        
        # Step 1: Agent 1 - Image Analysis and Data Extraction
        print("Extracting dashboard information...")
        analysis_data = analyze_dashboard_with_agent1(image_paths, get_bedrock_client())
        
        if not analysis_data:
            print("Failed to analyze dashboard images")
            return None
        
        print("Dashboard analysis complete")
        
        # Save intermediate analysis data for review (silently)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_filename = f"outputs/agent1_analysis_{timestamp}.json"
        
        try:
            # Try to parse as JSON and save formatted
            import json
            parsed_data = json.loads(analysis_data)
            with open(analysis_filename, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False)
        except:
            # If not valid JSON, save as text
            with open(analysis_filename, 'w', encoding='utf-8') as f:
                f.write(analysis_data)
        
        # Step 2: Agent 2 - Documentation Creation
        print("Creating comprehensive documentation...")
        documentation_text = create_documentation_with_agent2(analysis_data, get_bedrock_client())
        
        if not documentation_text:
            print("Failed to create documentation")
            return None
        
        print("Documentation generation complete")
        
        # Step 3: Process and save final documentation
        print("Finalizing documentation...")
        
        # Remove extra spacing after header tags
        documentation_text = documentation_text.replace('<h2>Objective</h2>\n\n', '<h2>Objective</h2>\n')
        documentation_text = documentation_text.replace('<h2>Objective</h2>\n ', '<h2>Objective</h2>\n')
        documentation_text = documentation_text.replace('<h3>', '\n<h3>')  # Ensure h3 tags have proper spacing
        
        # Generate filename using dashboard name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Clean dashboard name for filename (remove special characters)
        clean_name = "".join(c for c in dashboard_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_').replace('-', '_')
        
        if len(image_paths) > 1:
            doc_filename = f"outputs/{clean_name}_{timestamp}.md"
        else:
            image_basename = os.path.splitext(os.path.basename(image_paths[0]))[0]
            doc_filename = f"outputs/{clean_name}_{image_basename}_{timestamp}.md"
        
        # Ensure outputs and images directories exist
        os.makedirs("outputs", exist_ok=True)
        os.makedirs("outputs/images", exist_ok=True)
        
        # Copy source images to outputs/images for embedding
        copied_files = ImageProcessor.copy_images_to_outputs(image_paths)
        
        # Create final documentation
        with open(doc_filename, 'w', encoding='utf-8') as f:
            # Write clean HTML without styling
            f.write(f'<h1>{dashboard_name}</h1>\n\n')
            
            # Main documentation content from Agent 2
            f.write(documentation_text)
            f.write('\n\n')
            
            # Metadata footer
            f.write('<hr/>\n\n')
            f.write(f'<p><strong>Analysis Date:</strong> {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>\n')
            f.write(f'<p><strong>Images Analyzed:</strong> {len(image_paths)} image{"s" if len(image_paths) > 1 else ""}</p>\n')
            f.write('<p><strong>Analysis Method:</strong> AI-Powered Analysis</p>\n')
            f.write('<p>Generated using AI analysis for GoDaddy BI team</p>\n')
        
        logger.info(f"Dashboard documentation generated: {doc_filename}")
        return doc_filename
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"Analysis failed: {e}")
        return None


def publish_to_confluence(doc_file: str, title: str = None, images: list = None) -> bool:
    """Publish documentation to Confluence."""
    try:
        from utils.confluence_uploader import ConfluenceUploader
        
        print("Publishing to Confluence...")
        
        # Read the documentation content
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate title if not provided
        if not title:
            # Extract title from first heading in the document
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    title = line.replace('# ', '').strip()
                    break
            
            if not title:
                title = f"Dashboard User Guide - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Initialize Confluence uploader
        uploader = ConfluenceUploader()
        
        # Upload to Confluence with images
        page_url = uploader.upload_content(
            title=title,
            content=content,
            content_type='html',
            images=images or []
        )
        
        if page_url:
            print(f"Successfully published to Confluence")
            print(f"Page URL: {page_url}")
            logger.info(f"Published to Confluence: {page_url}")
            return True
        else:
            print("Failed to publish to Confluence!")
            return False
            
    except ImportError:
        print("Confluence uploader not available!")
        print("Install confluence requirements or check configuration")
        return False
    except Exception as e:
        logger.error(f"Confluence publishing failed: {e}")
        print(f"Confluence publishing failed: {e}")
        return False


def find_recent_images() -> List[str]:
    """Find recent image files in common locations, avoiding duplicates."""
    
    common_paths = [
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Downloads"), 
        os.path.expanduser("~/Pictures"),
        os.path.expanduser("~/dashboard-images")  # Add your dashboard images folder
    ]
    
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp', '*.bmp']
    recent_images = []
    seen_filenames = set()  # Track filenames to avoid duplicates
    
    for path in common_paths:
        if os.path.exists(path):
            for ext in image_extensions:
                pattern = os.path.join(path, ext)
                files = glob.glob(pattern)
                for file in files:
                    filename = os.path.basename(file)
                    
                    # Skip if we've already seen this filename
                    if filename in seen_filenames:
                        continue
                    
                    seen_filenames.add(filename)
                    
                    # Get file modification time
                    mtime = os.path.getmtime(file)
                    recent_images.append((file, mtime))
    
    # Sort by modification time (newest first) and return top 10
    recent_images.sort(key=lambda x: x[1], reverse=True)
    return [img[0] for img in recent_images[:10]]


def get_image_paths() -> List[str]:
    """Get image paths from user input."""
    print("Image Selection")
    print("Select one or multiple QuickSight dashboard screenshots for AI analysis")
    print("Supported formats: PNG, JPG, JPEG, GIF, WebP, BMP")
    print("Maximum file size: 10MB per image")
    print()
    
    recent_images = find_recent_images()
    selected_images: List[str] = []
    
    if recent_images:
        print("Recent image files found:")
        for i, img_path in enumerate(recent_images, 1):
            filename = os.path.basename(img_path)
            print(f"   {i:2d}. {filename}")
        print("    0. Add custom file path")
        print("   ff. Done selecting images")
        print("   qq. Quit")
        print()
        
        while True:
            print(f"Currently selected: {len(selected_images)} image(s)")
            if selected_images:
                for img in selected_images:
                    print(f"   - {os.path.basename(img)}")
                print()
            
            choice = input("Choose image number, enter a file path, ff to finish, or qq to quit: ").strip()

            if choice.lower() in ['qq', 'q', 'exit']:
                print("Goodbye!")
                return []

            if not choice:
                print("Please provide a selection")
                continue
            
            if choice.lower() == 'ff':
                if len(selected_images) >= 1:
                    break
                else:
                    print("Please select at least 1 image")
                    continue

            if choice == '0':
                custom_path = input("Enter file path: ").strip()
                custom_path = custom_path.strip().strip('"').strip("'")
                if custom_path and os.path.exists(custom_path):
                    selected_images.append(custom_path)
                    print(f"Added: {os.path.basename(custom_path)}")
                else:
                    print(f"File not found: {custom_path}")
                continue

            # Handle numeric choice from recent list
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(recent_images):
                    img_path = recent_images[choice_num - 1]
                    if img_path not in selected_images:
                        selected_images.append(img_path)
                        print(f"Added: {os.path.basename(img_path)}")
                    else:
                        print("Image already selected")
                else:
                    print(f"Invalid choice. Enter 1-{len(recent_images)}, 0, ff, or a file path")
            else:
                # Try as direct file path
                path_candidate = choice.strip().strip('"').strip("'")
                if os.path.exists(path_candidate):
                    selected_images.append(path_candidate)
                    print(f"Added: {os.path.basename(path_candidate)}")
                else:
                    print(f"File not found: {path_candidate}")
    else:
        print("No recent images found. Please enter file paths.")
        print("Enter one file path per line, or 'ff' to finish when done.")
        print()
        
        while True:
            print(f"Currently selected: {len(selected_images)} image(s)")
            if selected_images:
                for img in selected_images:
                    print(f"   - {os.path.basename(img)}")
                print()
            
            img_path = input("Enter image file path (or 'ff' to finish, 'qq' to quit): ").strip()
            if img_path.lower() in ['qq', 'q', 'exit']:
                print("Goodbye!")
                return []
            if img_path.lower() == 'ff':
                if len(selected_images) >= 1:
                    break
                else:
                    print("Please select at least 1 image")
                    continue
            
            img_path = img_path.strip().strip('"').strip("'")
            if os.path.exists(img_path):
                selected_images.append(img_path)
                print(f"Added: {os.path.basename(img_path)}")
            else:
                print(f"File not found: {img_path}")
    
    return selected_images


def validate_documentation_quality(content: str) -> dict:
    """Validate the quality and completeness of generated documentation."""
    validation = {
        'score': 0,
        'issues': [],
        'strengths': [],
        'recommendations': []
    }
    
    # Check for required sections
    required_sections = [
        'Executive Summary', 'Objective', 'Dashboard Views', 
        'Detailed Overview', 'Dashboard Controls', 'How to Use',
        'Key Insights & Recommendations'
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)
    
    if missing_sections:
        validation['issues'].append(f"Missing required sections: {', '.join(missing_sections)}")
    else:
        validation['strengths'].append("All required sections present")
        validation['score'] += 20
    
    # Check content length
    content_length = len(content)
    if content_length < 2000:
        validation['issues'].append("Documentation appears too short (less than 2000 characters)")
        validation['recommendations'].append("Consider adding more detailed explanations and examples")
    elif content_length > 15000:
        validation['strengths'].append("Documentation is comprehensive and detailed")
        validation['score'] += 15
    else:
        validation['strengths'].append("Documentation has appropriate length")
        validation['score'] += 10
    
    # Check for metrics and data
    if 'Metrics Reported' in content:
        validation['strengths'].append("Metrics section present")
        validation['score'] += 15
    else:
        validation['issues'].append("Metrics section missing")
    
    # Check for interactive elements
    if 'Interactive Controls' in content or 'Drill-Down' in content:
        validation['strengths'].append("Interactive controls documented")
        validation['score'] += 15
    else:
        validation['issues'].append("Interactive controls documentation missing")
    
    # Check for business context
    business_keywords = ['business', 'stakeholder', 'decision', 'performance', 'KPI', 'metric']
    business_context_count = sum(1 for keyword in business_keywords if keyword.lower() in content.lower())
    if business_context_count >= 3:
        validation['strengths'].append("Good business context coverage")
        validation['score'] += 15
    else:
        validation['issues'].append("Limited business context")
        validation['recommendations'].append("Add more business context and stakeholder value")
    
    # Check for actionable content
    action_keywords = ['how to', 'step', 'action', 'recommendation', 'insight']
    action_count = sum(1 for keyword in action_keywords if keyword.lower() in content.lower())
    if action_count >= 2:
        validation['strengths'].append("Good actionable content")
        validation['score'] += 10
    else:
        validation['issues'].append("Limited actionable content")
        validation['recommendations'].append("Include more specific steps and recommendations")
    
    # Check HTML formatting
    if '<h2' in content and '<h3' in content and '<strong>' in content:
        validation['strengths'].append("Proper HTML formatting")
        validation['score'] += 10
    else:
        validation['issues'].append("HTML formatting issues")
        validation['recommendations'].append("Ensure proper HTML structure")
    
    # Final score calculation
    validation['score'] = min(100, validation['score'])
    
    # Add overall assessment
    if validation['score'] >= 80:
        validation['assessment'] = "Excellent"
    elif validation['score'] >= 60:
        validation['assessment'] = "Good"
    elif validation['score'] >= 40:
        validation['assessment'] = "Fair"
    else:
        validation['assessment'] = "Needs Improvement"
    
    return validation


def print_documentation_feedback(validation: dict):
    """Print feedback about the generated documentation quality."""
    print()
    print("Documentation Quality Assessment")
    print("=" * 40)
    print(f"Overall Score: {validation['score']}/100 ({validation['assessment']})")
    print()
    
    if validation['strengths']:
        print("Strengths:")
        for strength in validation['strengths']:
            print(f"   • {strength}")
        print()
    
    if validation['issues']:
        print("Areas for Improvement:")
        for issue in validation['issues']:
            print(f"   • {issue}")
        print()
    
    if validation['recommendations']:
        print("Recommendations:")
        for rec in validation['recommendations']:
            print(f"   • {rec}")
        print()
    
    if validation['score'] >= 80:
        print("Excellent documentation quality! Ready for stakeholder use.")
    elif validation['score'] >= 60:
        print("Good documentation quality. Consider minor improvements before sharing.")
    else:
        print("Documentation needs improvement. Review and enhance before sharing with stakeholders.")


def main():
    """Main function to run the dashboard analyzer."""
    print("QuickSight Dashboard Image Analyzer")
    print("=" * 50)
    print("AI-powered dashboard documentation generator for GoDaddy BI team")
    print()
    
    try:
        # Get image paths first (before AWS authentication to improve UI responsiveness)
        print("Getting image paths...")
        image_paths = get_image_paths()
        if not image_paths:
            print("No images selected. Exiting.")
            return
            
        if len(image_paths) > 10:
            print("Warning: You've selected more than 10 images. This may take a while and could exceed API limits.")
            continue_choice = get_user_input("Continue anyway? (y/n): ", ['y', 'yes', 'n', 'no'])
            if continue_choice.lower() in ['n', 'no']:
                print("Image selection cancelled.")
                return
        
        print(f"Selected {len(image_paths)} image{'s' if len(image_paths) > 1 else ''} for analysis")
        print()
        
        # Get custom dashboard name
        print("Dashboard Naming")
        print("Enter a descriptive name for your dashboard (e.g., 'Sales Performance Dashboard', 'Customer Analytics')")
        print("Or press Enter to use the default name")
        print()
        
        dashboard_name = get_user_input("Dashboard name: ", default="Dashboard Analysis")
        print(f"Dashboard name: {dashboard_name}")
        print()
        
        # Validate image files before processing
        print("Validating image files...")
        valid_images = []
        for img_path in image_paths:
            if os.path.exists(img_path):
                file_size = os.path.getsize(img_path) / (1024 * 1024)  # MB
                if file_size > 10:
                    print(f"Warning: {os.path.basename(img_path)} is {file_size:.1f}MB (exceeds 10MB limit)")
                    continue_choice = get_user_input("Continue with this image? (y/n): ", ['y', 'yes', 'n', 'no'])
                    if continue_choice.lower() in ['n', 'no']:
                        continue
                valid_images.append(img_path)
                print(f"{os.path.basename(img_path)} - {file_size:.1f}MB")
            else:
                print(f"File not found: {img_path}")
        
        if not valid_images:
            print("No valid images found. Please check your file paths.")
            return
        
        image_paths = valid_images
        print(f"{len(image_paths)} valid images ready for analysis")
        print()
        
        # Now check AWS configuration (lazy loading to improve UI responsiveness)
        print("Checking AWS configuration...")
        bedrock_client = get_bedrock_client_lazy()
        if not bedrock_client:
            print("AWS Bedrock configuration failed. Please check your AWS credentials and configuration.")
            return
        print("AWS Bedrock configured successfully")
        print()
        
        # Start analysis
        print("Starting AI analysis...")
        print("This may take a few minutes depending on the number and size of images.")
        print()
        
        print("Phase 1: Analyzing dashboard images...")
        print("   - Extracting metrics and interactive elements...")
        print("   - Identifying chart types and data patterns...")
        print("   - Mapping business context and purpose...")
        print()
        
        result = analyze_dashboard_images_multi_agent(image_paths, dashboard_name)
        
        if result:
            print("Analysis complete!")
            print(f"Documentation saved to: {result}")
            print()
            
            # Validate documentation quality
            try:
                with open(result, 'r', encoding='utf-8') as f:
                    content = f.read()
                validation = validate_documentation_quality(content)
                print_documentation_feedback(validation)
            except Exception as e:
                print(f"Could not validate documentation quality: {e}")
            
            # Offer Confluence upload
            upload_choice = get_user_input("Would you like to upload this documentation to Confluence? (y/n): ", ['y', 'yes', 'n', 'no'])
            if upload_choice.lower() in ['y', 'yes']:
                print()
                print("Uploading to Confluence...")
                
                try:
                    uploader = ConfluenceUploader()
                    print("Testing Confluence Cloud connection...")
                    
                    if not uploader.test_connection():
                        print("Confluence connection failed. Please check your configuration.")
                    else:
                        print("Confluence connection successful!")
                        
                        # Read the generated documentation
                        with open(result, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Create page title from dashboard name
                        page_title = dashboard_name
                        
                        # Upload content with images
                        page_id = uploader.upload_content(page_title, content, images=image_paths)
                        
                        if page_id:
                            print(f"Successfully uploaded to Confluence!")
                            print(f"Page ID: {page_id}")
                            print(f"View page: {uploader.confluence_url}/pages/viewpage.action?pageId={page_id.split('/')[-1]}")
                        else:
                            print("Failed to upload to Confluence")
                            
                except Exception as e:
                    print(f"Error uploading to Confluence: {e}")
                    print("You can still manually import the documentation file to Confluence.")
            
            print()
            print("Workflow complete! Thank you for using the Dashboard Analyzer.")
            
        else:
            print("Analysis failed. Please check your images and try again.")
            print("Common issues:")
            print("   - Image files are corrupted or in unsupported format")
            print("   - AWS Bedrock service is unavailable")
            print("   - Network connectivity issues")
            
    except KeyboardInterrupt:
        print("\n\nProcess interrupted. Goodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please check your configuration and try again.")
        print("If the problem persists, check the logs for more details.")
        logger.error(f"Unexpected error in main: {e}", exc_info=True)


if __name__ == "__main__":
    main()