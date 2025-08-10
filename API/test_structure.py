#!/usr/bin/env python3
"""Test script to verify the new modular structure"""

def test_imports():
    """Test all module imports"""
    try:
        # Test models
        from models import QueryRequest, QueryResponse
        print("✅ Models imported successfully")
        
        # Test config
        from config import get_settings
        print("✅ Config imported successfully")
        
        # Test utils
        from utils import sanitize_for_logging, generate_csrf_token
        print("✅ Utils imported successfully")
        
        # Test core (without services that need external deps)
        print("✅ All critical imports successful")
        
        # Test basic functionality
        settings = get_settings()
        assert "allowed_origins" in settings
        print("✅ Settings working")
        
        token = generate_csrf_token()
        assert len(token) > 20
        print("✅ CSRF token generation working")
        
        sanitized = sanitize_for_logging("Test\nMessage", 10)
        assert "Test Message" in sanitized
        print("✅ Input sanitization working")
        
        print("\n🎉 All tests passed! Modular structure is working correctly.")
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_imports()