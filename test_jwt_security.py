import requests
import json

BASE_URL = "http://127.0.0.1:8001"
test_token = None

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code} - {response.json()}")

def test_register_user():
    """Test registering a new user"""
    user_data = {
        "email": "securitytest2@example.com",
        "name": "Security Test User",
        "password": "supersecurepassword123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Register User: {response.status_code}")
    if response.status_code == 201:
        user = response.json()
        print(f"Registered user: {user['name']} ({user['email']}) - ID: {user['id']}")
        return user['id']
    else:
        print(f"Registration error: {response.json()}")
        return None

def test_login_jwt():
    """Test login and JWT token generation"""
    global test_token
    
    login_data = {
        "email": "securitytest2@example.com",
        "password": "supersecurepassword123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"JWT Login: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        test_token = result['access_token']
        print(f"Login successful! Token received: {test_token[:50]}...")
        print(f"User info: {result['user']['name']} - {result['user']['email']}")
        return test_token
    else:
        print(f"Login failed: {response.json()}")
        return None

def test_protected_endpoint_without_token():
    """Test accessing protected endpoint without token"""
    response = requests.get(f"{BASE_URL}/auth/me")
    print(f"Access /auth/me without token: {response.status_code}")
    if response.status_code == 403:
        print("✅ Correctly blocked unauthorized access")
    else:
        print("❌ Security issue: Should have been blocked")

def test_protected_endpoint_with_token():
    """Test accessing protected endpoint with valid token"""
    if not test_token:
        print("No token available for testing")
        return
    
    headers = {"Authorization": f"Bearer {test_token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Access /auth/me with token: {response.status_code}")
    
    if response.status_code == 200:
        user_info = response.json()
        print(f"✅ Authenticated successfully: {user_info['name']}")
    else:
        print(f"❌ Authentication failed: {response.json()}")

def test_protected_endpoint_with_invalid_token():
    """Test accessing protected endpoint with invalid token"""
    headers = {"Authorization": "Bearer invalid-token-here"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Access /auth/me with invalid token: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Correctly rejected invalid token")
    else:
        print("❌ Security issue: Should have rejected invalid token")

def test_update_user_profile():
    """Test updating user profile with authentication"""
    if not test_token:
        print("No token available for testing")
        return
    
    headers = {"Authorization": f"Bearer {test_token}"}
    update_data = {
        "name": "Updated Security Test User"
    }
    
    response = requests.put(f"{BASE_URL}/auth/me", json=update_data, headers=headers)
    print(f"Update profile: {response.status_code}")
    
    if response.status_code == 200:
        updated_user = response.json()
        print(f"✅ Profile updated: {updated_user['name']}")
    else:
        print(f"❌ Update failed: {response.json()}")

if __name__ == "__main__":
    print("🔐 Testing JWT Security Implementation...")
    print("Make sure your service is running on port 8001!")
    print("=" * 60)
    
    # Test sequence
    test_health_check()
    user_id = test_register_user()
    
    if user_id:
        # Authentication tests
        token = test_login_jwt()
        
        # Security tests
        test_protected_endpoint_without_token()
        test_protected_endpoint_with_invalid_token()
        test_protected_endpoint_with_token()
        test_update_user_profile()
    
    print("=" * 60)
    print("🔐 Security testing complete!")