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

# Analysis depth configuration
ANALYSIS_DEPTH = os.getenv('ANALYSIS_DEPTH', 'comprehensive').lower()  # 'basic' or 'comprehensive'
ENABLE_DETAILED_METRICS = os.getenv('ENABLE_DETAILED_METRICS', 'true').lower() == 'true'
ENABLE_BUSINESS_INSIGHTS = os.getenv('ENABLE_BUSINESS_INSIGHTS', 'true').lower() == 'true'
ENABLE_TECHNICAL_SPECS = os.getenv('ENABLE_TECHNICAL_SPECS', 'true').lower() == 'true'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_bedrock_client():
    """Get a configured Bedrock client using AWS credential chain."""
    # Use AWS credential chain for authentication
    # This supports: IAM roles, AWS SSO, CLI profiles, instance profiles, env vars
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
    
    # If AWS profile is specified, use it
    if hasattr(config, 'aws_profile') and config.aws_profile:
        # Use session with profile
        session = boto3.Session(profile_name=config.aws_profile)
        return session.client('bedrock-runtime', region_name=config.aws_region)
    
    return boto3.client(**client_kwargs)



def create_unified_prompt(is_multi_image: bool = False) -> str:
    """Create a comprehensive prompt for in-depth dashboard analysis and documentation generation."""
    
    # Define conditional content  
    multi_note = " across multiple dashboard sections" if is_multi_image else ""
    
    # Base prompt for comprehensive analysis
    comprehensive_prompt = f"""You are a senior business intelligence analyst and data visualization expert with deep expertise in dashboard design, business metrics, and user experience. Your task is to perform an extremely detailed, word-by-word analysis of the dashboard images to create comprehensive, actionable documentation for GoDaddy stakeholders.

## ANALYSIS APPROACH - EXTREMELY DETAILED

### VISUAL ELEMENT ANALYSIS
- **Text Analysis**: Read and analyze EVERY word, number, and label visible in the screenshots
- **Layout Analysis**: Examine the exact positioning, grouping, and visual hierarchy of elements
- **Color Analysis**: Note specific colors, color schemes, and their business significance
- **Icon Analysis**: Identify and describe every icon, symbol, and visual indicator
- **Interactive Elements**: Catalog every button, dropdown, filter, and clickable component

### BUSINESS CONTEXT ANALYSIS
- **Metric Definitions**: Provide detailed explanations of what each metric measures and why it matters
- **Business Impact**: Explain how each visualization helps stakeholders make decisions
- **Data Relationships**: Identify connections between different metrics and views
- **Trend Analysis**: Note any visible trends, patterns, or anomalies in the data
- **Performance Indicators**: Highlight KPIs, targets, and performance benchmarks

### TECHNICAL ANALYSIS
- **Data Sources**: Identify specific data tables, systems, or sources mentioned
- **Refresh Patterns**: Note update frequencies and data freshness indicators
- **Filter Logic**: Explain how filters work and their impact on data views
- **Drill-Down Capabilities**: Detail available navigation paths and data exploration options
- **Export/Sharing**: Note any data export or collaboration features

## COMPREHENSIVE DOCUMENTATION STRUCTURE

### 1. EXECUTIVE SUMMARY
- **Dashboard Purpose**: Detailed explanation of business objectives and use cases
- **Target Audience**: Specific stakeholder groups and their information needs
- **Business Value**: Quantified benefits and decision-making impact
- **Key Insights**: Most important findings and actionable takeaways

### 2. DASHBOARD ARCHITECTURE
- **Overall Layout**: Detailed description of the dashboard structure and organization
- **Navigation Flow**: Step-by-step user journey through the dashboard
- **View Relationships**: How different sections connect and complement each other
- **Responsive Design**: Notes on mobile/tablet compatibility and layout adaptations

### 3. DETAILED VIEW ANALYSIS (For Each View)
- **View Purpose**: Specific business questions this view answers
- **Data Elements**: Every metric, chart, and data point with detailed explanations
- **Visual Design**: Chart types, color schemes, and layout choices
- **Interactive Features**: Filters, drill-downs, and user controls
- **Business Logic**: How the data is calculated and what it represents
- **Performance Notes**: Loading times, data refresh, and system performance
- **User Experience**: Ease of use, accessibility, and user guidance

### 4. METRIC DEEP DIVE
- **Definition**: Precise explanation of what each metric measures
- **Calculation**: How the metric is computed (if visible)
- **Business Context**: Why this metric matters to GoDaddy
- **Benchmarks**: Target values, historical comparisons, and industry standards
- **Trends**: Visible patterns, seasonality, and performance changes
- **Actionability**: What stakeholders should do based on this metric

### 5. INTERACTIVE ELEMENTS CATALOG
- **Filter Controls**: Every dropdown, date picker, and selection tool
- **Navigation Elements**: Buttons, links, and menu options
- **Drill-Down Paths**: Available data exploration routes
- **Export Options**: Data download and sharing capabilities
- **User Preferences**: Customization and personalization features

### 6. DATA QUALITY ASSESSMENT
- **Data Freshness**: Update timestamps and refresh indicators
- **Completeness**: Missing data indicators and coverage notes
- **Accuracy**: Data validation and quality checks
- **Consistency**: Cross-view data alignment and verification
- **Reliability**: System uptime and data availability

### 7. BUSINESS INTELLIGENCE INSIGHTS
- **Pattern Recognition**: Identified trends, cycles, and anomalies
- **Correlation Analysis**: Relationships between different metrics
- **Performance Analysis**: Success indicators and improvement areas
- **Risk Assessment**: Warning signs and areas of concern
- **Opportunity Identification**: Growth potential and optimization areas

### 8. USER GUIDANCE AND BEST PRACTICES
- **Getting Started**: Step-by-step first-time user instructions
- **Daily Operations**: Routine monitoring and analysis procedures
- **Advanced Usage**: Power user features and optimization tips
- **Troubleshooting**: Common issues and resolution steps
- **Training Recommendations**: Skills needed and learning resources

### 9. TECHNICAL SPECIFICATIONS
- **System Requirements**: Browser compatibility and performance needs
- **Data Sources**: Specific databases, APIs, and integration points
- **Security**: Access controls and data protection measures
- **Performance**: Loading times, response rates, and scalability
- **Maintenance**: Update schedules and system administration

### 10. FUTURE ENHANCEMENTS
- **Feature Requests**: Identified improvement opportunities
- **Integration Possibilities**: Connections with other systems
- **Advanced Analytics**: Potential for ML/AI enhancements
- **User Experience**: Interface and workflow improvements
- **Data Expansion**: Additional metrics and data sources

## CRITICAL REQUIREMENTS

### ACCURACY AND DETAIL
- **Word-by-Word Analysis**: Read and analyze every visible text element
- **No Assumptions**: Only report what is clearly visible in the screenshots
- **Specific Details**: Use exact names, numbers, and labels from the images
- **Business Context**: Provide GoDaddy-specific insights and relevance

### FORMATTING AND STRUCTURE
- Use clear, professional business language
- Include specific examples and data points from the screenshots
- Provide actionable insights and recommendations
- Structure information logically with clear headings and sections
- Include visual descriptions for accessibility

### COMPREHENSIVENESS
- Cover every visible element and feature
- Explain the business purpose and value of each component
- Provide context for technical and non-technical stakeholders
- Include both high-level overview and detailed analysis
- Address user needs at all experience levels

## OUTPUT FORMAT

Create a comprehensive, well-structured document that follows the sections above. Each section should contain detailed analysis with specific examples from the dashboard images. Focus on providing actionable insights that help GoDaddy stakeholders understand, use, and derive value from the dashboard.

Remember: This is not just a description - it's a comprehensive business intelligence document that should enable stakeholders to make informed decisions and take action based on the dashboard insights."""

    # Basic prompt for simpler analysis
    basic_prompt = f"""You are a business intelligence expert creating documentation for GoDaddy stakeholders. Analyze the dashboard images to understand the objective, information/products it conveys, and how it helps users/stakeholders.

## BASIC ANALYSIS REQUIREMENTS
- Examine visible filters, dropdowns, buttons, and interactive elements
- Note specific control names, field names, and options visible
- Identify clickable elements and navigation features
- Report ONLY what is clearly visible in the screenshots

## BASIC DOCUMENTATION STRUCTURE

### 1. Objective
[Explain the dashboard's purpose in 2-3 sentences]

### 2. Dashboard Views
[List and briefly describe the main views visible]

### 3. Key Metrics
[Identify the main metrics and what they measure]

### 4. Interactive Controls
[List filters, dropdowns, and other controls]

### 5. How to Use
[Basic step-by-step instructions]

## OUTPUT FORMAT
Create a concise, well-structured document following the sections above. Focus on essential information for basic understanding and usage."""

    # Return appropriate prompt based on configuration
    if ANALYSIS_DEPTH == 'comprehensive':
        return comprehensive_prompt
    else:
        return basic_prompt


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
        
        image_data_list, valid_image_paths = ImageProcessor.prepare_multiple_images_for_bedrock(image_paths, optimize=ENABLE_IMAGE_OPTIMIZATION)
        
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
    
    if not recent_images:
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