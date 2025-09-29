import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code} - {response.json()}")

def test_create_user():
    """Test creating a new user"""
    user_data = {
        "email": "testuser3@example.com",
        "name": "Test User",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    print(f"Create User: {response.status_code}")
    if response.status_code == 201:
        user = response.json()
        print(f"Created user: {user['name']} ({user['email']}) - ID: {user['id']}")
        return user['id']
    else:
        print(f"Error: {response.json()}")
        return None

def test_get_user(user_id):
    """Test getting a user by ID"""
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    print(f"Get User: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"Retrieved user: {user['name']} - {user['email']}")
    else:
        print(f"Error: {response.json()}")

def test_login():
    """Test user login"""
    login_data = {
        "email": "testuser3@example.com",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/users/login", json=login_data)
    print(f"Login: {response.status_code}")
    print(f"Response content: {response.text}")  # This will show us the actual error
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"Login successful: {result}")
        except:
            print(f"Login response (not JSON): {response.text}")
    else:
        print(f"Login failed with status {response.status_code}")
        print(f"Error details: {response.text}")

def test_get_all_users():
    """Test getting all users"""
    response = requests.get(f"{BASE_URL}/users/")
    print(f"Get All Users: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f"  - {user['name']} ({user['email']})")

if __name__ == "__main__":
    print("🧪 Testing User Service...")
    print("Make sure your service is running on port 8001!")
    print("=" * 50)
    
    test_health_check()
    user_id = test_create_user()
    
    if user_id:
        test_get_user(user_id)
        test_login()
        test_get_all_users()
    
    print("=" * 50)
    print("✅ Testing complete!")