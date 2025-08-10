import redis
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import logging
from config import get_settings

settings = get_settings()

redis_client = redis.Redis(
    host=settings["redis_host"],
    port=settings["redis_port"],
    db=settings["redis_db"],
    password=settings["redis_password"],
    decode_responses=True
)

class RedisSessionManager:
    def __init__(self, ttl_hours: int = 24):
        self.ttl = ttl_hours * 3600
        
    def get_session(self, session_id: str) -> Optional[Dict]:
        try:
            data = redis_client.get(f"session:{session_id}")
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logging.error(f"Redis get error: {e}")
            return None
    
    def set_session(self, session_id: str, data: Dict) -> bool:
        try:
            redis_client.setex(
                f"session:{session_id}", 
                self.ttl, 
                json.dumps(data, default=str)
            )
            return True
        except Exception as e:
            logging.error(f"Redis set error: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        try:
            redis_client.delete(f"session:{session_id}")
            return True
        except Exception as e:
            logging.error(f"Redis delete error: {e}")
            return False
    
    def get_csrf_token(self, session_id: str) -> Optional[str]:
        try:
            key = f"csrf:{session_id}"
            token = redis_client.get(key)
            logging.info(f"🔍 Redis GET csrf:{session_id[:8]} = {token[:10] if token else 'None'}...")
            return token
        except Exception as e:
            logging.error(f"Redis CSRF get error: {e}")
            return None
    
    def set_csrf_token(self, session_id: str, token: str) -> bool:
        try:
            key = f"csrf:{session_id}"
            redis_client.setex(key, self.ttl, token)
            logging.info(f"🔍 Redis SET csrf:{session_id[:8]} = {token[:10]}... (TTL: {self.ttl}s)")
            return True
        except Exception as e:
            logging.error(f"Redis CSRF set error: {e}")
            return False

session_manager = RedisSessionManager()