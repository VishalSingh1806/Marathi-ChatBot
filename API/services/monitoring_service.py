import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
import logging
from config import get_settings

settings = get_settings()

def init_sentry():
    sentry_dsn = settings["sentry_dsn"]
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FastApiIntegration(auto_enabling_integrations=False),
                LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)
            ],
            traces_sample_rate=0.1,
            environment=settings["environment"]
        )

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ACTIVE_SESSIONS = Gauge('active_sessions_total', 'Number of active sessions')
LLM_REQUESTS = Counter('llm_requests_total', 'Total LLM requests', ['status'])
AUDIO_TRANSCRIPTIONS = Counter('audio_transcriptions_total', 'Total audio transcriptions', ['status'])

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        method = scope["method"]
        path = scope["path"]
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = time.time() - start_time
                
                REQUEST_COUNT.labels(method=method, endpoint=path, status=status_code).inc()
                REQUEST_DURATION.labels(method=method, endpoint=path).observe(duration)
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

def get_metrics():
    return generate_latest()

def track_llm_request(success: bool):
    status = "success" if success else "error"
    LLM_REQUESTS.labels(status=status).inc()

def track_audio_transcription(success: bool):
    status = "success" if success else "error"
    AUDIO_TRANSCRIPTIONS.labels(status=status).inc()

def update_active_sessions(count: int):
    ACTIVE_SESSIONS.set(count)