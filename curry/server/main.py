import asyncio
import datetime
import os
import typing

from dask.distributed import Client
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import threading


from curry.methods import MethodManager
from curry.models import Block, BlockConnection, BlockProducer
from curry.workflow import submit_workflow

from .utils.time import format_datetime

client = Client()  # Starts a local cluster
futures_lock = threading.Lock()
results_lock = threading.Lock()


app = FastAPI()


MAIN_FILE_PATH = os.path.dirname(__file__)

app.mount(
    os.path.join(MAIN_FILE_PATH, "static"), StaticFiles(directory=os.path.join(MAIN_FILE_PATH, "static")), name="static"
)


##########################################


@MethodManager.register(name="constant")
def constant(value: int) -> int:
    """Returns a constant value."""
    return value


@MethodManager.register(name="load_data")
def load_data(path: str) -> list[int]:
    """Simulates loading data from a file."""
    print(f"Loading data from {path}")
    return list(range(10))


@MethodManager.register(name="filter_data")
def filter_data(data: list[int], threshold: int) -> list[int]:
    """Filters data based on a threshold."""
    print(f"Filtering data with threshold {threshold}")
    return [x for x in data if x > threshold]


@MethodManager.register(name="sum_data")
def sum_data(data: list[int]) -> int:
    """Sums the data."""
    print("Summing data")
    return sum(data)


@MethodManager.register(name="merge_data")
def merge_data(data0: list[int], data1: list[int]) -> list[int]:
    """Merges two data lists."""
    print("Merging data")
    return data0 + data1


class MyConstantBlock(Block):
    def my_custom_html_renderer(self, block: Block) -> str:
        return f"<h2>CONSTANT Block ID: {self.id}</h2>"

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)

        self.name = "constant"
        self.description = kwargs.get("description") or "A block that returns a constant value."
        self.method_id = "constant"

        self.register_producer(
            BlockProducer(
                format_name="html",
                func=self.my_custom_html_renderer,
                description="Custom HTML renderer for the CONSTANT block",
            )
        )


BLOCKS = [
    # MethodManager.get_block_template(
    #     method_name="constant", block_modifications={"id": "constant-0", "parameters": {"value": 2}}
    # ),
    MyConstantBlock(id="constant-0", parameters={"value": 2}),
    # MethodManager.get_block_template(
    #     method_name="load_data", block_modifications={"id": "load-data-0", "parameters": {"path": "/data/sample.csv"}}
    # ),
    Block.from_func(load_data, id="load-data-0", parameters={"path": "/data/sample.csv"}),
    MethodManager.get_block_template(
        method_name="constant", block_modifications={"id": "constant-1", "parameters": {"value": 5}}
    ),
    MethodManager.get_block_template(
        method_name="load_data", block_modifications={"id": "load-data-1", "parameters": {"path": "/data/sample.csv"}}
    ),
    MethodManager.get_block_template(
        method_name="filter_data",
        block_modifications={
            "id": "filter_data-0",
            "connections": [
                BlockConnection(source_block_id="constant-0", self_input_name="threshold"),
                BlockConnection(source_block_id="load-data-0", self_input_name="data"),
            ],
        },
    ),
    MethodManager.get_block_template(
        method_name="filter_data",
        block_modifications={
            "id": "filter_data-1",
            "connections": [
                BlockConnection(source_block_id="constant-1", self_input_name="threshold"),
                BlockConnection(source_block_id="load-data-1", self_input_name="data"),
            ],
        },
    ),
    MethodManager.get_block_template(
        method_name="merge_data",
        block_modifications={
            "id": "3",
            "connections": [
                BlockConnection(source_block_id="filter_data-0", self_input_name="data0"),
                BlockConnection(source_block_id="filter_data-1", self_input_name="data1"),
            ],
        },
    ),
    MethodManager.get_block_template(
        method_name="sum_data",
        block_modifications={
            "id": "sum_data-0",
            "connections": [BlockConnection(source_block_id="3", self_input_name="data")],
        },
    ),
]


##########################################


templates = Jinja2Templates(directory=os.path.join(MAIN_FILE_PATH, "templates"))
templates.env.auto_reload = True
templates.env.filters["format_datetime"] = format_datetime


@app.get("/", response_class=HTMLResponse)
async def welcome(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="pages/landing.html", context={})


@app.get("/items/{item_id}", response_class=HTMLResponse)
async def read_item(request: Request, item_id: str) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="pages/item.html", context={"item": {"id": item_id}})


@app.get("/teams", response_class=HTMLResponse)
async def teams(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("pages/teams.html", {"request": request})


@app.get("/projects", response_class=HTMLResponse)
async def projects(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("pages/projects.html", {"request": request})


@app.get("/users/{username}", response_class=HTMLResponse)
async def user_profile(request: Request, username: str) -> HTMLResponse:
    user = {"name": username, "email": "no email yet", "joined_date": datetime.datetime.now()}
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("layouts/user_base.html", {"request": request, "user": user})


@app.get("/workflows/{workflow_id}", response_class=HTMLResponse)
async def display_workflow(request: Request, workflow_id: str) -> HTMLResponse:
    s = submit_workflow(BLOCKS, execute=False, render=True, render_format="svg")
    svg = s["render_result"]

    return templates.TemplateResponse(
        "pages/workflow.html",
        {
            #
            "request": request,
            "workflow_id": workflow_id,
            "workflow_svg": svg.data,
            "blocks": BLOCKS,
        },
    )


WORKFLOW_FUTURES = {}
WORKFLOW_RESULTS = {}


@app.get("/workflows/{workflow_id}/compute", response_class=HTMLResponse)
async def compute_workflow(request: Request, workflow_id: str) -> HTMLResponse:
    s = submit_workflow(BLOCKS)
    future = s["result_future"]
    with futures_lock:
        WORKFLOW_FUTURES[workflow_id] = future
    workflow_url = app.url_path_for("display_workflow", workflow_id=workflow_id)
    return RedirectResponse(url=workflow_url)


@app.websocket("/workflows/{workflow_id}/progress")
async def websocket_progress(websocket: WebSocket, workflow_id: str):
    await websocket.accept()
    try:
        with futures_lock:
            future = WORKFLOW_FUTURES.get(workflow_id)
        if not future:
            await websocket.send_text("Error: No such workflow")
            await websocket.close()
            return

        # Get all the futures associated with the task graph
        futures = client.futures_of(future)
        total_tasks = len(futures)

        while True:
            # Count the number of completed tasks
            completed_tasks = sum(f.status == "finished" for f in futures)
            progress = int((completed_tasks / total_tasks) * 100)
            await websocket.send_text(str(progress))

            if completed_tasks >= total_tasks:
                break

            await asyncio.sleep(1)  # Adjust the sleep time as needed

        # Ensure the progress reaches 100% at the end
        await websocket.send_text("100")

        # Retrieve and store the result
        result = future.result()
        with results_lock:
            WORKFLOW_RESULTS[workflow_id] = result

    except WebSocketDisconnect:
        print(f"Client disconnected from workflow {workflow_id} progress WebSocket")
    except Exception as e:
        print(f"Error in progress WebSocket for workflow {workflow_id}: {e}")
        await websocket.close()
