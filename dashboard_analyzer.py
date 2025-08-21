#!/usr/bin/env python3
"""
QuickSight Dashboard Image Analyzer

Upload and analyze QuickSight dashboard screenshots with AI-powered insights.
"""

import base64
import glob
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

import boto3
from dotenv import load_dotenv

from utils import config, ImageProcessor

# Load environment variables
load_dotenv()

# Configuration
ENABLE_IMAGE_OPTIMIZATION = os.getenv('ENABLE_IMAGE_OPTIMIZATION', 'true').lower() == 'true'
OPTIMIZATION_QUALITY = int(os.getenv('OPTIMIZATION_QUALITY', '85'))  # JPEG quality 0-100
OPTIMIZATION_MAX_WIDTH = int(os.getenv('OPTIMIZATION_MAX_WIDTH', '1920'))
OPTIMIZATION_MAX_HEIGHT = int(os.getenv('OPTIMIZATION_MAX_HEIGHT', '1080'))

# Analysis configuration (keeping it simple and working)
ENABLE_ENHANCED_ANALYSIS = os.getenv('ENABLE_ENHANCED_ANALYSIS', 'true').lower() == 'true'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_bedrock_client():
    """Get a configured Bedrock client using AWS SSO profile."""
    # Use AWS SSO profile for authentication
    # This will automatically handle Okta authentication flow
    profile_name = 'gd-aws-usa-cpo-gdac-dev-private-poweruser'
    
    try:
        # Create session with the SSO profile
        session = boto3.Session(profile_name=profile_name)
        client = session.client('bedrock-agent-runtime', region_name=config.aws_region)
        
        logger.info(f"Using AWS SSO profile: {profile_name}")
        return client
        
    except Exception as e:
        logger.error(f"Failed to create Bedrock client with SSO profile {profile_name}: {e}")
        logger.info("Falling back to credential chain method...")
        
        # Fallback to credential chain method
        client_kwargs = {
            'service_name': 'bedrock-agent-runtime',
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



def create_unified_prompt(is_multi_image: bool = False) -> str:
    """Create a unified prompt for dashboard analysis and documentation generation."""
    
    # Define conditional content  
    multi_note = " across multiple dashboard sections" if is_multi_image else ""
    
    return f"""You are a business intelligence expert creating documentation guidelines for GoDaddy stakeholders. Analyze the dashboard images to understand the objective, information/products it conveys, and how it helps users/stakeholders.

INSTRUCTIONS:
Create professional documentation that data analysts at GoDaddy will use to help their stakeholders understand how to use their dashboards. Focus on practical usage and navigation guidance for business users.

ANALYSIS REQUIREMENTS:
- Carefully examine all visible filters, dropdowns, buttons, and interactive elements in the dashboard images
- Note specific control names, field names, and options visible in the interface
- Identify clickable elements, drill-down capabilities, and navigation features
- Report ONLY what is clearly visible in the screenshots - do not make assumptions

CRITICAL FORMATTING REQUIREMENTS - FOLLOW EXACTLY:
- MANDATORY: Use ONLY the exact structure provided below - NO other sections allowed
- FORBIDDEN: Do NOT create sections like "Dashboard Overview", "How to Navigate", "Understanding Visualizations", "Interactive Features", "Usage Guidelines"
- REQUIRED SECTIONS ONLY: Objective, New Enhanced View, New Additions, Detailed Overview (numbered 1-5), Dashboard Controls, How tos
- Use <h2> for main sections (Objective, New Enhanced View, etc.)
- Use <h3> for numbered detailed views (1., 2., 3., 4., 5.)
- Use <strong>bold text</strong> for subsection names: <strong>Metrics Reported</strong>, <strong>Data Source</strong>, <strong>View Specific Drill Down Control</strong>
- CRITICAL: Follow the template structure word-for-word - do not add extra sections
- Write in professional business language for GoDaddy stakeholders

CRITICAL INSTRUCTIONS - FOLLOW STRICTLY:
- OUTPUT ONLY THE DOCUMENTATION using the EXACT structure above
- START with "<h2>Objective</h2>" immediately - no other content before it
- NO EXTRA LINE BREAKS: Content must follow immediately after each header tag
- CRITICAL: After <h2>Objective</h2> the next line must be the explanation text with NO blank line in between
- INCLUDE ALL sections in the exact order: Objective → New Enhanced View → New Additions → Detailed Overview → Dashboard Controls → How tos
- FORBIDDEN: Do NOT create any sections not shown in the template
- FORBIDDEN: Do NOT use sections like "Dashboard Overview", "How to Navigate", "Understanding Visualizations"
- MANDATORY: Use the 5 numbered detailed views (<h3>1., <h3>2., <h3>3., <h3>4., <h3>5.)
- NO introductory text, explanations, or template deviations allowed

OUTPUT FORMAT (copy this structure exactly - NO BLANK LINES between headers and content):

<h2>Objective</h2>
[Explain the dashboard's purpose in 2-3 sentences. What business problems does it solve and how does it help GoDaddy stakeholders make informed decisions{multi_note}]
<h2>New Enhanced [Dashboard Name] View</h2>
The <strong>[Dashboard Name]</strong> in QuickSight has the following views:
1. [View 1 Name]
2. [View 2 Name] 
3. [View 3 Name]
4. [View 4 Name]
5. [View 5 Name]
For <strong>[Dashboard Name]</strong> in QuickSight, you can also navigate to [X] other additional views for additional insights:
1. [Additional View 1]
2. [Additional View 2]
All these views are discussed in detail below.
<h2>New Additions, Features and Changes</h2>
Unlike the previous version, the new enhanced version of [Dashboard Name] in QuickSight has several additional metrics and features:
1. <strong>Faster Loading:</strong> [Description of performance improvements]
2. <strong>Consolidated Dashboard View:</strong> [Description of view consolidation]
3. <strong>Enhanced [Feature] Diagnostics:</strong> [Description of diagnostic improvements]
4. <strong>Future Period Pacing:</strong> [Description of pacing features]
5. <strong>Prior [Metric] Tracking:</strong> [Description of tracking capabilities]
6. <strong>[Metric] ML Momentum View:</strong> [Description of ML features]
7. <strong>Controls:</strong> [Description of control improvements]
<h2>Detailed Overview of Each View</h2>
<h3>1. [View 1 Name]</h3>
[Description of what this view shows and its business purpose]
<strong>Metrics Reported</strong>
1. [Metric 1]: [Description of what it measures]
2. [Metric 2]: [Description of what it measures]
3. [Metric 3]: [Description of what it measures]
<strong>View Specific Drill Down Control</strong>
[Description of available drill-down options and controls]
<strong>Data Source</strong>
[Information about data sources and refresh schedules]
<h3>2. [View 2 Name]</h3>
[Description of what this view shows and its business purpose]
<strong>Metrics Reported</strong>
1. [Metric 1]: [Description of what it measures]
2. [Metric 2]: [Description of what it measures]
<strong>Data Source</strong>
[Information about data sources and refresh schedules]
<h3>3. [View 3 Name]</h3>
[Description of what this view shows and its business purpose]
<strong>Metrics Reported</strong>
1. [Metric 1]: [Description of what it measures]
2. [Metric 2]: [Description of what it measures]
<strong>Data Source</strong>
[Information about data sources and refresh schedules]
<h3>4. [View 4 Name]</h3>
[Description of what this view shows and its business purpose]
<strong>Metrics Reported</strong>
1. [Metric 1]: [Description of what it measures]
2. [Metric 2]: [Description of what it measures]
<strong>Data Source</strong>
[Information about data sources and refresh schedules]
<h3>5. [View 5 Name]</h3>
[Description of what this view shows and its business purpose]
<strong>Metrics Reported</strong>
1. [Metric 1]: [Description of what it measures]
2. [Metric 2]: [Description of what it measures]
<strong>Data Source</strong>
[Information about data sources and refresh schedules]
<h2>Dashboard Controls</h2>
[List and describe the specific filters, dropdowns, date selectors, and other controls visible in the dashboard images. Include their exact names and locations as shown in the screenshots.]
<h2>How tos:</h2>
[Based on what you see in the dashboard images, provide specific step-by-step instructions for using THIS dashboard. Include actual filter names, button locations, and specific features visible in the screenshots. Make this practical and actionable for users of this specific dashboard.]
[Include all images used, in-ligned with text and document.]"""


def validate_image_file(image_path: str) -> tuple[bool, str]:
    """Validate the uploaded image file using centralized utilities."""
    return ImageProcessor.validate_image_file(image_path)


def analyze_dashboard_image(image_path: str) -> Optional[str]:
    """Convenience function for single image analysis."""
    return analyze_dashboard_images([image_path])


def analyze_dashboard_images(image_paths: List[str]) -> Optional[str]:
    """Generate dashboard documentation from one or more image analysis.
    
    This function consolidates the previous separate single and multi-image handlers
    into a unified approach that efficiently handles both cases.
    """
    try:
        is_multi_image = len(image_paths) > 1
        print(f"🤖 Generating {'comprehensive' if is_multi_image else ''} documentation from {len(image_paths)} dashboard image{'s' if is_multi_image else ''}...")
        
        # Prepare all images for analysis using centralized utilities
        # Apply optimization settings if enabled
        if ENABLE_IMAGE_OPTIMIZATION:
            print(f"🔧 Image optimization enabled (Quality: {OPTIMIZATION_QUALITY}%, Max: {OPTIMIZATION_MAX_WIDTH}x{OPTIMIZATION_MAX_HEIGHT})")
            # Update ImageProcessor settings with our configuration
            ImageProcessor.JPEG_QUALITY = OPTIMIZATION_QUALITY
            ImageProcessor.MAX_WIDTH = OPTIMIZATION_MAX_WIDTH
            ImageProcessor.MAX_HEIGHT = OPTIMIZATION_MAX_HEIGHT
        
        image_data_list, valid_image_paths = ImageProcessor.prepare_multiple_images_for_bedrock(image_paths)
        
        if not image_data_list:
            print("❌ No valid images to process")
            return None
            
        print(f"✅ Successfully processed {len(image_data_list)} images for analysis")
        
        # Use unified prompt for documentation generation
        unified_prompt = create_unified_prompt(is_multi_image=is_multi_image)
        
        # Initialize Bedrock client
        print("Connecting to AWS Bedrock AI...")
        bedrock = get_bedrock_client()
        
        # Prepare messages with all images
        content_list = image_data_list + [{
            "type": "text",
            "text": unified_prompt
        }]
        
        print(f"Sending {len(image_data_list)} image{'s' if is_multi_image else ''} to Bedrock...")
        
        messages = [{
            "role": "user",
            "content": content_list
        }]
        
        # Adjust max_tokens based on number of images and analysis depth
        # Increased for more comprehensive analysis
        max_tokens = 8000 if is_multi_image else 6000
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": 0.1
        }
        
        # Calculate approximate payload size for multi-image
        if is_multi_image:
            body_str = json.dumps(body)
            payload_size_mb = len(body_str.encode('utf-8')) / (1024 * 1024)
            print(f"Payload size: {payload_size_mb:.2f} MB")
            
            if payload_size_mb > 20:
                print("⚠️ Payload might be too large for Bedrock")
        
        print("Calling Bedrock API...")
        # Call Bedrock with vision model
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=json.dumps(body),
            contentType='application/json'
        )
        
        # Parse response  
        response_body = json.loads(response['body'].read())
        documentation_text = response_body['content'][0]['text']
        
        # Remove extra spacing after header tags
        documentation_text = documentation_text.replace('<h2>Objective</h2>\n\n', '<h2>Objective</h2>\n')
        documentation_text = documentation_text.replace('<h2>Objective</h2>\n ', '<h2>Objective</h2>\n')
        documentation_text = documentation_text.replace('<h3>', '\n<h3>')  # Ensure h3 tags have proper spacing
        
        # Generate filename based on image count
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if is_multi_image:
            doc_filename = f"outputs/multi_dashboard_howto_{timestamp}.md"
        else:
            image_basename = os.path.splitext(os.path.basename(valid_image_paths[0]))[0]
            doc_filename = f"outputs/dashboard_howto_{image_basename}_{timestamp}.md"
        
        # Ensure outputs and images directories exist
        os.makedirs("outputs", exist_ok=True)
        os.makedirs("outputs/images", exist_ok=True)
        
        # Copy source images to outputs/images for embedding using centralized utilities
        copied_files = ImageProcessor.copy_images_to_outputs(valid_image_paths)
        for dest_path in copied_files:
            print(f"✅ Copied image: {os.path.basename(dest_path)}")
        
        # Create Markdown documentation with center alignment for Confluence
        markdown_filename = doc_filename  # Keep .md extension
        with open(markdown_filename, 'w', encoding='utf-8') as f:
            # Write centered title without metadata table
            f.write('<div style="text-align: center; max-width: 800px; margin: 0 auto;">\n\n')
            f.write("<h1>Dashboard User Guide</h1>\n")
            
            # Main documentation content
            f.write(documentation_text)
            f.write("\n\n")
            
            # Add screenshots section at the end
            f.write("<h2>Dashboard Screenshots</h2>\n\n")
            f.write(f"**Screenshot Analysis Date:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n")
            if is_multi_image:
                f.write(f"**Screenshots Analyzed:** {len(valid_image_paths)} images\n\n")
            f.write(f"*Generated using AWS Bedrock Claude 3.5 Sonnet AI analysis*\n\n")
            
            # Clean footer
            f.write("---\n\n")
            f.write("*This documentation was automatically generated using AI analysis.*\n")
            f.write("*For questions or updates, please contact the BI team.*\n\n")
            f.write("</div>")
        
        logger.info(f"✅ {'Multi-' if is_multi_image else ''}Dashboard documentation generated: {markdown_filename}")
        print(f"💾 Markdown documentation saved to: {markdown_filename}")
        print(f"Ready for Confluence import!")
        
        # Show a preview of key insights for single images
        if not is_multi_image:
            print("\n🔍 Quick Preview:")
            print("="*50)
            lines = documentation_text.split('\n')
            preview_lines = []
            section_count = 0
            
            for line in lines:
                if line.strip().startswith('##') and section_count < 3:  # Show first 3 sections
                    section_count += 1
                    preview_lines.append(f"  {line.strip()}")
                elif line.strip() and section_count <= 3 and len(preview_lines) < 15:
                    if line.strip().startswith('**') or line.strip().startswith('1.') or line.strip().startswith('-'):
                        preview_lines.append(f"    {line.strip()}")
                    elif not line.strip().startswith('#'):
                        preview_lines.append(f"  {line.strip()}")
            
            for line in preview_lines[:12]:  # Limit preview length
                print(line)
            
            if len(preview_lines) > 12:
                print("  ...")
        
        print(f"\n📖 View complete analysis: {markdown_filename}")
        
        return markdown_filename
        
    except Exception as e:
        logger.error(f"❌ Failed to analyze image{'s' if len(image_paths) > 1 else ''}: {e}")
        print(f"❌ Analysis failed: {e}")
        
        # Provide helpful error context
        if "ExpiredToken" in str(e):
            print("💡 Your AWS credentials have expired. Please refresh them in Okta.")
        elif "Access" in str(e) or "Permission" in str(e):
            print("💡 Check your AWS credentials and Bedrock permissions.")
        elif "not found" in str(e).lower():
            print("💡 Double-check the image file path.")
        elif "ValidationException" in str(e) or "PayloadTooLargeException" in str(e):
            print("💡 Multiple images may be too large. Try with fewer images or smaller files.")
        elif "Credentials" in str(e) or "Token" in str(e):
            print("💡 Credential issue detected. Please refresh your AWS credentials.")
        else:
            print("💡 Please verify your AWS credentials and image files.")
        
        return None





def publish_to_confluence(doc_file: str, title: str = None, images: list = None) -> bool:
    """Publish documentation to Confluence."""
    try:
        from utils.confluence_uploader import ConfluenceUploader
        
        print("Publishing documentation to Confluence...")
        
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
            content_type='markdown',
            images=images or []
        )
        
        if page_url:
            print(f"✅ Successfully published to Confluence!")
            print(f"Page URL: {page_url}")
            logger.info(f"✅ Published to Confluence: {page_url}")
            return True
        else:
            print("❌ Failed to publish to Confluence")
            return False
            
    except ImportError:
        print("❌ Confluence uploader not available")
        print("💡 Install confluence requirements or check configuration")
        return False
    except Exception as e:
        logger.error(f"❌ Confluence publishing failed: {e}")
        print(f"❌ Confluence publishing failed: {e}")
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


def upload_dashboard_image():
    """Unified interactive image upload and analysis (single or multiple images)."""
    print("QuickSight Dashboard Image Analyzer")
    print("=" * 50)
    print("Select one or multiple QuickSight dashboard screenshots for AI analysis")
    print()
    print("✅ Supported formats: PNG, JPG, JPEG, GIF, WebP, BMP")
    print("✅ Maximum file size: 10MB per image")
    print("✅ AI-powered business insights and recommendations")
    print("✅ Detailed visualization breakdown and technical assessment")
    print()
    print("💡 Tips for best results:")
    print("   - Capture the full dashboard view")
    print("   - Include chart titles and legends")
    print("   - Ensure text is readable")
    print("   - Use PNG format for best quality")
    print()
    
    recent_images = find_recent_images()
    selected_images: list[str] = []
    
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
                    print(f"   ✅ {os.path.basename(img)}")
                print()
            
            choice = input("Choose image number, enter a file path, ff to finish, or qq to quit: ").strip()

            if choice.lower() in ['qq', 'q', 'exit']:
                print("Goodbye!")
                return

            if not choice:
                print("❌ Please provide a selection")
                continue
            
            if choice.lower() == 'ff':
                if len(selected_images) >= 1:
                    break
                else:
                    print("❌ Please select at least 1 image")
                    continue

            if choice == '0':
                custom_path = input("📁 Enter file path: ").strip()
                custom_path = custom_path.strip().strip('"').strip("'")
                if custom_path and os.path.exists(custom_path):
                    selected_images.append(custom_path)
                    print(f"✅ Added: {os.path.basename(custom_path)}")
                else:
                    print(f"❌ File not found: {custom_path}")
                continue

            # Handle numeric choice from recent list
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(recent_images):
                    img_path = recent_images[choice_num - 1]
                    if img_path not in selected_images:
                        selected_images.append(img_path)
                        print(f"✅ Added: {os.path.basename(img_path)}")
                    else:
                        print("⚠️ Image already selected")
                else:
                    print(f"❌ Invalid choice. Enter 1-{len(recent_images)}, 0, ff, or a file path")
            else:
                # Try as direct file path
                path_candidate = choice.strip().strip('"').strip("'")
                if os.path.exists(path_candidate):
                    selected_images.append(path_candidate)
                    print(f"✅ Added: {os.path.basename(path_candidate)}")
                else:
                    print(f"❌ File not found: {path_candidate}")
    else:
        print("📁 No recent images found. Please enter file paths.")
        while True:
            if len(selected_images) >= 1:
                done = input(f"Currently selected: {len(selected_images)} image(s). Add more? (y/n): ").strip().lower()
                if done == 'n':
                    break
            
            img_path = input("📁 Enter image file path (or 'done' to finish, 'qq' to quit): ").strip()
            if img_path.lower() in ['qq', 'q', 'exit']:
                print("Goodbye!")
                return
            if img_path.lower() == 'done':
                if len(selected_images) >= 1:
                    break
                else:
                    print("❌ Please select at least 1 image")
                    continue
            
            img_path = img_path.strip().strip('"').strip("'")
            if os.path.exists(img_path):
                selected_images.append(img_path)
                print(f"✅ Added: {os.path.basename(img_path)}")
            else:
                print(f"❌ File not found: {img_path}")
    
    if len(selected_images) == 0:
        print("❌ No images selected")
        return
    
    if len(selected_images) == 1:
        # Single image flow
        image_path = selected_images[0]
        result = analyze_dashboard_images([image_path])

        if result:
            print(f"\nAnalysis Complete!")
            print(f"Full report saved to: {result}")
        print()
        
        print("Additional Options:")
        print("1. Generate how-to documentation")
        print("2. Generate how-to + publish to Confluence")
        print("3. Finish")

        doc_choice = input("Choose option (1-3): ").strip()

        if doc_choice == '2':
            custom_title = input("Enter custom title (or press Enter for auto-generated): ").strip()
            title = custom_title if custom_title else None
            success = publish_to_confluence(result, title, [image_path])
            if success:
                print("🚀 Complete workflow finished successfully!")
            else:
                print("⚠️ Documentation created but Confluence publishing failed")
        elif doc_choice == '1':
            print("✅ Documentation saved locally")
        else:
            print("Skipping documentation")

        another = input("Analyze more images? (y/n): ").strip().lower()
        if another in ['y', 'yes']:
            print()
            upload_dashboard_image()
        else:
            print("Thank you for using QuickSight Dashboard Image Analyzer!")
        
        if not result:
            print("❌ Analysis failed for the selected image")
        return

    # Multi-image flow - generate consolidated documentation
    doc_file = analyze_dashboard_images(selected_images)

    if doc_file:
        print(f"\nMulti-image Analysis Complete!")
        print(f"Successfully analyzed {len(selected_images)} screenshots of the dashboard")
        print()

        print("Documentation Options:")
        print("1. Keep documentation local")
        print("2. Publish to Confluence")
        print("3. Finish")
        
        doc_choice = input("Choose option (1-3): ").strip()
        
        if doc_choice == '2':
                print("\nPublishing to Confluence...")
                custom_title = input("Enter custom title (or press Enter for auto-generated): ").strip()
                title = custom_title if custom_title else None
                success = publish_to_confluence(doc_file, title, selected_images)
                if success:
                    print("✅ Successfully published to Confluence!")
                else:
                    print("❌ Failed to publish to Confluence")
        elif doc_choice == '1':
            print("✅ Documentation saved locally")

        print(f"\n🚀 Multi-image analysis workflow complete!")
        another = input("Analyze more images? (y/n): ").strip().lower()
        if another in ['y', 'yes']:
            print()
            upload_dashboard_image()
        else:
            print("Thank you for using QuickSight Dashboard Image Analyzer!")
    else:
        print("❌ Multi-image documentation generation failed")




def main():
    """Main application entry point."""
    logger.info("Starting QuickSight Dashboard Image Analyzer")
    
    print("\n" + "="*65)
    print("QuickSight Dashboard Image Analyzer")
    print("="*65)
    print("Upload and analyze QuickSight dashboard screenshots with AI")
    print()
    print("Features:")
    print("   - AI-powered dashboard analysis")
    print("   - Business insights and recommendations") 
    print("   - Visualization breakdown and assessment")
    print("   - Technical evaluation and improvement suggestions")
    print("   - Detailed markdown reports")
    print()
    
    try:
        upload_dashboard_image()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"\n❌ Application error: {e}")
        print("💡 Please check your AWS credentials and try again.")
    finally:
        logger.info("Application completed")


if __name__ == "__main__":
    main()