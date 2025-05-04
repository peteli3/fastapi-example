from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import re
import uuid

from pydantic import BaseModel

from .db import DB

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

db = DB()
sessions = {}

@app.get("/", response_class=HTMLResponse)
def get_homepage(request: Request):
    session_token = request.cookies.get("session_token")
    username = sessions.get(session_token, None)
    logged_in_as = f"Logged in as: {username}" if username else ""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "logged_in_as": logged_in_as,
        },
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
        res = db.authenticate_user(login_request.username, login_request.password)
        if not res:
            raise HTTPException(status_code=401, detail="Email and password do not match")

        session_token = str(uuid.uuid4())
        sessions[session_token] = login_request.username
        response.set_cookie(key="session_token",
                            value=session_token,
                            httponly=True,
                            secure=False,  # Set to True for production
                            samesite="lax",
                            max_age=3600)

        return f"Logged in as: {login_request.username}"
    except HTTPException as e:
        return f"Error {e.status_code}: {e.detail}"

@app.post("/logout", response_class=HTMLResponse)
def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token and session_token in sessions:
        response.delete_cookie(key="session_token")

class Counter:
    def __init__(self):
        self.value = 0

    def get_value(self):
        return self.value

    def set_value(self, new_value):
        self.value = new_value

counter = Counter()

@app.post("/increment")
def increment_counter():
    counter.set_value(counter.get_value() + 1)
    return counter.get_value()

@app.get("/basic", response_class=HTMLResponse)
def get_basic(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="basic.html",
        context={
            "request": request,
            "counter": counter.get_value(),
        },
    )

@app.get("/table", response_class=HTMLResponse)
def read_item(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="table.html",
        context={
            "data_source": db.list_items(),
            "categories": db.list_categories(),
        },
    )

class AddItemRequest(BaseModel):
    name: str
    category: str
    value: int
    description: str

@app.post("/add_item", response_class=HTMLResponse)
def add_item(request: Request, item: AddItemRequest):
    db.add_item(item.name,
                item.category,
                item.value,
                item.description)
    return templates.TemplateResponse(
        name="table.html",
        context={
            "request": request,
            "data_source": db.list_items(),
            "categories": db.list_categories(),
        }
    )

class EditItemRequest(BaseModel):
    name: str
    category: str
    value: int
    description: str

@app.post("/edit_item", response_class=HTMLResponse)
def edit_item(request: Request, edit_request: EditItemRequest):
    db.edit_item(edit_request.name,
                 edit_request.category,
                 edit_request.value,
                 edit_request.description)
    return templates.TemplateResponse(
        name="table.html",
        context={
            "request": request,
            "data_source": db.list_items(),
            "categories": db.list_categories(),
        }
    )

class DeleteItemRequest(BaseModel):
    name: str

@app.post("/delete_item", response_class=HTMLResponse)
def delete_item(request: Request, delete_request: DeleteItemRequest):
    db.delete_item(delete_request.name)
    return templates.TemplateResponse(
        name="table.html",
        context={
            "request": request,
            "data_source": db.list_items(),
            "categories": db.list_categories(),
        }
    )
