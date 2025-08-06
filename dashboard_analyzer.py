#!/usr/bin/env python3
"""
QuickSight Dashboard Image Analyzer

Upload and analyze QuickSight dashboard screenshots with AI-powered insights.
"""

import base64
import json
import logging
import os
from datetime import datetime
from typing import Optional

import boto3
from dotenv import load_dotenv

from utils import config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_image_file(image_path: str) -> tuple[bool, str]:
    """Validate the uploaded image file."""
    if not image_path or not image_path.strip():
        return False, "❌ No image path provided"
    
    image_path = image_path.strip().strip('"').strip("'")  # Clean quotes
    
    if not os.path.exists(image_path):
        return False, f"❌ Image file not found: {image_path}"
    
    # Check file size (max 10MB for reasonable processing)
    file_size = os.path.getsize(image_path)
    if file_size > 10 * 1024 * 1024:  # 10MB
        return False, f"❌ Image file too large: {file_size / (1024*1024):.1f}MB (max 10MB)"
    
    # Check file extension
    valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
    file_ext = os.path.splitext(image_path)[1].lower()
    if file_ext not in valid_extensions:
        return False, f"❌ Unsupported format: {file_ext}. Supported: {', '.join(valid_extensions)}"
    
    return True, "✅ Valid image file"


def analyze_dashboard_image(image_path: str) -> Optional[str]:
    """Analyze a QuickSight dashboard image with enhanced AI insights."""
    try:
        logger.info(f"🖼️ Starting dashboard image analysis: {image_path}")
        
        # Validate image file
        is_valid, message = validate_image_file(image_path)
        if not is_valid:
            print(message)
            return None
        
        image_path = image_path.strip().strip('"').strip("'")  # Clean path
        print(f"✅ {message}")
        print("📖 Reading and processing image...")
        
        # Read and encode image
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Determine media type
        file_ext = os.path.splitext(image_path)[1].lower()
        media_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg', 
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        media_type = media_type_map.get(file_ext, 'image/jpeg')
        
        # Enhanced AI analysis prompt for QuickSight dashboards
        analysis_prompt = """
You are an expert business intelligence analyst specializing in QuickSight dashboard analysis and data visualization best practices.

Analyze this QuickSight dashboard screenshot and provide comprehensive, actionable insights.

**ANALYSIS STRUCTURE:**

## 📊 DASHBOARD OVERVIEW
- Dashboard title, purpose, and main objective
- Overall design quality and visual hierarchy
- Number and arrangement of visualizations
- Brand/styling consistency

## 📈 VISUALIZATION BREAKDOWN
For each chart/visual, identify:
- Chart type (bar, line, pie, table, gauge, etc.)
- Data dimensions and measures displayed
- Key performance indicators (KPIs)
- Time ranges or date filters visible
- Data sources or datasets (if identifiable)
- Specific metric names and exact values shown

## 💡 KEY BUSINESS INSIGHTS
- Primary business domain (sales, finance, operations, marketing, etc.)
- Critical trends, patterns, or anomalies
- Performance indicators (meeting/missing targets)
- Seasonal patterns or time-based trends
- Top performers and areas of concern

## 🔧 INTERACTIVE FEATURES
- Filter controls and parameter selections (REPORT EXACT VALUES VISIBLE)
- Drill-down capabilities
- Navigation elements
- Date/time selectors
- Cross-filtering relationships

## 📑 MULTI-TAB ANALYSIS
- If multiple tabs are visible (e.g., Scorecard + SLAs), identify each tab name
- Note the currently active tab
- Describe purpose of each visible tab
- Identify any navigation links or buttons

## 🎯 BUSINESS VALUE & USE CASES
- Primary audience (executives, analysts, operations teams)
- Key business questions this dashboard answers
- Decision-making scenarios it supports
- Frequency of use (daily monitoring, weekly reviews, etc.)

## ⚠️ TECHNICAL ASSESSMENT
- Data quality indicators
- Completeness of information
- Loading states or errors visible
- Performance considerations
- Mobile responsiveness (if apparent)

## 🚀 IMPROVEMENT RECOMMENDATIONS
- Missing visualizations that would add value
- Layout or design enhancements
- Additional filters or interactivity
- Data storytelling improvements
- Accessibility considerations

**CRITICAL ACCURACY REQUIREMENTS:**
- Report ONLY filter names and values that are clearly visible in the screenshot
- Do NOT assume or hallucinate filter settings (e.g., don't say "US" if you see "Overall")
- List exact tab names if multiple tabs are present
- Identify specific visualization types and their exact data
- Note any URLs, links, or navigation elements visible
- Be precise about metric names, values, and time periods shown
- If something is unclear or not visible, state that explicitly rather than guessing

**Focus on practical, implementable insights based ONLY on what you can clearly see in the image.**
        """
        
        # Initialize Bedrock client
        print("🤖 Connecting to AWS Bedrock AI...")
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name=config.aws_region,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            aws_session_token=getattr(config, 'aws_session_token', None)
        )
        
        # Prepare Bedrock request with image
        print("🧠 Analyzing dashboard with AI vision...")
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": analysis_prompt
                    }
                ]
            }
        ]
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": messages,
            "temperature": 0.1
        }
        
        # Call Bedrock with vision model
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=json.dumps(body),
            contentType='application/json'
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        analysis_text = response_body['content'][0]['text']
        
        # Generate filename based on image name and timestamp
        image_basename = os.path.splitext(os.path.basename(image_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure outputs directory exists
        os.makedirs("outputs", exist_ok=True)
        output_filename = f"outputs/dashboard_analysis_{image_basename}_{timestamp}.md"
        
        # Create enhanced markdown output
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(f"# 📊 QuickSight Dashboard Analysis Report\n\n")
            f.write(f"**📁 Image Source:** `{image_path}`\n")
            f.write(f"**📅 Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**🖼️ Image Format:** {media_type}\n")
            f.write(f"**🤖 AI Model:** Claude 3.5 Sonnet (AWS Bedrock)\n\n")
            f.write("---\n\n")
            f.write(analysis_text)
            f.write(f"\n\n---\n\n")
            f.write(f"*Report generated by QuickSight Dashboard Image Analyzer*\n")
            f.write(f"*Analysis powered by AWS Bedrock AI*\n")
        
        logger.info(f"✅ Analysis completed and saved to: {output_filename}")
        print(f"💾 Analysis saved to: {output_filename}")
        
        # Show a preview of key insights
        print("\n🔍 Quick Preview:")
        print("="*50)
        lines = analysis_text.split('\n')
        preview_lines = []
        section_count = 0
        
        for line in lines:
            if line.strip().startswith('##') and section_count < 3:  # Show first 3 sections
                section_count += 1
                preview_lines.append(f"  {line.strip()}")
            elif line.strip() and section_count <= 3 and len(preview_lines) < 15:
                if line.strip().startswith('-'):
                    preview_lines.append(f"    {line.strip()}")
                elif not line.strip().startswith('#'):
                    preview_lines.append(f"  {line.strip()}")
        
        for line in preview_lines[:12]:  # Limit preview length
            print(line)
        
        if len(preview_lines) > 12:
            print("  ...")
        
        print(f"\n📖 View complete analysis: {output_filename}")
        
        return output_filename
        
    except Exception as e:
        logger.error(f"❌ Failed to analyze image: {e}")
        print(f"❌ Analysis failed: {e}")
        
        # Provide helpful error context
        if "ExpiredToken" in str(e):
            print("💡 Your AWS credentials have expired. Please refresh them in Okta.")
        elif "Access" in str(e) or "Permission" in str(e):
            print("💡 Check your AWS credentials and Bedrock permissions.")
        elif "not found" in str(e).lower():
            print("💡 Double-check the image file path.")
        else:
            print("💡 Please verify your AWS credentials and image file.")
        
        return None


def add_screenshot_references(documentation: str, image_path: str) -> str:
    """
    Add screenshot reference information to documentation in professional format.
    """
    # Add clean reference note at the top
    screenshot_note = f"""
**Source Dashboard Screenshot:** {image_path}

"""
    
    # Insert after the first section
    lines = documentation.split('\n')
    insert_index = 1
    for i, line in enumerate(lines):
        if line.startswith('**Objective**'):
            insert_index = i
            break
    
    lines.insert(insert_index, screenshot_note)
    return '\n'.join(lines)


def generate_dashboard_documentation(analysis_file: str, image_path: str) -> Optional[str]:
    """Generate user-friendly how-to documentation from dashboard analysis."""
    try:
        logger.info(f"📝 Generating how-to documentation from: {analysis_file}")
        
        # Read the analysis file
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_content = f.read()
        
        # Enhanced documentation prompt based on user's Cash Dash example
        documentation_prompt = f"""
You are a technical writer specializing in business intelligence dashboard documentation. Create professional documentation following the exact format and style of GoDaddy's Cash Dash documentation.

**DASHBOARD ANALYSIS:**
{analysis_content}

**CREATE DOCUMENTATION FOLLOWING THIS EXACT STRUCTURE AND STYLE:**

**Objective**

[Write a clear, professional paragraph explaining the goal of this dashboard, what it provides overview of, and what performance it tracks. Be specific about business context and purpose. No emojis.]

**Dashboard Overview**

The [Dashboard Name] in QuickSight has the following views:
1. [View Name 1]
2. [View Name 2] 
3. [View Name 3]
[etc.]

For [Dashboard Name] in QuickSight, you can also navigate to [X] other additional views for additional insights:
1. [Additional View 1]
2. [Additional View 2]
All these views are discussed in detail below.

**New Additions, Features and Changes**

[If this is an existing dashboard, note improvements. If new, describe key features.]

1. **Feature Name**: [Detailed explanation of what this feature does, how it works, and its business value. Include specific details about performance, timing, or technical specifications.]

2. **Feature Name**: [Continue with numbered list format. Be specific about functionality, comparison capabilities, and business benefits.]

[Continue for all major features]

**Detailed Overview of Each View**

**1. [View Name]**

[Detailed paragraph explaining what this view shows, what performance metrics it tracks, and how it relates to business objectives. Include specific details about data sources, time periods, and calculation methods.]

**Metrics Reported**

1. **Metric Name**: [Detailed explanation of what this metric measures, how it's calculated, any toggle options, and business significance. Include formulas where relevant.]

2. **Metric Name**: [Continue with detailed explanations. Be specific about calculation methods, data sources, and business context.]

[Continue for all metrics]

**How tos**

1. **How to [specific task]?**
   - [Detailed step-by-step instructions with specific examples]
   - [Include any restrictions, permissions, or special considerations]

2. **[Next practical task]**
   - [Step-by-step instructions]
   - [Specific details about process or requirements]

**WRITING GUIDELINES:**
- Use professional, technical language similar to business documentation
- Be specific with numbers, percentages, time periods, and technical details
- Avoid emojis and casual language
- Use numbered lists for features and steps
- Use bold for feature names and important terms
- Include exact metric definitions and calculation methods
- Provide specific business context for each feature
- Write in third person, professional tone
- Include concrete examples where helpful

Create documentation that matches the professional style and depth of the Cash Dash example.
        """
        
        # Initialize Bedrock client
        print("🤖 Generating how-to documentation with AI...")
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name=config.aws_region,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            aws_session_token=getattr(config, 'aws_session_token', None)
        )
        
        # Prepare Bedrock request
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": documentation_prompt
                    }
                ]
            }
        ]
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": messages,
            "temperature": 0.1
        }
        
        # Call Bedrock
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=json.dumps(body),
            contentType='application/json'
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        documentation_text = response_body['content'][0]['text']
        
        # Generate filename  
        image_basename = os.path.splitext(os.path.basename(image_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure outputs directory exists
        os.makedirs("outputs", exist_ok=True)
        doc_filename = f"outputs/dashboard_howto_{image_basename}_{timestamp}.md"
        
        # Enhance documentation with screenshot references
        enhanced_documentation = add_screenshot_references(documentation_text, image_path)
        
        # Create comprehensive documentation file
        with open(doc_filename, 'w', encoding='utf-8') as f:
            f.write(enhanced_documentation)
            f.write(f"\n\n---\n\n")
            f.write(f"**📁 Original Image:** `{image_path}`\n")
            f.write(f"**📄 Analysis Source:** `{analysis_file}`\n")
            f.write(f"**📅 Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**🤖 AI Model:** Claude 3.5 Sonnet (AWS Bedrock)\n\n")
            f.write("*Generated by QuickSight Dashboard Image Analyzer*\n")
        
        logger.info(f"✅ Documentation generated: {doc_filename}")
        print(f"📚 How-to documentation saved: {doc_filename}")
        
        return doc_filename
        
    except Exception as e:
        logger.error(f"❌ Failed to generate documentation: {e}")
        print(f"❌ Documentation generation failed: {e}")
        return None


def publish_to_confluence(doc_file: str, title: str = None) -> bool:
    """Publish documentation to Confluence."""
    try:
        from utils.confluence_uploader import ConfluenceUploader
        
        print("🔗 Publishing documentation to Confluence...")
        
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
        
        # Upload to Confluence
        page_url = uploader.upload_content(
            title=title,
            content=content,
            content_type='markdown'
        )
        
        if page_url:
            print(f"✅ Successfully published to Confluence!")
            print(f"🔗 Page URL: {page_url}")
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


def find_recent_images():
    """Find recent image files in common locations."""
    import glob
    
    common_paths = [
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Downloads"), 
        os.path.expanduser("~/Pictures")
    ]
    
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp', '*.bmp']
    recent_images = []
    
    for path in common_paths:
        if os.path.exists(path):
            for ext in image_extensions:
                pattern = os.path.join(path, ext)
                files = glob.glob(pattern)
                for file in files:
                    # Get file modification time
                    mtime = os.path.getmtime(file)
                    recent_images.append((file, mtime))
    
    # Sort by modification time (newest first) and return top 10
    recent_images.sort(key=lambda x: x[1], reverse=True)
    return [img[0] for img in recent_images[:10]]


def upload_dashboard_image():
    """Interactive dashboard image upload and analysis."""
    print("🖼️ Upload Dashboard Screenshot")
    print("=" * 50)
    print("📋 Upload a QuickSight dashboard screenshot for AI analysis")
    print()
    print("✅ Supported formats: PNG, JPG, JPEG, GIF, WebP, BMP")
    print("✅ Maximum file size: 10MB")
    print("✅ AI-powered business insights and recommendations")
    print("✅ Detailed visualization breakdown and technical assessment")
    print()
    
    # Show helpful tips
    print("💡 Tips for best results:")
    print("   • Capture the full dashboard view")
    print("   • Include chart titles and legends")
    print("   • Ensure text is readable")
    print("   • Use PNG format for best quality")
    print()
    
    # Show recent images
    recent_images = find_recent_images()
    if recent_images:
        print("📷 Recent image files found:")
        for i, img_path in enumerate(recent_images[:5], 1):
            filename = os.path.basename(img_path)
            print(f"   {i}. {filename}")
        print(f"   0. Browse for different file")
        print()
    
    # Show common file locations
    print("📁 Common file locations:")
    print("   • ~/Desktop/")
    print("   • ~/Downloads/")
    print("   • ~/Pictures/")
    print("   • Drag & drop file path from Finder")
    print()
    
    while True:
        if recent_images:
            print("📎 Choose an option:")
            print("   • Enter number (1-5) to select recent image")
            print("   • Enter file path directly")
            print("   • Type 'quit' to exit")
            choice = input("Choice: ").strip()
        else:
            print("📎 Enter image file path (or type 'quit' to exit):")
            choice = input("Path: ").strip()
        
        if choice.lower() in ['quit', 'q', 'exit']:
            print("👋 Goodbye!")
            return
        
        if not choice:
            print("❌ Please provide a choice or file path")
            continue
        
        # Handle numbered choice for recent images
        image_path = None
        if choice.isdigit() and recent_images:
            choice_num = int(choice)
            if 1 <= choice_num <= min(5, len(recent_images)):
                image_path = recent_images[choice_num - 1]
                print(f"✅ Selected: {os.path.basename(image_path)}")
            elif choice_num == 0:
                image_path = input("📁 Enter file path: ").strip()
            else:
                print(f"❌ Invalid choice. Please enter 1-{min(5, len(recent_images))} or 0")
                continue
        else:
            image_path = choice
        
        if not image_path:
            print("❌ Please provide an image file path")
            continue
        
        # Analyze the image
        result = analyze_dashboard_image(image_path)
        
        if result:
            print(f"\n🎉 Analysis Complete!")
            print(f"📄 Full report saved to: {result}")
            print()
            
            # Ask about documentation generation
            print("📚 Additional Options:")
            print("1. 📝 Generate how-to documentation")
            print("2. 🔗 Generate how-to + publish to Confluence") 
            print("3. ⏭️  Skip to next image")
            
            doc_choice = input("Choose option (1-3): ").strip()
            
            if doc_choice == '1':
                # Generate documentation only
                doc_file = generate_dashboard_documentation(result, image_path)
                if doc_file:
                    print(f"✅ How-to documentation created: {doc_file}")
                    
            elif doc_choice == '2':
                # Generate documentation and publish to Confluence
                doc_file = generate_dashboard_documentation(result, image_path)
                if doc_file:
                    print(f"✅ How-to documentation created: {doc_file}")
                    print()
                    
                    # Ask for custom title
                    custom_title = input("📝 Enter custom title (or press Enter for auto-generated): ").strip()
                    title = custom_title if custom_title else None
                    
                    # Publish to Confluence
                    success = publish_to_confluence(doc_file, title)
                    if success:
                        print("🚀 Complete workflow finished successfully!")
                    else:
                        print("⚠️ Documentation created but Confluence publishing failed")
                        
            elif doc_choice == '3':
                print("⏭️ Skipping additional options")
            else:
                print("❌ Invalid choice, skipping additional options")
            
            print()
            
            # Ask if user wants to analyze another image
            another = input("📊 Analyze another dashboard image? (y/n): ").strip().lower()
            if another not in ['y', 'yes']:
                print("👋 Thank you for using QuickSight Dashboard Image Analyzer!")
                break
        else:
            print("\n💡 Please try again with a valid image file")
            
        print()  # Add spacing


def main():
    """Main application entry point."""
    logger.info("Starting QuickSight Dashboard Image Analyzer")
    
    print("\n" + "="*65)
    print("🚀 QuickSight Dashboard Image Analyzer")
    print("="*65)
    print("Upload and analyze QuickSight dashboard screenshots with AI")
    print()
    print("🎯 Features:")
    print("   • 🧠 AI-powered dashboard analysis")
    print("   • 📊 Business insights and recommendations") 
    print("   • 📈 Visualization breakdown and assessment")
    print("   • ⚡ Technical evaluation and improvement suggestions")
    print("   • 📝 Detailed markdown reports")
    print()
    
    try:
        upload_dashboard_image()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"\n❌ Application error: {e}")
        print("💡 Please check your AWS credentials and try again.")
    finally:
        logger.info("Application completed")


if __name__ == "__main__":
    main()