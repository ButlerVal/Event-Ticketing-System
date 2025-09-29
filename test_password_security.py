import requests
import time

BASE_URL = "http://127.0.0.1:8001"

def test_password_strength():
    """Test password strength requirements"""
    weak_passwords = [
        "123",
        "password",
        "12345678",
        "qwerty",
        "admin"
    ]
    
    print("🔒 Testing Password Strength Requirements...")
    
    for i, weak_password in enumerate(weak_passwords):
        user_data = {
            "email": f"weakpass{i}@example.com",
            "name": f"Weak Password User {i}",
            "password": weak_password
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        
        if response.status_code == 422:
            print(f"✅ Correctly rejected weak password: '{weak_password}'")
        else:
            print(f"❌ Accepted weak password: '{weak_password}' - Status: {response.status_code}")

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\n🚦 Testing Rate Limiting...")
    
    # Make rapid requests
    for i in range(15):
        response = requests.get(f"{BASE_URL}/health")
        print(f"Request {i+1}: {response.status_code}")
        
        if response.status_code == 429:
            print("✅ Rate limiting is working!")
            break
        
        time.sleep(0.1)  # Small delay

def test_sql_injection_attempt():
    """Test SQL injection protection"""
    print("\n💉 Testing SQL Injection Protection...")
    
    malicious_inputs = [
        "admin@example.com' OR '1'='1",
        "admin@example.com'; DROP TABLE users; --",
        "admin@example.com' UNION SELECT * FROM users --"
    ]
    
    for malicious_input in malicious_inputs:
        login_data = {
            "email": malicious_input,
            "password": "anypassword"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 422 or response.status_code == 401:
            print(f"✅ Protected against: {malicious_input[:30]}...")
        else:
            print(f"❌ Potential vulnerability with: {malicious_input[:30]}...")

def test_xss_protection():
    """Test XSS protection"""
    print("\n🕸️ Testing XSS Protection...")
    
    xss_payloads = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>"
    ]
    
    for payload in xss_payloads:
        user_data = {
            "email": "xsstest@example.com",
            "name": payload,
            "password": "securepassword123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        
        if response.status_code in [400, 422]:
            print(f"✅ Protected against XSS: {payload[:20]}...")
        elif response.status_code == 201:
            # Check if the payload was sanitized
            user = response.json()
            if payload not in user.get('name', ''):
                print(f"✅ XSS payload sanitized: {payload[:20]}...")
            else:
                print(f"❌ XSS vulnerability: {payload[:20]}...")

if __name__ == "__main__":
    print("🛡️ Advanced Security Testing")
    print("Make sure your service is running on port 8001!")
    print("=" * 60)
    
    test_password_strength()
    test_rate_limiting()
    test_sql_injection_attempt()
    test_xss_protection()
    
    print("\n" + "=" * 60)
    print("🛡️ Advanced security testing complete!")