from typing import Dict, List
from datetime import datetime, timezone
from services.session_service import session_manager
from services.search_service import find_best_answer
from services.llm_service import refine_with_gemini

def get_or_create_session(session_id: str) -> Dict:
    """Get existing session or create new one"""
    session = session_manager.get_session(session_id)
    if not session:
        session = {"history": [], "created_at": datetime.now(timezone.utc).isoformat()}
        session_manager.set_session(session_id, session)
    return session

def update_session_history(session_id: str, user_text: str, bot_response: str) -> None:
    """Update session with new conversation"""
    session = session_manager.get_session(session_id) or {"history": []}
    session["history"].extend([
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": bot_response}
    ])
    session_manager.set_session(session_id, session)

def process_query(text: str, history: List[Dict]) -> tuple[str, List[str]]:
    """Process user query and return response with suggestions"""
    search_result = find_best_answer(text)
    raw_answer = search_result.get("answer", "")
    suggestions = search_result.get("suggestions", [])
    refined_answer = refine_with_gemini(text, raw_answer, history)
    return refined_answer, suggestions