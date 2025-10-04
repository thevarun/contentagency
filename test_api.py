#!/usr/bin/env python
"""
Test script for ContentAgency API.
Run the API server first: uv run api
"""
import requests

API_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint."""
    print("\n1. Testing Health Check...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_update_interests():
    """Test updating user interests."""
    print("\n2. Testing Update Interests...")
    data = {
        "user_id": "test_user",
        "interests": [
            {"topic": "Artificial Intelligence"},
            {"topic": "Machine Learning"},
            {"topic": "Data Science"}
        ]
    }
    response = requests.post(f"{API_URL}/api/v1/interests", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_update_posts():
    """Test updating recent posts."""
    print("\n3. Testing Update Posts...")
    data = {
        "user_id": "test_user",
        "posts": [
            {
                "id": "test_post_1",
                "platform": "linkedin",
                "content": "This is a test post about AI trends",
                "title": "AI Trends 2025",
                "topics": ["AI", "Tech"]
            },
            {
                "id": "test_post_2",
                "platform": "twitter",
                "content": "Quick thoughts on machine learning",
                "topics": ["ML"]
            }
        ]
    }
    response = requests.post(f"{API_URL}/api/v1/posts", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_run_brainstorm():
    """Test running brainstorm crew."""
    print("\n4. Testing Run Brainstorm...")
    print("This will take 30-60 seconds as the AI crew runs...")

    data = {"user_id": "test_user"}
    response = requests.post(f"{API_URL}/api/v1/brainstorm", json=data)
    print(f"Status: {response.status_code}")

    result = response.json()
    print(f"Status: {result.get('status')}")
    print(f"Message: {result.get('message')}")

    if result.get('result'):
        print(f"\nBrainstorm Result:")
        print(f"  Timestamp: {result['result']['timestamp']}")
        print(f"  Topics (first 200 chars): {result['result']['suggested_topics'][:200]}...")

    assert response.status_code == 200

def test_get_results():
    """Test getting brainstorm results."""
    print("\n5. Testing Get Results...")
    response = requests.get(f"{API_URL}/api/v1/results?limit=3")
    print(f"Status: {response.status_code}")

    result = response.json()
    print(f"Status: {result.get('status')}")
    print(f"Total sessions: {result.get('count')}")
    print(f"Returned sessions: {len(result.get('sessions', []))}")

    assert response.status_code == 200

def test_validation_error():
    """Test validation error handling."""
    print("\n6. Testing Validation Error...")
    # Try to send empty interests (should fail)
    data = {
        "user_id": "test_user",
        "interests": []
    }
    response = requests.post(f"{API_URL}/api/v1/interests", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 422  # Validation error

def main():
    print("=" * 60)
    print("ContentAgency API Test Suite")
    print("=" * 60)
    print(f"\nAPI URL: {API_URL}")
    print("Make sure the API server is running: uv run api")
    print("\nStarting tests...")

    try:
        test_health()
        test_update_interests()
        test_update_posts()
        test_validation_error()
        test_run_brainstorm()  # This takes time
        test_get_results()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("Make sure the API is running: uv run api")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
