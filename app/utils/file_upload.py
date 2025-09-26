"""
File upload utilities for AgriConnect
"""

import os
import uuid
from datetime import datetime
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
IMAGE_DIMENSIONS = {
    'thumbnail': (150, 150),
    'medium': (400, 400),
    'large': (800, 800)
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """Generate unique filename while preserving extension"""
    if not original_filename:
        return None
    
    # Get file extension
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return f"{timestamp}_{unique_id}.{ext}" if ext else f"{timestamp}_{unique_id}"

def create_upload_folders():
    """Create necessary upload folders if they don't exist"""
    base_upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
    
    folders = [
        os.path.join(base_upload_folder, 'products'),
        os.path.join(base_upload_folder, 'profiles'),
        os.path.join(base_upload_folder, 'thumbnails'),
    ]
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
    
    return folders

def resize_image(image_path, size, output_path=None):
    """Resize image to specified dimensions"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Calculate aspect ratio
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save resized image
            if output_path is None:
                output_path = image_path
            
            img.save(output_path, 'JPEG', quality=85, optimize=True)
            return output_path
    except Exception as e:
        current_app.logger.error(f"Error resizing image: {str(e)}")
        return None

def save_uploaded_file(file, folder='products', create_thumbnail=True):
    """
    Save uploaded file with proper validation and processing
    Returns: dict with file paths or None if failed
    """
    if not file or not allowed_file(file.filename):
        return None
    
    try:
        # Create upload folders
        create_upload_folders()
        
        # Generate unique filename
        filename = generate_unique_filename(file.filename)
        if not filename:
            return None
        
        # Define paths
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        folder_path = os.path.join(upload_folder, folder)
        file_path = os.path.join(folder_path, filename)
        
        # Save original file
        file.save(file_path)
        
        # Resize images for web optimization
        resize_image(file_path, IMAGE_DIMENSIONS['large'])
        
        result = {
            'filename': filename,
            'url': f"/static/uploads/{folder}/{filename}",
            'path': file_path
        }
        
        # Create thumbnail if requested
        if create_thumbnail:
            thumbnail_filename = f"thumb_{filename}"
            thumbnail_path = os.path.join(upload_folder, 'thumbnails', thumbnail_filename)
            
            if resize_image(file_path, IMAGE_DIMENSIONS['thumbnail'], thumbnail_path):
                result['thumbnail'] = {
                    'filename': thumbnail_filename,
                    'url': f"/static/uploads/thumbnails/{thumbnail_filename}",
                    'path': thumbnail_path
                }
        
        return result
        
    except Exception as e:
        current_app.logger.error(f"Error saving uploaded file: {str(e)}")
        return None

def save_multiple_files(files, folder='products'):
    """Save multiple uploaded files"""
    if not files:
        return []
    
    results = []
    for file in files:
        if file and file.filename:
            result = save_uploaded_file(file, folder)
            if result:
                results.append(result)
    
    return results

def delete_file(file_path):
    """Delete a file if it exists"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        current_app.logger.error(f"Error deleting file {file_path}: {str(e)}")
    return False

def delete_product_images(product):
    """Delete all images associated with a product"""
    try:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        
        # Delete main image
        if product.image_url:
            filename = os.path.basename(product.image_url)
            main_image_path = os.path.join(upload_folder, 'products', filename)
            delete_file(main_image_path)
            
            # Delete thumbnail
            thumbnail_path = os.path.join(upload_folder, 'thumbnails', f"thumb_{filename}")
            delete_file(thumbnail_path)
        
        # Delete additional images
        if product.images:
            import json
            try:
                additional_images = json.loads(product.images)
                for img_url in additional_images:
                    filename = os.path.basename(img_url)
                    img_path = os.path.join(upload_folder, 'products', filename)
                    delete_file(img_path)
                    
                    # Delete thumbnail
                    thumbnail_path = os.path.join(upload_folder, 'thumbnails', f"thumb_{filename}")
                    delete_file(thumbnail_path)
            except:
                pass
                
    except Exception as e:
        current_app.logger.error(f"Error deleting product images: {str(e)}")

def validate_image_file(file):
    """Validate uploaded image file"""
    if not file:
        return False, "No file provided"
    
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check file size (this is approximate, actual size check happens in Flask config)
    if hasattr(file, 'content_length') and file.content_length > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
    
    return True, "File is valid"