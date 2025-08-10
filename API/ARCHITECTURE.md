# Backend Architecture

## Modular Structure

The backend has been reorganized into a clean modular architecture with clear separation of concerns:

### 📁 config/
- **settings.py**: Centralized configuration management
- All environment variables and app settings

### 📁 models/
- **request_models.py**: Pydantic models for API requests
- **response_models.py**: Pydantic models for API responses
- Clean separation of input/output data structures

### 📁 services/
- **llm_service.py**: Google Gemini LLM integration
- **search_service.py**: Knowledge base search with embeddings
- **session_service.py**: Redis session management
- **monitoring_service.py**: Sentry error tracking + Prometheus metrics
- External service integrations

### 📁 utils/
- **validation.py**: Input validation and sanitization
- **security.py**: CSRF token generation and validation
- Reusable utility functions

### 📁 core/
- **business_logic.py**: Core application logic
- Session management, query processing
- Main business workflows

### 📁 data/
- **startup_knowledge.csv**: Knowledge base
- Static data files

## Benefits

✅ **Separation of Concerns**: Each module has a single responsibility
✅ **Maintainability**: Easy to locate and modify specific functionality  
✅ **Testability**: Individual modules can be tested in isolation
✅ **Scalability**: New features can be added without affecting existing code
✅ **Clean Imports**: Clear dependency structure
✅ **Production Ready**: Professional code organization

## Import Structure

```python
# Main application
from models import QueryRequest, QueryResponse
from services import init_sentry, session_manager
from utils import sanitize_for_logging, generate_csrf_token
from core import process_query, get_or_create_session
from config import get_settings
```

## File Dependencies

```
main.py
├── models/ (request/response schemas)
├── services/ (external integrations)
├── utils/ (helper functions)
├── core/ (business logic)
└── config/ (settings)
```

This structure follows Python best practices and makes the codebase enterprise-ready.