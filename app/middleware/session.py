from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from ..internal.db import DB

class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db: DB):
        super().__init__(app)
        self.db = db

    async def dispatch(self, request: Request, call_next):
        session_token = request.cookies.get("session_token")

        request.state.user_email = None
        request.state.user_id = None
        request.state.authenticated = False

        if session_token:
            user = self.db.sessions.get_user_from_session(session_token)
            if user:
                request.state.user_email = user[1]
                request.state.user_id = user[0]
                request.state.authenticated = True

        response = await call_next(request)
        return response
