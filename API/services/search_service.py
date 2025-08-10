import pandas as pd
from sentence_transformers import SentenceTransformer, util
import logging

try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    logging.info("SentenceTransformer model loaded successfully")
except ImportError as e:
    logging.error(f"SentenceTransformer library not available: {e}")
    model = None
except OSError as e:
    logging.error(f"Failed to download/load SentenceTransformer model: {e}")
    model = None
except Exception as e:
    logging.error(f"Unexpected error loading SentenceTransformer model: {e}")
    model = None

try:
    df = pd.read_csv("data/startup_knowledge.csv")
    df = df.dropna(subset=["question", "answer"])
    df["question"] = df["question"].astype(str)
    
    if model is not None:
        df["embedding"] = df["question"].apply(lambda x: model.encode(x, convert_to_tensor=True))
        logging.info(f"Knowledge base loaded with {len(df)} entries")
    else:
        df["embedding"] = None
except FileNotFoundError as e:
    logging.error(f"Knowledge base CSV file not found: {e}")
    df = pd.DataFrame()
except pd.errors.EmptyDataError as e:
    logging.error(f"Knowledge base CSV file is empty: {e}")
    df = pd.DataFrame()
except KeyError as e:
    logging.error(f"Required columns missing in knowledge base: {e}")
    df = pd.DataFrame()
except Exception as e:
    logging.error(f"Unexpected error loading knowledge base: {e}")
    df = pd.DataFrame()

def find_best_answer(user_query: str) -> dict:
    try:
        if model is None or df.empty:
            return {
                "answer": "माफ करा, ज्ञान आधार उपलब्ध नाही. कृपया सिस्टम तपासा.",
                "suggestions": []
            }
        
        query_vec = model.encode(user_query, convert_to_tensor=True)
        scores = [util.cos_sim(query_vec, row)[0][0].item() for row in df["embedding"]]

        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:4]
        top_matches = df.iloc[top_indices]

        answer = top_matches.iloc[0]["answer"]
        similar_questions = list(top_matches.iloc[1:]["question"])

        return {
            "answer": answer,
            "suggestions": similar_questions
        }
    except Exception as e:
        logging.error(f"Error in find_best_answer: {e}")
        return {
            "answer": "माफ करा, उत्तर शोधताना समस्या आली. कृपया पुन्हा प्रयत्न करा.",
            "suggestions": []
        }