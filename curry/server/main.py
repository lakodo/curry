import datetime
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .utils.time import format_datetime

app = FastAPI()


MAIN_FILE_PATH = os.path.dirname(__file__)

app.mount(
    os.path.join(MAIN_FILE_PATH, "static"), StaticFiles(directory=os.path.join(MAIN_FILE_PATH, "static")), name="static"
)


# Add the custom filter to Jinja2 environment

templates = Jinja2Templates(directory=os.path.join(MAIN_FILE_PATH, "templates"))
templates.env.auto_reload = True
templates.env.filters["format_datetime"] = format_datetime



@app.get("/", response_class=HTMLResponse)
async def welcome(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="index.html", context={})


@app.get("/items/{item_id}", response_class=HTMLResponse)
async def read_item(request: Request, item_id: str) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="item.html", context={"item": {"id": item_id}})

@app.get("/users/{username}", response_class=HTMLResponse)
async def user_profile(request: Request, username: str):
    user = {"name": username, "email": "no email yet", "joined_date": datetime.datetime.now()}
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("layouts/user_base.html", {"request": request, "user": user})
