import google.generativeai as genai
from typing import List, Dict
from dotenv import load_dotenv
import logging
from config import get_settings

load_dotenv()
settings = get_settings()

try:
    api_key = settings["gemini_api_key"]
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except ValueError as e:
    logging.error(f"Configuration error for Gemini model: {e}")
    model = None
except ImportError as e:
    logging.error(f"Gemini library not available: {e}")
    model = None
except Exception as e:
    logging.error(f"Unexpected error initializing Gemini model: {e}")
    model = None

bot_name = "StartupBot"

def refine_with_gemini(query: str, raw_answer: str, history: List[Dict[str, str]]) -> str:
    history_parts = []
    for message in history:
        role = "वापरकर्ता" if message.get("role") == "user" else "सहाय्यक"
        content = message.get("content", message.get("text", ""))
        history_parts.append(f'{role}: {content}')
    history_str = '\n'.join(history_parts)

    prompt_text = (
        f'तुम्ही {bot_name} आहात, स्टार्टअप आणि उद्योजकतेसाठी एक मैत्रीपूर्ण आणि उपयुक्त AI सहाय्यक.\n'
        'तुमचे मुख्य उद्दिष्ट म्हणजे दिलेल्या माहितीच्या आधारे स्पष्ट आणि संक्षिप्त उत्तरे देणे.\n'
        'तुम्ही फक्त मराठीत उत्तर द्या.\n\n'
        '## संभाषण इतिहास (संदर्भासाठी):\n'
        f'{history_str}\n'
        '## सध्याचा वापरकर्त्याचा प्रश्न:\n'
        f'{query}\n\n'
        '## ज्ञान आधार माहिती (हा तुमचा मुख्य सत्याचा स्रोत आहे. यावर आधारित उत्तर द्या):\n'
        f'---\n{raw_answer}\n---\n\n'
        '## सूचना:\n'
        '1. ज्ञान आधार माहितीच्या आधारे, सध्याच्या वापरकर्त्याच्या प्रश्नाचे उत्तर द्या.\n'
        '2. प्रश्नाचा संदर्भ समजून घेण्यासाठी संभाषण इतिहास वापरा.\n'
        '3. तुमचे उत्तर छोटे, स्पष्ट आणि मैत्रीपूर्ण ठेवा.\n'
        '4. फक्त स्टार्टअप, उद्योजकता, व्यवसाय सुरू करणे, फंडिंग, आणि संबंधित विषयांबद्दल प्रश्नांची उत्तरे द्या.\n'
        '5. असंबंधित प्रश्नांसाठी, विनम्रपणे नकार द्या आणि संभाषण संबंधित विषयांकडे वळवा.\n'
        f'6. जर वापरकर्ता तुमचे नाव किंवा ओळख विचारत असेल, तर स्पष्टपणे उत्तर द्या: "मी {bot_name} आहे, तुमचा स्टार्टअप सहाय्यक."\n'
        '7. सर्व उत्तरे मराठी भाषेत द्या.'
    )

    try:
        if model is None:
            return "माफ करा, AI मॉडेल उपलब्ध नाही. कृपया API key तपासा."
        
        response = model.generate_content(prompt_text)
        if not response or not response.text:
            return "माफ करा, उत्तर मिळाले नाही. कृपया पुन्हा प्रयत्न करा."
        
        return response.text.strip()
    except ValueError as e:
        logging.error(f"Invalid input for Gemini API: {e}")
        return "माफ करा, अयोग्य इनपुट. कृपया पुन्हा प्रयत्न करा."
    except Exception as e:
        logging.error(f"Error in refine_with_gemini: {e}")
        return "माफ करा, तांत्रिक समस्या आली आहे. कृपया पुन्हा प्रयत्न करा."