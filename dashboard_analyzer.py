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

# Image optimization configuration (optional)
ENABLE_IMAGE_OPTIMIZATION = os.getenv('ENABLE_IMAGE_OPTIMIZATION', 'true').lower() == 'true'
OPTIMIZATION_QUALITY = int(os.getenv('OPTIMIZATION_QUALITY', '85'))  # JPEG quality 0-100
OPTIMIZATION_MAX_WIDTH = int(os.getenv('OPTIMIZATION_MAX_WIDTH', '1920'))
OPTIMIZATION_MAX_HEIGHT = int(os.getenv('OPTIMIZATION_MAX_HEIGHT', '1080'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_bedrock_client():
    """Get a configured Bedrock client using AWS SSO profile."""
    # Use AWS SSO profile for authentication
    # This will automatically handle Okta authentication flow
    profile_name = 'g-aws-usa-gd-aisummerca-dev-private-poweruser'
    
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



def create_unified_prompt(is_multi_image: bool = False) -> str:
    """Create a unified prompt for dashboard analysis and documentation generation."""
    
    # Define conditional content  
    multi_note = " across multiple dashboard sections" if is_multi_image else ""
    
    return f"""You are a business intelligence expert creating comprehensive documentation guidelines for GoDaddy stakeholders. Analyze the dashboard images to understand the objective, information/products it conveys, and how it helps users/stakeholders.

INSTRUCTIONS:
Create comprehensive, in-depth documentation that data analysts at GoDaddy will use to help their stakeholders understand how to use their dashboards. Focus on practical usage and navigation guidance for business users. Always provide detailed, thorough analysis with comprehensive insights.

ANALYSIS REQUIREMENTS:
- Carefully examine all visible filters, dropdowns, buttons, and interactive elements in the dashboard images
- Note specific control names, field names, and options visible in the interface
- Identify clickable elements, drill-down capabilities, and navigation features
- Report ONLY what is clearly visible in the screenshots - do not make assumptions
- DYNAMICALLY determine the number of views/sections based on what you actually see in the images
- Provide comprehensive, in-depth analysis of each element and view
- Give detailed explanations and business context for all visible features

CRITICAL FORMATTING REQUIREMENTS - FOLLOW EXACTLY:
- MANDATORY: Use ONLY the exact structure provided below - NO other sections allowed
- FORBIDDEN: Do NOT create sections like "Dashboard Overview", "How to Navigate", "Understanding Visualizations", "Interactive Features", "Usage Guidelines"
- REQUIRED SECTIONS ONLY: Objective, Dashboard Views, New Additions, Detailed Overview, Dashboard Controls, How tos
- Use <h2 style="font-weight: bold;"> for main sections (Objective, Dashboard Views, etc.)
- Use <h3 style="font-weight: bold;"> for numbered detailed views - DYNAMIC COUNTING based on actual content (1., 2., 3., etc.)
- Use <strong>bold text</strong> for subsection names: <strong>Metrics Reported</strong>, <strong>Data Source</strong>, <strong>View Specific Drill Down Control</strong>
- CRITICAL: Follow the template structure word-for-word - do not add extra sections
- Write in professional business language for GoDaddy stakeholders
- MANDATORY: Use proper HTML tags for ALL formatting - <strong>, <h2 style="font-weight: bold;">, <h3 style="font-weight: bold;">, <ul>, <li>
- MANDATORY: Create proper numbered lists using <ol><li> for all numbered items
- MANDATORY: Create proper bullet lists using <ul><li> for all bullet points
- MANDATORY: Use <strong> tags around ALL subsection headers like "Metrics Reported", "Data Source", etc.

CRITICAL INSTRUCTIONS - FOLLOW STRICTLY:
- OUTPUT ONLY THE DOCUMENTATION using the EXACT structure above
- START with "<h2 style="font-weight: bold;">Objective</h2>" immediately - no other content before it
- NO EXTRA LINE BREAKS: Content must follow immediately after each header tag
- CRITICAL: After <h2 style="font-weight: bold;">Objective</h2> the next line must be the explanation text with NO blank line in between
- CRITICAL: After EVERY header tag, content must follow immediately with NO blank lines
- CRITICAL: NO blank lines between ANY headers and their content
- CRITICAL: NO spaces, line breaks, or empty lines between headers and paragraphs
- CRITICAL: Headers and content must be directly connected with zero spacing
- CRITICAL: Use this exact format: <h2>Header</h2>Content immediately follows
- CRITICAL: Provide COMPREHENSIVE, IN-DEPTH analysis for each section
- CRITICAL: Be SPECIFIC and DETAILED - avoid generic descriptions
- CRITICAL: Include BUSINESS CONTEXT and STRATEGIC INSIGHTS
- CRITICAL: Make content ACTIONABLE and PRACTICAL for stakeholders
- INCLUDE ALL sections in the exact order: Objective → Dashboard Views → Detailed Overview → Dashboard Controls → How to Use → Key Insights
- FORBIDDEN: Do NOT create any sections not shown in the template
- FORBIDDEN: Do NOT use sections like "Dashboard Overview", "How to Navigate", "Understanding Visualizations"
- DYNAMIC VIEW COUNTING: Create the exact number of <h3 style="font-weight: bold;"> sections that match what you see in the images (could be 1, 3, 7, etc.)
- NO introductory text, explanations, or template deviations allowed

OUTPUT FORMAT (copy this structure exactly - NO SPACING between headers and content):

<h2 style="font-weight: bold;">Objective</h2>
[Provide a comprehensive 4-6 sentence overview explaining the dashboard's strategic purpose, business context, target audience, key performance indicators, and how it enables data-driven decision making for GoDaddy stakeholders. Be specific about the business unit, operational focus, and strategic value.{multi_note}]
<h2 style="font-weight: bold;">Dashboard Views</h2>
Based on the dashboard images, I can identify the following views:
<ol>
<li>[Dynamically list the views you see in the images with brief 1-2 word descriptions]</li>
</ol>
<h2 style="font-weight: bold;">Detailed Overview of Each View</h2>
[DYNAMIC VIEW SECTIONS - Create exactly the number of <h3 style="font-weight: bold;"> sections that match the views you identified above. Each view should have comprehensive, in-depth analysis:]
<h3 style="font-weight: bold;">1. [View Name - Based on what you see]</h3>
[Provide a detailed 3-4 sentence description of what this view displays, its business purpose, target audience, and strategic importance. Explain the specific insights it provides and how stakeholders can use this information.]
<strong>Metrics Reported</strong>
<ol>
<li>[Dynamically list ALL metrics you see in the images with specific names, units, and brief explanations of what each metric measures]</li>
</ol>
<strong>Data Visualization Type</strong>
[Describe the specific chart type, graph style, or visualization method used in this view. Explain why this visualization choice is effective for the data being presented.]
<strong>Business Context & Interpretation</strong>
[Provide 2-3 sentences explaining what these metrics mean in business terms, how to interpret trends, what good vs. poor performance looks like, and what actions stakeholders should take based on the data.]
<strong>View Specific Drill Down Control</strong>
[Describe in detail the available drill-down options, filters, and interactive controls visible in this view. Include specific names, locations, and how users can navigate deeper into the data.]
<strong>Data Source & Refresh Schedule</strong>
[Specify the data sources, update frequency, and any refresh schedules visible in the dashboard. Include data quality indicators and any latency considerations.]
[CONTINUE WITH ADDITIONAL VIEWS - Create exactly the number you identified, numbered sequentially with the same comprehensive detail level]
<h2 style="font-weight: bold;">Dashboard Controls & Filters</h2>
[Provide a comprehensive overview of ALL interactive elements including filters, dropdowns, date selectors, search boxes, and navigation controls. For each control, specify its exact name, location, purpose, available options, and how it affects the dashboard view. Include any global vs. view-specific controls.]
<h2 style="font-weight: bold;">How to Use This Dashboard</h2>
[Provide detailed, step-by-step instructions for using THIS specific dashboard. Include exact filter names, button locations, navigation paths, and specific features visible in the screenshots. Make this practical and actionable with real examples. Include troubleshooting tips for common issues users might encounter.]
<h2 style="font-weight: bold;">Key Insights & Recommendations</h2>
[Based on the dashboard content and metrics, provide 3-4 actionable business insights and recommendations. Focus on what the data reveals about performance, trends, opportunities, and areas for improvement. Make these specific to GoDaddy's business context.]
[Include all images used, in-lined with text and document.]"""


def validate_image_file(image_path: str) -> tuple[bool, str]:
    """Validate the uploaded image file using centralized utilities."""
    return ImageProcessor.validate_image_file(image_path)


def analyze_dashboard_image(image_path: str) -> Optional[str]:
    """Convenience function for single image analysis."""
    return analyze_dashboard_images([image_path])


def analyze_dashboard_images(image_paths: List[str]) -> Optional[str]:
    """Generate dashboard documentation from one or more image analysis.
    
    This function uses unified processing for both single and multi-image cases
    to ensure consistent protocols and outcomes.
    """
    try:
        # Unified processing - no difference between single and multi-image
        print(f"Generating comprehensive documentation from {len(image_paths)} dashboard image{'s' if len(image_paths) > 1 else ''}...")
        
        # Prepare all images for analysis using centralized utilities
        # Apply optimization settings if enabled
        if ENABLE_IMAGE_OPTIMIZATION:
            print(f"Image optimization enabled (Quality: {OPTIMIZATION_QUALITY}%, Max: {OPTIMIZATION_MAX_WIDTH}x{OPTIMIZATION_MAX_HEIGHT})")
            # Update ImageProcessor settings with our configuration
            ImageProcessor.JPEG_QUALITY = OPTIMIZATION_QUALITY
            ImageProcessor.MAX_WIDTH = OPTIMIZATION_MAX_WIDTH
            ImageProcessor.MAX_HEIGHT = OPTIMIZATION_MAX_HEIGHT
        
        image_data_list, valid_image_paths = ImageProcessor.prepare_multiple_images_for_bedrock(image_paths)
        
        if not image_data_list:
            print("No valid images to process")
            return None
            
        print(f"Successfully processed {len(image_data_list)} images for analysis")
        
        # Use unified prompt for documentation generation - same for all
        unified_prompt = create_unified_prompt(len(image_paths) > 1)
        
        # Initialize Bedrock client
        print("Connecting to AWS Bedrock AI...")
        bedrock = get_bedrock_client()
        
        # Prepare messages with all images
        content_list = image_data_list + [{
            "type": "text",
            "text": unified_prompt
        }]
        
        print(f"Sending {len(image_data_list)} image{'s' if len(image_paths) > 1 else ''} to Bedrock...")
        
        messages = [{
            "role": "user",
            "content": content_list
        }]
        
        # Unified max_tokens - same for all (removed artificial difference)
        max_tokens = 8000
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": 0.1
        }
        
        # Check payload size and warn if too large
        payload_size = len(str(body))
        if payload_size > 200000:  # 200KB limit
            print("Warning: Payload might be too large for Bedrock")
            print(f"Current size: {payload_size / 1024:.1f}KB")
            print("Consider using fewer images or smaller files")
        
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
        
        # Unified filename generation - consistent pattern for all
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if len(image_paths) > 1:
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
            print(f"Copied image: {os.path.basename(dest_path)}")
        
        # Create clean, well-formatted documentation for Confluence with centered margin and left alignment
        markdown_filename = doc_filename
        with open(markdown_filename, 'w', encoding='utf-8') as f:
            # Centered container with left-aligned text
            f.write('<div style="text-align: left; max-width: 800px; margin: 0 auto;">\n\n')
            f.write('<h1 style="font-weight: bold; text-align: left;">Dashboard User Guide</h1>\n\n')
            
            # Main documentation content - ensure it's properly formatted
            f.write(documentation_text)
            f.write('\n\n')
            
            # Simple metadata footer
            f.write('<hr style="border: none; border-top: 2px solid #DFE1E6; margin: 40px 0;"/>\n\n')
            f.write(f'<p><strong>Analysis Date:</strong> {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>\n')
            f.write(f'<p><strong>Images Analyzed:</strong> {len(valid_image_paths)} image{"s" if len(valid_image_paths) > 1 else ""}</p>\n')
            f.write('<p>Generated using AI analysis for GoDaddy BI team</p>\n')
            f.write('</div>')
        
        logger.info(f"Dashboard documentation generated: {markdown_filename}")
        print(f"Markdown documentation saved to: {markdown_filename}")
        print(f"Ready for Confluence import!")
        
        return markdown_filename
        
    except Exception as e:
        logger.error(f"Failed to analyze image{'s' if len(image_paths) > 1 else ''}: {e}")
        print(f"Analysis failed: {e}")
        
        # Provide helpful error context
        if "InvalidClientTokenId" in str(e):
            print("Your AWS credentials have expired. Please refresh them in Okta.")
        elif "AccessDenied" in str(e):
            print("Check your AWS credentials and Bedrock permissions.")
        elif "NoSuchKey" in str(e):
            print("Double-check the image file path.")
        elif "PayloadTooLarge" in str(e):
            print("Multiple images may be too large. Try with fewer images or smaller files.")
        elif "ExpiredTokenException" in str(e):
            print("Credential issue detected. Please refresh your AWS credentials.")
        else:
            print("Please verify your AWS credentials and image files.")
        
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
            content_type='html',
            images=images or []
        )
        
        if page_url:
            print(f"Successfully published to Confluence!")
            print(f"Page URL: {page_url}")
            logger.info(f"Published to Confluence: {page_url}")
            return True
        else:
            print("Failed to publish to Confluence")
            return False
            
    except ImportError:
        print("Confluence uploader not available")
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


def upload_dashboard_image():
    """Unified interactive image upload and analysis (single or multiple images)."""
    print("QuickSight Dashboard Image Analyzer")
    print("=" * 50)
    print("Select one or multiple QuickSight dashboard screenshots for AI analysis")
    print()
    print("Supported formats: PNG, JPG, JPEG, GIF, WebP, BMP")
    print("Maximum file size: 10MB per image")
    print("AI-powered business insights and recommendations")
    print("Detailed visualization breakdown and technical assessment")
    print()
    print("Tips for best results:")
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
                    print(f"   - {os.path.basename(img)}")
                print()
            
            choice = input("Choose image number, enter a file path, ff to finish, or qq to quit: ").strip()

            if choice.lower() in ['qq', 'q', 'exit']:
                print("Goodbye!")
                return

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
                return
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
    
    if len(selected_images) == 0:
        print("No images selected")
        return
    
    # Unified workflow for both single and multi-image processing
    result = analyze_dashboard_images(selected_images)

    if result:
        print(f"\nAnalysis Complete!")
        print(f"Successfully analyzed {len(selected_images)} dashboard image{'s' if len(selected_images) > 1 else ''}")
        print(f"Full report saved to: {result}")
        print()

        print("Documentation Options:")
        print("1. Keep documentation local")
        print("2. Publish to Confluence")
        print("3. Finish")
        
        doc_choice = input("Choose option (1-3): ").strip()
        
        if doc_choice == '2':
            print("Publishing to Confluence...")
            custom_title = input("Enter custom title (or press Enter for auto-generated): ").strip()
            title = custom_title if custom_title else None
            success = publish_to_confluence(result, title, selected_images)
            if success:
                print("Complete workflow finished successfully!")
            else:
                print("Documentation created but Confluence publishing failed")
        elif doc_choice == '1':
            print("Documentation saved locally")
        else:
            print("Skipping documentation")

        print(f"\nAnalysis workflow complete!")
        another = input("Analyze more images? (y/n): ").strip().lower()
        if another in ['y', 'yes']:
            print()
            upload_dashboard_image()
        else:
            print("Thank you for using QuickSight Dashboard Image Analyzer!")
    else:
        print("Documentation generation failed")




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
        print(f"\n Application error: {e}")
        print("Please check your AWS credentials and try again.")
    finally:
        logger.info("Application completed")


if __name__ == "__main__":
    main()