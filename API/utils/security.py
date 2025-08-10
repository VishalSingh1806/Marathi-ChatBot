import secrets

def generate_csrf_token() -> str:
    """Generate a secure CSRF token"""
    return secrets.token_urlsafe(32)

def validate_csrf_token(token: str, session_id: str) -> bool:
    """Validate CSRF token for session"""
    import logging
    from services.session_service import session_manager
    
    logging.info(f"🔍 Validating CSRF token for session {session_id[:8]}")
    logging.info(f"🔍 Received token: {token[:10]}...")
    
    stored_token = session_manager.get_csrf_token(session_id)
    logging.info(f"🔍 Stored token: {stored_token[:10] if stored_token else 'None'}...")
    
    if not stored_token:
        logging.error(f"❌ No CSRF token found in Redis for session {session_id[:8]}")
        return False
    
    is_valid = stored_token == token
    logging.info(f"{'✅' if is_valid else '❌'} CSRF token validation result: {is_valid}")
    return is_valid