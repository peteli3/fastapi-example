from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from ..internal.db import DB
from ..internal.common import templates, VERSION, GIT_COMMIT

router = APIRouter(prefix="/table")
db = DB()

@router.get("", response_class=HTMLResponse)
async def get_table_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="table.html",
        context={
            "data_source": db.items.list_items(),
            "categories": db.items.list_categories(),
            "version": VERSION,
            "git_commit": GIT_COMMIT,
        },
    )

class AddItemRequest(BaseModel):
    name: str
    category: str
    value: int
    description: str

@router.post("/add_item", response_class=HTMLResponse)
async def add_item(request: Request, item: AddItemRequest):
    db.items.add_item(item.name,
                      item.category,
                      item.value,
                      item.description)
    return templates.TemplateResponse(
        name="table.html",
        context={
            "request": request,
            "data_source": db.items.list_items(),
            "categories": db.items.list_categories(),
            "version": VERSION,
            "git_commit": GIT_COMMIT,
        }
    )

class EditItemRequest(BaseModel):
    name: str
    category: str
    value: int
    description: str

@router.post("/edit_item", response_class=HTMLResponse)
async def edit_item(request: Request, item: EditItemRequest):
    db.items.edit_item(item.name,
                       item.category,
                       item.value,
                       item.description)
    return templates.TemplateResponse(
        name="table.html",
        context={
            "request": request,
            "data_source": db.items.list_items(),
            "categories": db.items.list_categories(),
            "version": VERSION,
            "git_commit": GIT_COMMIT,
        }
    )

class DeleteItemRequest(BaseModel):
    name: str

@router.post("/delete_item", response_class=HTMLResponse)
async def delete_item(request: Request, item: DeleteItemRequest):
    db.items.delete_item(item.name)
    return templates.TemplateResponse(
        name="table.html",
        context={
            "request": request,
            "data_source": db.items.list_items(),
            "categories": db.items.list_categories(),
            "version": VERSION,
            "git_commit": GIT_COMMIT,
        }
    )
