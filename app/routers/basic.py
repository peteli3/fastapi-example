from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..internal.common import templates, VERSION, GIT_COMMIT

router = APIRouter(prefix="/basic")

class Counter:
    def __init__(self):
        self.value = 0

    def get_value(self):
        return self.value

    def set_value(self, new_value):
        self.value = new_value

counter = Counter()

@router.get("", response_class=HTMLResponse)
def get_basic_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="basic.html",
        context={
            "request": request,
            "counter": counter.get_value(),
            "version": VERSION,
            "git_commit": GIT_COMMIT,
        },
    )

@router.post("/increment")
def increment_counter():
    counter.set_value(counter.get_value() + 1)
    return counter.get_value()
