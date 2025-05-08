from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import re
import uuid

from pydantic import BaseModel

from .internal.db import DB
from .internal.common import templates, VERSION, GIT_COMMIT
from .routers.table import router as table_router
from .routers.basic import router as basic_router
from .middleware.session import SessionMiddleware

db = DB()
db.migrations.run()

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(table_router)
app.include_router(basic_router)
app.add_middleware(SessionMiddleware, db=db)

@app.get("/version")
def get_version():
    return {
        "version": VERSION,
        "git_commit": GIT_COMMIT,
    }

@app.get("/", response_class=HTMLResponse)
def get_home_page(request: Request):
    user_email = request.state.user_email
    logged_in_as = f"Logged in as: {user_email}" if user_email else ""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "logged_in_as": logged_in_as or "Not logged in",
            "version": VERSION,
            "git_commit": GIT_COMMIT,
        }
    )

class LoginRequest(BaseModel):
    username: str
    password: bytes

@app.post("/login", response_class=HTMLResponse)
def login(request: Request, login_request: LoginRequest, response: Response):
    try:
        if len(login_request.username) == 0:
            raise HTTPException(status_code=400, detail="Enter an email address")
        if len(login_request.password) == 0:
            raise HTTPException(status_code=400, detail="Enter a password")
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, login_request.username):
            raise HTTPException(status_code=400, detail="Invalid email address format")
        res = db.authentication.verify_credentials(login_request.username, login_request.password)
        if not res:
            raise HTTPException(status_code=401, detail="Email and password do not match")

        user_id = res[0]
        user_agent = request.headers.get("user-agent", "")
        session_token = db.sessions.create_session(user_id, user_agent)
        response.set_cookie(key="session_token",
                            value=session_token,
                            httponly=True,
                            secure=False,  # Set to True for https
                            samesite="lax",
                            max_age=30*60) # In seconds

        return f"Logged in as: {login_request.username}"
    except HTTPException as e:
        return f"Error {e.status_code}: {e.detail}"

@app.post("/logout", response_class=HTMLResponse)
def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        db.sessions.delete_session(session_token)
        response.delete_cookie(key="session_token")
        return "Logged out successfully"
    return "Not logged in"
