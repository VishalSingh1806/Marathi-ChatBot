import re
import logging
from fastapi import UploadFile

def sanitize_for_logging(text: str, max_length: int = 100) -> str:
    """Sanitize user input for safe logging"""
    if not text:
        return "[empty]"
    sanitized = re.sub(r'[\r\n\t\x00-\x1f\x7f-\x9f]', ' ', str(text))
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    return sanitized

def validate_audio_file(file: UploadFile) -> bool:
    """Validate audio file type and size"""
    ALLOWED_EXTENSIONS = {'.wav', '.mp3', '.webm', '.ogg', '.m4a'}
    ALLOWED_MIME_TYPES = {
        'audio/wav', 'audio/mpeg', 'audio/webm', 'audio/ogg', 
        'audio/mp4', 'audio/x-m4a'
    }
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        logging.warning(f"File too large: {file.size} bytes")
        return False
    
    if file.filename:
        ext = '.' + file.filename.split('.')[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            logging.warning(f"Invalid file extension: {ext}")
            return False
    
    if file.content_type:
        mime_type = file.content_type.split(';')[0].strip()
        if mime_type not in ALLOWED_MIME_TYPES:
            logging.warning(f"Invalid MIME type: {file.content_type}")
            return False
    
    return True