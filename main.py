from bcrypt import hashpw, gensalt, checkpw
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import re
import uuid

from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

counter = 0
data_source = []
categories = [ "A", "B", "C", "D", "X" ]
users = { "myuser@gmail.com": hashpw(b"mypassword", gensalt()) }

# In-memory session storage (replace with a database in production)
sessions = {}

@app.get("/items/{id}", response_class=HTMLResponse)
def read_item(request: Request, id: int):
    global counter, data_source, categories
    session_token = request.cookies.get("session_token")
    username = sessions.get(session_token, None)
    logged_in_as = f"Logged in as: {username}" if username else ""
    return templates.TemplateResponse(
        request=request,
        name="item.html",
        context={
            "id": id,
            "counter": counter,
            "data_source": data_source,
            "categories": categories,
            "logged_in_as": logged_in_as,
        },
    )

@app.post("/increment")
def increment_counter():
    global counter
    counter += 1
    return counter

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

        # Generate a session token
        session_token = str(uuid.uuid4())
        sessions[session_token] = login_request.username

        # Set the session token in a secure cookie
        response.set_cookie(key="session_token",
                            value=session_token,
                            httponly=True,
                            secure=True,
                            samesite="lax",
                            max_age=3600)  # 1 hour expiration

        return f"Logged in as: {login_request.username}"
    except HTTPException as e:
        return f"Error {e.status_code}: {e.detail}"

@app.post("/logout", response_class=HTMLResponse)
def logout(request: Request, response: Response):
    # Return a message only if a user was actually logged out
    session_token = request.cookies.get("session_token")
    if session_token and session_token in sessions:
        username = sessions.pop(session_token, None)
        response.delete_cookie(key="session_token")
        return "Logged out"

    # Return empty string if no valid session was found
    return ""

@app.post("/signup", response_class=HTMLResponse)
def signup(request: Request):
    # TODO: Implement signup
    return None

class AddItemRequest(BaseModel):
    name: str
    category: str
    value: int
    description: str
    id: str
    counter: int

@app.post("/add_item", response_class=HTMLResponse)
def add_item(request: Request, item: AddItemRequest):
    global counter, data_source, categories
    data_source.append([item.name,
                        item.category,
                        item.value,
                        item.description])
    return templates.TemplateResponse(
        name="item.html",
        context={
            "request": request,
            "data_source": data_source,
            "id": int(item.id),
            "counter": counter,
            "categories": categories,
        }
    )

class EditItemRequest(BaseModel):
    index: int
    name: str
    category: str
    value: int
    description: str
    id: str
    counter: int

@app.post("/edit_item", response_class=HTMLResponse)
def edit_item(request: Request, edit_request: EditItemRequest):
    global data_source
    index = edit_request.index
    if 0 <= index < len(data_source):
        data_source[index] = [edit_request.name,
                              edit_request.category,
                              edit_request.value,
                              edit_request.description]
    return templates.TemplateResponse(
        name="item.html",
        context={
            "request": request,
            "data_source": data_source,
            "id": int(edit_request.id),
            "counter": counter,
            "categories": categories,
        }
    )

class DeleteItemRequest(BaseModel):
    index: int

@app.post("/delete_item", response_class=HTMLResponse)
def delete_item(request: Request, delete_request: DeleteItemRequest):
    global data_source
    index = delete_request.index
    if 0 <= index < len(data_source):
        data_source.pop(index)  # Remove the item at the specified index
    return templates.TemplateResponse(
        name="item.html",
        context={
            "request": request,
            "data_source": data_source,
            "id": int(request.query_params.get("id", "0")),
            "counter": counter,
            "categories": categories,
        }
    )
