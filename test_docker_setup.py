import requests
import time
import sys

BASE_URL = "http://localhost:8001"

def wait_for_service(max_attempts=30):
    """Wait for the service to be ready"""
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Service ready after {attempt + 1} attempts")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Waiting for service... attempt {attempt + 1}/{max_attempts}")
        time.sleep(2)
    
    return False

def test_docker_deployment():
    """Test the Dockerized deployment"""
    print("🐳 Testing Docker Deployment...")
    
    if not wait_for_service():
        print("❌ Service not responding")
        return False
    
    # Test health endpoint
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code} - {response.json()}")
    
    # Test user registration
    user_data = {
        "email": "dockertest@example.com",
        "name": "Docker Test User",
        "password": "dockersecure123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Register User: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ User registration successful in Docker!")
        
        # Test login
        login_data = {
            "email": "dockertest@example.com",
            "password": "dockersecure123!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful in Docker!")
            print(f"Token received: {result['access_token'][:50]}...")
            return True
    
    return False

if __name__ == "__main__":
    success = test_docker_deployment()
    sys.exit(0 if success else 1)