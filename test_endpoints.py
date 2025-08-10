import requests
import json
import sys
import io

# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8001"

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"GET / - Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
    except Exception as e:
        print(f"Error testing health endpoint: {e}")

def test_health_alternative():
    """Test the alternative health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"GET /health - Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
    except Exception as e:
        print(f"Error testing health alternative endpoint: {e}")

def test_query_endpoint():
    """Test the query endpoint"""
    try:
        data = {
            "text": "स्टार्टअप कसे सुरू करावे?",
            "history": []
        }
        response = requests.post(
            f"{BASE_URL}/query",
            headers={"Content-Type": "application/json"},
            json=data
        )
        print(f"POST /query - Status: {response.status_code}")
        response_data = response.json()
        print(f"Response: {response_data}")
        print("-" * 50)
    except Exception as e:
        print(f"Error testing query endpoint: {e}")

def test_empty_query():
    """Test query endpoint with empty text"""
    try:
        data = {
            "text": "",
            "history": []
        }
        response = requests.post(
            f"{BASE_URL}/query",
            headers={"Content-Type": "application/json"},
            json=data
        )
        print(f"POST /query (empty) - Status: {response.status_code}")
        response_data = response.json()
        print(f"Response: {response_data}")
        print("-" * 50)
    except Exception as e:
        print(f"Error testing empty query: {e}")

if __name__ == "__main__":
    print("Testing Marathi Startup Chatbot Endpoints")
    print("=" * 50)
    
    test_health_endpoint()
    test_health_alternative()
    test_query_endpoint()
    test_empty_query()
    
    print("Testing completed!")