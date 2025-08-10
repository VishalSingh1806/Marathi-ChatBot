import base64
import json

def encrypt_data(data: dict) -> str:
    """Simple obfuscation (not real encryption for demo)"""
    json_str = json.dumps(data)
    return base64.b64encode(json_str.encode()).decode()

def decrypt_data(encrypted_data: str) -> dict:
    """Simple deobfuscation"""
    decoded = base64.b64decode(encrypted_data.encode()).decode()
    return json.loads(decoded)