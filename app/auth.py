import hmac
import hashlib
import time
import json
import base64
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from .database import verify_admin_credentials, get_db_connection

SECRET_KEY = "enamel-microscopic-dentistry-secure-admin-key-2026-mysuru"

def create_admin_token(username: str, role: str = "admin", expires_in_seconds: int = 86400 * 7) -> str:
    """Generates a signed HMAC-SHA256 session token."""
    payload = {
        "sub": username,
        "role": role,
        "exp": int(time.time()) + expires_in_seconds
    }
    raw = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    b64_payload = base64.urlsafe_b64encode(raw).decode('utf-8').rstrip('=')
    sig = hmac.new(SECRET_KEY.encode('utf-8'), b64_payload.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"{b64_payload}.{sig}"

def verify_admin_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies a signed HMAC-SHA256 session token and checks expiry."""
    if not token or "." not in token:
        return None
    try:
        b64_payload, sig = token.split('.', 1)
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), b64_payload.encode('utf-8'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        
        # Add padding back if necessary
        padding = 4 - (len(b64_payload) % 4)
        if padding != 4:
            b64_payload += '=' * padding
            
        payload = json.loads(base64.urlsafe_b64decode(b64_payload).decode('utf-8'))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None

def get_current_admin(request: Request) -> Dict[str, Any]:
    """Dependency that checks for admin token in cookies or Authorization header."""
    token = request.cookies.get("admin_session")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    payload = verify_admin_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid"
        )
    return payload

def optional_admin(request: Request) -> Optional[Dict[str, Any]]:
    """Returns admin payload if logged in, otherwise None without raising exception."""
    token = request.cookies.get("admin_session")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
    if token:
        return verify_admin_token(token)
    return None
