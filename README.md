# मराठी स्टार्टअप चॅटबॉट (Marathi Startup Chatbot)

A Marathi-speaking RAG (Retrieval-Augmented Generation) chatbot that provides information about startups, entrepreneurship, and business development using Google's Gemini API.

## Features

- **Marathi Language Support**: All responses are in Marathi
- **Startup Focus**: Specialized knowledge base for startup-related queries
- **No User Data Collection**: Privacy-focused design with no user registration required
- **RAG Architecture**: Combines knowledge base search with LLM refinement
- **Simple Interface**: Clean web interface for easy interaction

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Google Cloud Project with Gemini API access
- Required environment variables

### Environment Variables
Create a `.env` file in the `API` directory with:
```
GOOGLE_PROJECT_ID=your-google-project-id
GOOGLE_LOCATION=global
```

### Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   cd API
   pip install -r requirements.txt
   ```

3. **Start the server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   Or simply run the batch file:
   ```bash
   start_chatbot.bat
   ```

4. **Open the frontend**:
   Open `frontend/index.html` in your web browser

## API Endpoints

### GET /
Health check endpoint
- Returns: `{"message": "Marathi Startup Chatbot is running", "language": "marathi"}`

### POST /query
Main chat endpoint
- Input: `{"text": "your question", "history": []}`
- Output: `{"answer": "response in Marathi", "similar_questions": ["suggestion1", "suggestion2"]}`

## Knowledge Base

The chatbot uses a comprehensive knowledge base (`data/startup_knowledge.csv`) covering:

- स्टार्टअप मूलभूत गोष्टी (Startup Basics)
- व्यवसाय योजना (Business Planning)
- फंडिंग आणि गुंतवणूक (Funding & Investment)
- कायदेशीर बाबी (Legal Matters)
- मार्केटिंग आणि ब्रँडिंग (Marketing & Branding)
- टीम बिल्डिंग (Team Building)
- विविध सेक्टर्स (Various Sectors)
- सरकारी योजना (Government Schemes)

## Technology Stack

- **Backend**: FastAPI (Python)
- **LLM**: Google Gemini 2.5 Flash
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **Frontend**: React with TypeScript
- **Session Storage**: Redis
- **Monitoring**: Sentry + Prometheus
- **Data**: CSV-based knowledge base

## Backend Architecture

The backend follows a modular architecture with clear separation of concerns:

- **`config/`**: Application configuration and settings
- **`core/`**: Business logic and core functionality
- **`models/`**: Pydantic models for request/response validation
- **`services/`**: External service integrations (LLM, search, monitoring, sessions)
- **`utils/`**: Utility functions for validation and security
- **`data/`**: Knowledge base and static data files

## Changes Made

### Removed Features
- ❌ User data collection forms
- ❌ Session management
- ❌ Redis dependency
- ❌ Email notifications
- ❌ User registration/authentication

### Added Features
- ✅ Marathi language support
- ✅ Startup-focused knowledge base
- ✅ Simplified API structure
- ✅ Clean web interface
- ✅ Privacy-focused design

## Usage Examples

### Sample Questions (in Marathi):
- "स्टार्टअप कसे सुरू करावे?"
- "फंडिंग कसे मिळवावे?"
- "व्यवसाय योजना कशी तयार करावी?"
- "MVP म्हणजे काय?"
- "एंजेल इन्व्हेस्टर कसे शोधावे?"

## File Structure
```
SM/
├── API/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── business_logic.py
│   ├── data/
│   │   └── startup_knowledge.csv
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request_models.py
│   │   └── response_models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py
│   │   ├── monitoring_service.py
│   │   ├── search_service.py
│   │   └── session_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py
│   │   └── validation.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   └── src/
│       ├── components/
│       └── hooks/
├── docker-compose.yml
├── start_chatbot.bat
└── README.md
```

## Contributing

To add more knowledge to the chatbot:
1. Edit `API/data/startup_knowledge.csv`
2. Add new questions and answers in Marathi
3. Restart the server to reload the knowledge base

### Adding New Features

1. **Models**: Add new Pydantic models in `API/models/`
2. **Services**: Create new services in `API/services/`
3. **Business Logic**: Add core functionality in `API/core/`
4. **Utilities**: Add helper functions in `API/utils/`
5. **Configuration**: Update settings in `API/config/`

## License

This project is for educational and development purposes.