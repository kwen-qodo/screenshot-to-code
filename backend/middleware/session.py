from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable, Optional
import logging

from models.session import session_store, UserSession
import config

logger = logging.getLogger(__name__)


class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware to handle user session management."""
    
    def __init__(
        self,
        app: ASGIApp,
        session_cookie_name: str = "session_id",
        session_header_name: str = "X-Session-ID",
        auto_create_session: bool = True
    ):
        super().__init__(app)
        self.session_cookie_name = session_cookie_name
        self.session_header_name = session_header_name
        self.auto_create_session = auto_create_session
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and attach session context."""
        
        # Extract session ID from header or cookie
        session_id = self._extract_session_id(request)
        session = None
        
        if session_id:
            session = session_store.get_session(session_id)
            if session:
                session.update_activity()
                logger.debug(f"Found existing session: {session_id}")
        
        # Create new session if none exists and auto_create is enabled
        if not session and self.auto_create_session:
            session = session_store.create_session(
                metadata={
                    "user_agent": request.headers.get("user-agent", ""),
                    "ip_address": self._get_client_ip(request),
                    "referer": request.headers.get("referer", "")
                }
            )
            logger.debug(f"Created new session: {session.session_id}")
        
        # Attach session to request state
        request.state.session = session
        
        # Process the request
        response = await call_next(request)
        
        # Add session ID to response headers if session exists
        if session:
            response.headers[self.session_header_name] = session.session_id
            
            # Set session cookie if it's a new session or doesn't exist
            if not session_id or session_id != session.session_id:
                response.set_cookie(
                    key=self.session_cookie_name,
                    value=session.session_id,
                    httponly=True,
                    secure=False,  # Set to True in production with HTTPS
                    samesite="lax",
                    max_age=config.SESSION_MAX_AGE_HOURS * 3600  # Convert hours to seconds
                )
        
        return response
    
    def _extract_session_id(self, request: Request) -> Optional[str]:
        """Extract session ID from request headers or cookies."""
        # First try header
        session_id = request.headers.get(self.session_header_name)
        if session_id:
            return session_id
        
        # Then try cookie
        return request.cookies.get(self.session_cookie_name)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers first (for reverse proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"


def get_session(request: Request) -> Optional[UserSession]:
    """Helper function to get the current session from request state."""
    return getattr(request.state, "session", None)


def require_session(request: Request) -> UserSession:
    """Helper function to get the current session, raising an error if none exists."""
    session = get_session(request)
    if not session:
        raise ValueError("No active session found")
    return session