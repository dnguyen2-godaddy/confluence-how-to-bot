"""
Image processing utilities for Dashboard Analyzer

Centralizes common image operations to eliminate code duplication.
"""

import os
import base64
import mimetypes
import logging
from typing import List, Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Centralized image processing utilities."""
    
    # Supported image formats and their MIME types
    SUPPORTED_FORMATS = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg', 
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp'
    }
    
    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    @classmethod
    def validate_image_file(cls, image_path: str) -> Tuple[bool, str]:
        """Validate the uploaded image file."""
        if not image_path or not image_path.strip():
            return False, "❌ No image path provided"
        
        # Clean path: remove quotes but preserve original Unicode characters for file access
        original_path = image_path.strip().strip('"').strip("'")
        
        if not os.path.exists(original_path):
            return False, f"❌ Image file not found: {original_path}"
        
        # Check file size
        file_size = os.path.getsize(original_path)
        if file_size > cls.MAX_FILE_SIZE:
            return False, f"❌ Image file too large: {file_size / (1024*1024):.1f}MB (max {cls.MAX_FILE_SIZE / (1024*1024):.0f}MB)"
        
        # Check file extension
        file_ext = os.path.splitext(original_path)[1].lower()
        if file_ext not in cls.SUPPORTED_FORMATS:
            return False, f"❌ Unsupported format: {file_ext}. Supported: {', '.join(cls.SUPPORTED_FORMATS.keys())}"
        
        return True, "✅ Valid image file"
    
    @classmethod
    def get_media_type(cls, image_path: str) -> str:
        """Get MIME type for an image file."""
        file_ext = os.path.splitext(image_path)[1].lower()
        return cls.SUPPORTED_FORMATS.get(file_ext, 'image/jpeg')
    
    @classmethod
    def encode_image_to_base64(cls, image_path: str) -> Optional[str]:
        """Encode image file to base64 string."""
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            return None
    
    @classmethod
    def prepare_image_for_bedrock(cls, image_path: str) -> Optional[Dict[str, Any]]:
        """Prepare image data for AWS Bedrock API."""
        # Validate image first
        is_valid, message = cls.validate_image_file(image_path)
        if not is_valid:
            logger.error(f"Image validation failed: {message}")
            return None
        
        # Clean path
        clean_path = image_path.strip().strip('"').strip("'")
        
        # Encode image
        image_base64 = cls.encode_image_to_base64(clean_path)
        if not image_base64:
            return None
        
        # Get media type
        media_type = cls.get_media_type(clean_path)
        
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_base64
            }
        }
    
    @classmethod
    def prepare_multiple_images_for_bedrock(cls, image_paths: List[str]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Prepare multiple images for AWS Bedrock API."""
        image_data_list = []
        valid_image_paths = []
        
        for i, image_path in enumerate(image_paths, 1):
            logger.info(f"Processing image {i}/{len(image_paths)}: {os.path.basename(image_path)}")
            
            # Handle potential unicode issues in file paths
            if not os.path.exists(image_path):
                # Try to find the file with glob to handle unicode characters
                import glob
                dir_path = os.path.dirname(image_path) if os.path.dirname(image_path) else "."
                basename = os.path.basename(image_path)
                pattern = os.path.join(dir_path, "*" + basename.replace(" ", "*").replace("PM", "*PM*").replace("AM", "*AM*") + "*")
                matches = glob.glob(pattern)
                if matches:
                    image_path = matches[0]
                    logger.info(f"Resolved path to: {image_path}")
            
            # Prepare image data
            image_data = cls.prepare_image_for_bedrock(image_path)
            if image_data:
                image_data_list.append(image_data)
                valid_image_paths.append(image_path.strip().strip('"').strip("'"))
            else:
                logger.warning(f"Skipping invalid image: {image_path}")
        
        return image_data_list, valid_image_paths
    
    @classmethod
    def copy_images_to_outputs(cls, image_paths: List[str], output_dir: str = "outputs/images") -> List[str]:
        """Copy images to outputs directory for embedding."""
        import shutil
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        copied_files = []
        for image_path in image_paths:
            try:
                image_name = os.path.basename(image_path)
                dest_path = os.path.join(output_dir, image_name)
                shutil.copy2(image_path, dest_path)
                copied_files.append(dest_path)
                logger.info(f"Copied image: {image_name}")
            except Exception as e:
                logger.warning(f"Could not copy {os.path.basename(image_path)}: {e}")
        
        return copied_files
    
    @classmethod
    def get_image_info(cls, image_path: str) -> Dict[str, Any]:
        """Get comprehensive information about an image file."""
        try:
            stat = os.stat(image_path)
            file_ext = os.path.splitext(image_path)[1].lower()
            
            return {
                'path': image_path,
                'filename': os.path.basename(image_path),
                'size_bytes': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'extension': file_ext,
                'media_type': cls.get_media_type(image_path),
                'modified_time': stat.st_mtime,
                'is_valid': cls.validate_image_file(image_path)[0]
            }
        except Exception as e:
            logger.error(f"Failed to get image info for {image_path}: {e}")
            return {}
