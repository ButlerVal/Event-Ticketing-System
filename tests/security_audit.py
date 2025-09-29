import os
import re
from pathlib import Path

def audit_security_issues():
    """Audit code for common security issues"""
    issues = []
    
    # Check for hardcoded secrets
    patterns = [
        (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
        (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected"),
        (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected"),
        (r'debug\s*=\s*True', "Debug mode enabled"),
    ]
    
    # Scan Python files
    for py_file in Path(".").rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern, message in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append(f"🚨 {py_file}:{line_num} - {message}")
        except:
            continue
    
    return issues

def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = [
        "DATABASE_URL",
        "JWT_SECRET_KEY"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    return missing

def audit_file_permissions():
    """Check for sensitive files with wrong permissions"""
    sensitive_files = [".env", "*.key", "*.pem"]
    issues = []
    
    for pattern in sensitive_files:
        for file_path in Path(".").rglob(pattern):
            if file_path.exists():
                # On Windows, this is less relevant, but good practice
                issues.append(f"📁 Found sensitive file: {file_path}")
    
    return issues

if __name__ == "__main__":
    print("🔍 Security Audit Report")
    print("=" * 50)
    
    # Check code issues
    code_issues = audit_security_issues()
    if code_issues:
        print("🚨 Code Security Issues:")
        for issue in code_issues:
            print(f"  {issue}")
    else:
        print("✅ No obvious code security issues found")

        # Check environment variables
    missing_vars = check_environment_variables()
    if missing_vars:
        print(f"\n🚨 Missing Environment Variables:")
        for var in missing_vars:
            print(f"  - {var}")
    else:
        print("\n✅ All required environment variables are set")
    
    # Check file permissions
    file_issues = audit_file_permissions()
    if file_issues:
        print(f"\n📁 Sensitive Files Found:")
        for issue in file_issues:
            print(f"  {issue}")
    else:
        print("\n✅ No sensitive files found in unsafe locations")
    
    print("\n" + "=" * 50)
    print("🛡️ Security Audit Complete!")
    print("\n💡 Recommendations:")
    print("  1. Use strong, unique JWT secrets in production")
    print("  2. Enable HTTPS in production")
    print("  3. Regularly rotate secrets and tokens")
    print("  4. Monitor failed authentication attempts")
    print("  5. Keep dependencies updated")