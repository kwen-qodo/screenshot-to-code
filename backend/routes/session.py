from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

from middleware.session import get_session, require_session
from models.session import session_store, UserSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/session", tags=["session"])


class TrackActionRequest(BaseModel):
    """Request model for tracking user actions."""
    action_type: str
    metadata: Optional[Dict[str, Any]] = None


class SessionInfoResponse(BaseModel):
    """Response model for session information."""
    session_id: str
    created_at: str
    last_activity: str
    action_count: int
    metadata: Dict[str, Any]


class TrackActionResponse(BaseModel):
    """Response model for action tracking."""
    success: bool
    message: str
    action_count: int


class SessionStatsResponse(BaseModel):
    """Response model for session statistics."""
    active_sessions: int
    total_actions: int


@router.get("/info", response_model=SessionInfoResponse)
async def get_session_info(request: Request):
    """Retrieve current session details."""
    session = get_session(request)
    
    if not session:
        raise HTTPException(status_code=404, detail="No active session found")
    
    return SessionInfoResponse(
        session_id=session.session_id,
        created_at=session.created_at.isoformat(),
        last_activity=session.last_activity.isoformat(),
        action_count=len(session.user_actions),
        metadata=session.metadata
    )


@router.post("/track", response_model=TrackActionResponse)
async def track_action(request: Request, action_request: TrackActionRequest):
    """Log user actions to the current session."""
    session = get_session(request)
    
    if not session:
        raise HTTPException(status_code=404, detail="No active session found")
    
    try:
        session.add_action(
            action_type=action_request.action_type,
            metadata=action_request.metadata
        )
        
        logger.info(f"Tracked action '{action_request.action_type}' for session {session.session_id}")
        
        return TrackActionResponse(
            success=True,
            message=f"Action '{action_request.action_type}' tracked successfully",
            action_count=len(session.user_actions)
        )
    
    except Exception as e:
        logger.error(f"Failed to track action: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track action")


@router.delete("/clear")
async def clear_session(request: Request):
    """Clear current session data."""
    session = get_session(request)
    
    if not session:
        raise HTTPException(status_code=404, detail="No active session found")
    
    try:
        success = session_store.delete_session(session.session_id)
        
        if success:
            logger.info(f"Cleared session {session.session_id}")
            return {"success": True, "message": "Session cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear session")
    
    except Exception as e:
        logger.error(f"Failed to clear session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear session")


@router.get("/actions")
async def get_session_actions(request: Request, limit: Optional[int] = 100):
    """Get user actions for the current session."""
    session = get_session(request)
    
    if not session:
        raise HTTPException(status_code=404, detail="No active session found")
    
    # Get the most recent actions (limited by the limit parameter)
    actions = session.user_actions[-limit:] if limit else session.user_actions
    
    return {
        "session_id": session.session_id,
        "total_actions": len(session.user_actions),
        "actions": [
            {
                "action_type": action.action_type,
                "timestamp": action.timestamp.isoformat(),
                "metadata": action.metadata
            }
            for action in actions
        ]
    }


@router.get("/stats", response_model=SessionStatsResponse)
async def get_session_stats():
    """Get overall session statistics."""
    active_sessions = session_store.get_active_session_count()
    
    # Calculate total actions across all sessions
    total_actions = 0
    for session_id in session_store._sessions:
        session = session_store.get_session(session_id)
        if session:
            total_actions += len(session.user_actions)
    
    return SessionStatsResponse(
        active_sessions=active_sessions,
        total_actions=total_actions
    )


@router.post("/cleanup")
async def cleanup_expired_sessions(max_age_hours: int = 24):
    """Clean up expired sessions (admin endpoint)."""
    try:
        removed_count = session_store.cleanup_expired_sessions(max_age_hours)
        logger.info(f"Cleaned up {removed_count} expired sessions")
        
        return {
            "success": True,
            "message": f"Cleaned up {removed_count} expired sessions",
            "removed_count": removed_count,
            "remaining_sessions": session_store.get_active_session_count()
        }
    
    except Exception as e:
        logger.error(f"Failed to cleanup sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cleanup sessions")


@router.get("/export")
async def export_session_data(request: Request):
    """Export current session data as JSON."""
    session = get_session(request)
    
    if not session:
        raise HTTPException(status_code=404, detail="No active session found")
    
    return session.to_dict()