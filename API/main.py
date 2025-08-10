from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import logging
import uuid
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from google.cloud.speech import SpeechClient, RecognitionAudio, RecognitionConfig

from models import QueryRequest, QueryResponse, TranscribeRequest, TranscribeResponse, CSRFTokenResponse, EncryptedRequest, EncryptedResponse
from services import init_sentry, MetricsMiddleware, get_metrics, track_llm_request, track_audio_transcription
from utils import sanitize_for_logging, validate_audio_file, generate_csrf_token, validate_csrf_token, encrypt_data, decrypt_data
from core import get_or_create_session, update_session_history, process_query
from config import get_settings

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize monitoring
init_sentry()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Get settings
settings = get_settings()

app = FastAPI(title="Marathi Startup Chatbot", description="A Marathi-speaking chatbot for startup information")

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)



# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings["allowed_origins"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token", "X-Session-ID"],
)

# --- API Endpoints ---
@app.get("/")
async def root():
    """Health check endpoint"""
    logging.info("Root endpoint accessed")
    return {"message": "Marathi Startup Chatbot is running", "language": "marathi"}

# Encrypted API endpoints with obfuscated routes
@app.post("/api/v1/secure/process", response_model=EncryptedResponse)
@limiter.limit("20/minute")
async def secure_query(request: Request, encrypted_request: EncryptedRequest):
    """Encrypted query endpoint"""
    try:
        logging.info(f"🔐 Secure endpoint called with encrypted data: {encrypted_request.data[:50]}...")
        
        # Decrypt request
        try:
            decrypted_data = decrypt_data(encrypted_request.data)
            logging.info(f"🔓 Decrypted data: {decrypted_data}")
        except Exception as e:
            logging.error(f"❌ Failed to decrypt data: {e}")
            raise HTTPException(status_code=400, detail="Failed to decrypt request")
        
        try:
            query_data = QueryRequest(**decrypted_data)
            logging.info(f"✅ Parsed query data - session_id: {query_data.session_id}, has_csrf: {bool(query_data.csrf_token)}, text_length: {len(query_data.text) if query_data.text else 0}")
        except Exception as e:
            logging.error(f"❌ Failed to parse query data: {e}")
            raise HTTPException(status_code=400, detail="Invalid request format")
        
        session_id = query_data.session_id or str(uuid.uuid4())
        logging.info(f"🔍 Processing query from session {session_id[:8]}")
        
        # Simplified CSRF validation - only validate if both session_id and csrf_token are provided
        if query_data.session_id and query_data.csrf_token:
            logging.info(f"🔒 Validating CSRF token for session {query_data.session_id[:8]}")
            if not validate_csrf_token(query_data.csrf_token, query_data.session_id):
                logging.error(f"❌ Invalid CSRF token for session {query_data.session_id[:8]}")
                raise HTTPException(status_code=403, detail="Invalid CSRF token")
            logging.info(f"✅ CSRF token valid for session {query_data.session_id[:8]}")
        else:
            logging.info(f"🆕 No CSRF validation - treating as new session")
        
        if not query_data.text or not query_data.text.strip():
            raise HTTPException(status_code=400, detail="Query text cannot be empty")
        
        session = get_or_create_session(session_id)
        
        # Generate CSRF token for new sessions
        if not query_data.session_id:
            logging.info(f"🆕 Generating CSRF token for new session {session_id[:8]}")
            csrf_token = generate_csrf_token()
            from services.session_service import session_manager
            session_manager.set_csrf_token(session_id, csrf_token)
            logging.info(f"✅ CSRF token generated and stored for session {session_id[:8]}")
        else:
            logging.info(f"🔄 Using existing session {session_id[:8]}")
        
        refined_answer, suggestions = process_query(query_data.text, session["history"])
        update_session_history(session_id, query_data.text, refined_answer)
        
        track_llm_request(True)
        
        # Encrypt response
        response_data = {
            "answer": refined_answer,
            "similar_questions": suggestions,
            "session_id": session_id
        }
        encrypted_response = encrypt_data(response_data)
        
        return EncryptedResponse(data=encrypted_response)
        
    except HTTPException as he:
        logging.error(f"❌ HTTPException in secure endpoint: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        logging.error(f"❌ Unexpected error in secure endpoint: {e}", exc_info=True)
        track_llm_request(False)
        error_response = {
            "answer": "माफ करा, सर्वरमध्ये समस्या आली आहे. कृपया पुन्हा प्रयत्न करा.",
            "similar_questions": [],
            "session_id": query_data.session_id if 'query_data' in locals() else str(uuid.uuid4())
        }
        encrypted_error = encrypt_data(error_response)
        return EncryptedResponse(data=encrypted_error)

@app.post("/api/v1/secure/audio", response_model=EncryptedResponse)
@limiter.limit("5/minute")
async def secure_transcribe(request: Request, file: UploadFile = File(...)):
    """Encrypted transcription endpoint"""
    try:
        # Get CSRF token and session ID from headers
        csrf_token = request.headers.get("X-CSRF-Token")
        session_id = request.headers.get("X-Session-ID")
        
        # Validate CSRF token
        if not csrf_token or not session_id or not validate_csrf_token(csrf_token, session_id):
            raise HTTPException(status_code=403, detail="Invalid CSRF token")
        
        # Validate file
        if not validate_audio_file(file):
            raise HTTPException(status_code=400, detail="Invalid audio file type or size")
        
        client = SpeechClient()
        content = await file.read()
        audio = RecognitionAudio(content=content)
        
        config = RecognitionConfig(
            encoding=RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="mr-IN",
            enable_automatic_punctuation=True
        )
        
        response = client.recognize(config=config, audio=audio)
        
        transcript = ""
        if response.results and response.results[0].alternatives:
            transcript = response.results[0].alternatives[0].transcript
        
        track_audio_transcription(True)
        
        # Encrypt response
        response_data = {"transcript": transcript}
        encrypted_response = encrypt_data(response_data)
        
        return EncryptedResponse(data=encrypted_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ Error in secure transcription: {e}", exc_info=True)
        track_audio_transcription(False)
        raise HTTPException(status_code=500, detail="Failed to transcribe audio")

@app.get("/csrf-token", response_model=CSRFTokenResponse)
@limiter.limit("10/minute")
async def get_csrf_token(request: Request):
    """Get CSRF token for session"""
    from services.session_service import session_manager
    
    session_id = str(uuid.uuid4())
    csrf_token = generate_csrf_token()
    
    logging.info(f"🔑 Generating new CSRF token for session {session_id[:8]}")
    logging.info(f"🔑 CSRF token: {csrf_token[:10]}...")
    
    try:
        session_manager.set_csrf_token(session_id, csrf_token)
        logging.info(f"✅ CSRF token stored successfully for session {session_id[:8]}")
    except Exception as e:
        logging.error(f"❌ Failed to store CSRF token: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate CSRF token")
    
    return {"csrf_token": csrf_token, "session_id": session_id}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=get_metrics(), media_type="text/plain")

@app.get("/health")
async def health_check():
    """Health check with Redis connectivity"""
    from services.session_service import session_manager
    
    try:
        # Test Redis connection
        session_manager.redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "redis": "disconnected"}

@app.post("/transcribe", response_model=TranscribeResponse)
@limiter.limit("5/minute")
async def transcribe_audio(request: Request, file: UploadFile = File(...)):
    """Transcribes audio in Marathi using Google Cloud Speech-to-Text."""
    logging.info(f"Received audio file: {sanitize_for_logging(file.filename or 'unknown')}, Content-Type: {file.content_type}")
    
    # Get CSRF token and session ID from headers
    csrf_token = request.headers.get("X-CSRF-Token")
    session_id = request.headers.get("X-Session-ID")
    
    # Validate CSRF token
    if not csrf_token or not session_id or not validate_csrf_token(csrf_token, session_id):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
    
    # Validate file
    if not validate_audio_file(file):
        error_msg = f"Invalid audio file - filename: {sanitize_for_logging(file.filename or 'unknown')}, content_type: {file.content_type}"
        logging.error(error_msg)
        raise HTTPException(status_code=400, detail="Invalid audio file type or size")
    
    # Log file details for debugging
    logging.info(f"File size: {file.size if hasattr(file, 'size') else 'unknown'}")
    
    try:
        client = SpeechClient()

        content = await file.read()
        audio = RecognitionAudio(content=content)

        config = RecognitionConfig(
            encoding=RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000, # Common for webm
            language_code="mr-IN",
            enable_automatic_punctuation=True
        )

        logging.info("Sending audio to Google Speech-to-Text API...")
        response = client.recognize(config=config, audio=audio)
        logging.info("Received response from Google API.")

        if not response.results or not response.results[0].alternatives:
            logging.warning("Transcription returned no results.")
            return {"transcript": ""}

        transcript = response.results[0].alternatives[0].transcript
        logging.info(f"Transcription successful: {transcript}")
        
        # Track successful transcription
        track_audio_transcription(True)
        
        return {"transcript": transcript}

    except FileNotFoundError as e:
        logging.error(f"❌ Audio file not found: {e}")
        track_audio_transcription(False)
        raise HTTPException(status_code=400, detail="Audio file not found")
    except ValueError as e:
        logging.error(f"❌ Invalid audio format: {e}")
        track_audio_transcription(False)
        raise HTTPException(status_code=400, detail="Invalid audio format")
    except Exception as e:
        logging.error(f"❌ Error during transcription: {e}", exc_info=True)
        track_audio_transcription(False)
        raise HTTPException(status_code=500, detail="Failed to transcribe audio")

# Legacy endpoints (kept for backward compatibility)
@app.post("/query", response_model=QueryResponse)
@limiter.limit("20/minute")
async def handle_query(request: Request, query: QueryRequest):
    """Handle user queries and return responses in Marathi"""
    try:
        session_id = query.session_id or str(uuid.uuid4())
        logging.info(f"Query from session {session_id[:8]}: {sanitize_for_logging(query.text, 50)}")
        
        # Validate CSRF token for existing sessions
        if query.session_id and query.csrf_token:
            if not validate_csrf_token(query.csrf_token, query.session_id):
                raise HTTPException(status_code=403, detail="Invalid CSRF token")
        elif query.session_id:  # Session exists but no CSRF token provided
            raise HTTPException(status_code=403, detail="CSRF token required")
        
        if not query.text or not query.text.strip():
            raise HTTPException(status_code=400, detail="Query text cannot be empty")
        
        session = get_or_create_session(session_id)
        
        # Generate CSRF token for new sessions
        if not query.session_id:
            csrf_token = generate_csrf_token()
            from services.session_service import session_manager
            session_manager.set_csrf_token(session_id, csrf_token)
        
        refined_answer, suggestions = process_query(query.text, session["history"])
        update_session_history(session_id, query.text, refined_answer)
        
        # Track successful LLM request
        track_llm_request(True)
        
        logging.info(f"LLM Response to {session_id[:8]}: {sanitize_for_logging(refined_answer, 100)}")
        
        return {
            "answer": refined_answer,
            "similar_questions": suggestions,
            "session_id": session_id
        }
    except HTTPException:
        raise
    except ValueError as e:
        logging.error(f"❌ Invalid input in /query endpoint: {e}")
        track_llm_request(False)
        raise HTTPException(status_code=400, detail="Invalid input provided")
    except KeyError as e:
        logging.error(f"❌ Missing required data in /query endpoint: {e}")
        track_llm_request(False)
        raise HTTPException(status_code=400, detail="Missing required information")
    except Exception as e:
        logging.error(f"❌ Unexpected error in /query endpoint: {e}", exc_info=True)
        track_llm_request(False)
        return {
            "answer": "माफ करा, सर्वरमध्ये समस्या आली आहे. कृपया पुन्हा प्रयत्न करा.",
            "similar_questions": [],
            "session_id": query.session_id or str(uuid.uuid4())
        }

# To run: uvicorn main:app --reload