import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()


MAIN_FILE_PATH = os.path.dirname(__file__)

app.mount(
    os.path.join(MAIN_FILE_PATH, "static"), StaticFiles(directory=os.path.join(MAIN_FILE_PATH, "static")), name="static"
)

templates = Jinja2Templates(directory=os.path.join(MAIN_FILE_PATH, "templates"))


@app.get("/items/{item_id}", response_class=HTMLResponse)
async def read_item(request: Request, item_id: str) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="item.html", context={"id": item_id})
