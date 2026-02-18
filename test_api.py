#!/usr/bin/env python3
"""
Test script for RAG Microservice API
"""

import requests
import sys
import time

API_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_index_document(file_path):
    """Test document indexing"""
    print(f"\n📄 Testing document indexing: {file_path}")
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_URL}/index", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document indexed successfully")
            print(f"   Message: {result['message']}")
            print(f"   Chunks: {result['chunks_indexed']}")
            return True
        else:
            print(f"❌ Indexing failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_chat(query):
    """Test chat endpoint"""
    print(f"\n💬 Testing chat: {query}")
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"query": query, "max_length": 512}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat response received")
            print(f"   Answer: {result['answer'][:200]}...")
            print(f"   Sources: {len(result['sources'])} documents")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 RAG Microservice API Test Suite\n")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("\n❌ Backend is not running. Start it with: cd backend && python main.py")
        sys.exit(1)
    
    # Wait a bit for models to load if just started
    time.sleep(2)
    
    # Test indexing (if data file exists)
    test_file = "data/Microbiology-A-Laboratory-Experience.pdf"
    if test_index_document(test_file):
        # Wait for indexing to complete
        time.sleep(2)
        
        # Test chat
        test_chat("What is this document about?")
        test_chat("Explain the main concepts covered in the document.")
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")

if __name__ == "__main__":
    main()
