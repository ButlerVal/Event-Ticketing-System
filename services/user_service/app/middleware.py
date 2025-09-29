import time
import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import json
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Custom security middleware for logging and monitoring"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        start_time = time.time()
        
        # Security headers
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                
                # Add security headers
                headers[b"x-content-type-options"] = b"nosniff"
                headers[b"x-frame-options"] = b"DENY"
                headers[b"x-xss-protection"] = b"1; mode=block"
                headers[b"strict-transport-security"] = b"max-age=31536000; includeSubDomains"
                
                message["headers"] = [(k, v) for k, v in headers.items()]
            
            await send(message)
        
        # Log request
        client_ip = request.client.host if request.client else "unknown"
        
        method = request.method
        url = str(request.url)
        
        logger.info(f"Request: {method} {url} from {client_ip}")
        
        await self.app(scope, receive, send_wrapper)
        
        # Log response time
        process_time = time.time() - start_time
        logger.info(f"Response time: {process_time:.4f}s for {method} {url}")

class RateLimitMiddleware:
    """Simple rate limiting middleware"""
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        self.app = app
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # In production, use Redis or similar
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old requests
        self.requests = {
            ip: [req_time for req_time in times if current_time - req_time < self.window_seconds]
            for ip, times in self.requests.items()
        }
        
        # Check rate limit
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        if len(self.requests[client_ip]) >= self.max_requests:
            # Rate limited
            response = JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."}
            )
            await response(scope, receive, send)
            return
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        await self.app(scope, receive, send)

class CORSMiddleware:
    """Custom CORS middleware"""
    
    def __init__(self, app, allowed_origins=None, allowed_methods=None):
        self.app = app
        self.allowed_origins = allowed_origins or ["http://localhost:3000", "http://127.0.0.1:3000"]
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                
                # Add CORS headers
                origin = request.headers.get("origin")
                if origin in self.allowed_origins:
                    headers[b"access-control-allow-origin"] = origin.encode() if origin else b"*"
                
                headers[b"access-control-allow-methods"] = ", ".join(self.allowed_methods).encode()
                headers[b"access-control-allow-headers"] = b"Content-Type, Authorization"
                headers[b"access-control-allow-credentials"] = b"true"
                
                message["headers"] = [(k, v) for k, v in headers.items()]
            
            await send(message)
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response(status_code=204)
            await response(scope, receive, send_wrapper)
            return
        
        await self.app(scope, receive, send_wrapper)