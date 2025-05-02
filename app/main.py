from bcrypt import hashpw, gensalt, checkpw
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

counter = 0
users = { "myuser@gmail.com": hashpw(b"mypassword", gensalt()) }
sessions = {}

def get_counter():
    return counter

def set_counter(newval):
    global counter
    counter = newval
    return counter

@app.get("/items/{id}", response_class=HTMLResponse)
def read_item(request: Request, id: int):
    session_token = request.cookies.get("session_token")
    username = sessions.get(session_token, None)
    logged_in_as = f"Logged in as: {username}" if username else ""
    return templates.TemplateResponse(
        request=request,
        name="item.html",
        context={
            "id": id,
            "counter": get_counter(),
            "data_source": db.list_items(),
            "categories": db.list_categories(),
            "logged_in_as": logged_in_as,
        },
    )

@app.post("/increment")
def increment_counter():
    return set_counter(get_counter() + 1)

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
        if login_request.username not in users:
            raise HTTPException(status_code=404, detail="User not found")
        if not checkpw(login_request.password, users[login_request.username]):
            raise HTTPException(status_code=401, detail="Incorrect password")

        session_token = str(uuid.uuid4())
        sessions[session_token] = login_request.username
        response.set_cookie(key="session_token",
                            value=session_token,
                            httponly=True,
                            secure=True,
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

class AddItemRequest(BaseModel):
    name: str
    category: str
    value: int
    description: str
    id: str

@app.post("/add_item", response_class=HTMLResponse)
def add_item(request: Request, item: AddItemRequest):
    db.add_item(item.name,
                item.category,
                item.value,
                item.description)
    return templates.TemplateResponse(
        name="item.html",
        context={
            "request": request,
            "data_source": db.list_items(),
            "id": int(item.id),
            "counter": get_counter(),
            "categories": db.list_categories(),
        }
    )

class EditItemRequest(BaseModel):
    name: str
    category: str
    value: int
    description: str
    id: str

@app.post("/edit_item", response_class=HTMLResponse)
def edit_item(request: Request, edit_request: EditItemRequest):
    db.edit_item(edit_request.name,
                 edit_request.category,
                 edit_request.value,
                 edit_request.description)
    return templates.TemplateResponse(
        name="item.html",
        context={
            "request": request,
            "data_source": db.list_items(),
            "id": int(edit_request.id),
            "counter": get_counter(),
            "categories": db.list_categories(),
        }
    )

class DeleteItemRequest(BaseModel):
    name: str

@app.post("/delete_item", response_class=HTMLResponse)
def delete_item(request: Request, delete_request: DeleteItemRequest):
    db.delete_item(delete_request.name)
    return templates.TemplateResponse(
        name="item.html",
        context={
            "request": request,
            "data_source": db.list_items(),
            "id": int(request.query_params.get("id", "0")),
            "counter": get_counter(),
            "categories": db.list_categories(),
        }
    )
