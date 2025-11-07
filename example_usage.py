"""
Example script to test the Question-Answering API.

This script demonstrates how to use the API with sample files.
Make sure the API server is running before executing this script.
"""
import requests
import json

# API endpoint
API_URL = "http://localhost:8000/qa"

# Sample files
DOCUMENT_FILE = "sample_document.json"
QUESTIONS_FILE = "sample_questions.json"


def test_api():
    """Test the QA API with sample files."""
    try:
        # Prepare files
        with open(DOCUMENT_FILE, 'rb') as doc_file, \
             open(QUESTIONS_FILE, 'rb') as questions_file:
            
            files = {
                'document': (DOCUMENT_FILE, doc_file, 'application/json'),
                'questions_file': (QUESTIONS_FILE, questions_file, 'application/json')
            }
            
            # Make request
            print("Sending request to API...")
            response = requests.post(API_URL, files=files)
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Success! Answers received:\n")
                print(json.dumps(result, indent=2))
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(response.text)
                
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("Make sure sample_document.json and sample_questions.json exist.")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the API server is running.")
        print("Start the server with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    test_api()

