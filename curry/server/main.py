import datetime
import math
import os
import threading
import time
import typing

from dask.delayed import Delayed, delayed
from dask.distributed import Client
from distributed import Future
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from curry.methods import MethodManager
from curry.models import Block, BlockConnection, BlockProducer
from curry.utils.typing.typing import AnyDict
from curry.workflow import submit_workflow

from .utils.time import format_datetime

app = FastAPI()


MAIN_FILE_PATH = os.path.dirname(__file__)

app.mount(
    os.path.join(MAIN_FILE_PATH, "static"), StaticFiles(directory=os.path.join(MAIN_FILE_PATH, "static")), name="static"
)


##########################################


@MethodManager.register(name="constant")
def constant(value: int) -> int:
    """Returns a constant value."""
    time.sleep(5)
    return value


@MethodManager.register(name="load_data")
def load_data(path: str) -> list[int]:
    """Simulates loading data from a file."""
    print(f"Loading data from {path}")
    time.sleep(5)
    return list(range(10))


@MethodManager.register(name="filter_data")
def filter_data(data: list[int], threshold: int) -> list[int]:
    """Filters data based on a threshold."""
    print(f"Filtering data with threshold {threshold}")
    time.sleep(2)
    return [x for x in data if x > threshold]


@MethodManager.register(name="sum_data")
def sum_data(data: list[int]) -> int:
    """Sums the data."""
    print("Summing data")
    time.sleep(3)
    return sum(data)


@MethodManager.register(name="merge_data")
def merge_data(data0: list[int], data1: list[int]) -> list[int]:
    """Merges two data lists."""
    print("Merging data")
    time.sleep(3)
    return data0 + data1


class MyConstantBlock(Block):
    def my_custom_html_renderer(self, block: Block) -> str:
        return f"<h2>CONSTANT Block ID: {self.id}</h2>"

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(
            #
            *args,
            method_id="constant",
            name="constant",
            description="A block that returns a constant value.",
            **kwargs,
        )

        self.register_producer(
            BlockProducer(
                format_name="html",
                func=self.my_custom_html_renderer,
                description="Custom HTML renderer for the CONSTANT block",
            )
        )


BLOCK_FLOW_EXAMPLE: list[Block] = [
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
templates.env.auto_reload = True  # type: ignore  # noqa: PGH003
templates.env.filters["format_datetime"] = format_datetime  # type: ignore  # noqa: PGH003


@app.get("/", response_class=HTMLResponse)
async def welcome(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="pages/landing.html", context={})


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="pages/home.html", context={})


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
    user: AnyDict = {"name": username, "email": "no email yet", "joined_date": datetime.datetime.now()}
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("layouts/user_base.html", {"request": request, "user": user})


@app.get("/workflows/{workflow_id}", response_class=HTMLResponse)
async def display_workflow(request: Request, workflow_id: str) -> HTMLResponse:
    s = submit_workflow(BLOCK_FLOW_EXAMPLE, execute=False, render=True, render_format="svg")
    svg = s["render_result"]

    return templates.TemplateResponse(
        "pages/workflow.html",
        {
            #
            "request": request,
            "workflow_id": workflow_id,
            "workflow_svg": svg.data,
            "blocks": BLOCK_FLOW_EXAMPLE,
        },
    )


@app.get("/builder/{workflow_id}", response_class=HTMLResponse)
async def display_workflow_builder(request: Request, workflow_id: str) -> HTMLResponse:
    methods = MethodManager.get_registry()

    # a = list(methods.values())
    # m=a[0]
    # m.method.__code__

    return templates.TemplateResponse(
        "pages/builder.html",
        {
            #
            "request": request,
            "methods": methods,
            "workflow_id": workflow_id,
        },
    )


# @app.get("/dask", response_class=HTMLResponse)
# async def display_workflow(request: Request, workflow_id: str) -> HTMLResponse:


# WORKFLOW_FUTURES = {}
# WORKFLOW_RESULTS = {}


workflow_state_lock = threading.Lock()
WORKFLOW_STATE: dict[str, dict[str, Delayed]] = {}
WORKFLOW_FUTURE: dict[str, dict[str, Future]] = {}


@app.get("/workflows/{workflow_id}/delay")
async def delay_workflow(request: Request, workflow_id: str) -> HTMLResponse:
    task_delayed_dict: dict[str, Delayed] = {}

    # Iterate through the blocks of the workflow
    for block in BLOCK_FLOW_EXAMPLE:
        block_id = block.id
        block_method_id = block.method_id or "no_method"

        # Retrieve the function corresponding to the block type
        block_method_info = MethodManager.get_method_info(block_method_id)
        block_method = block_method_info.method

        # Merge block parameters with block connections
        block_parameters = {}
        if len(block.connections) > 0 or len(block.parameters) > 0:
            block_parameters: AnyDict = {
                **block.parameters,
                **{
                    connection.self_input_name: task_delayed_dict[connection.source_block_id]
                    for connection in block.connections
                },
            }

        # Create the Dask task for the block and submit it
        with workflow_state_lock:
            task_delayed_dict[block_id] = delayed(block_method)(**block_parameters)
            print(block_method.__name__, block_parameters, task_delayed_dict[block_id])
            default_local_client.submit(task_delayed_dict[block_id])
            # task_future_dict[block_id] = default_local_client.submit(task_delayed_dict[block_id])  # type: ignore  # noqa: PGH003

    with workflow_state_lock:
        WORKFLOW_STATE[workflow_id] = task_delayed_dict
        print("\ttask_delayed_dict:\n", WORKFLOW_STATE[workflow_id])

    return 0


@app.get("/workflows/{workflow_id}/submit")
async def submit_workflow(request: Request, workflow_id: str) -> HTMLResponse:
    task_future_dict: dict[str, Future] = {}

    with workflow_state_lock:
        last_task_delayed: Delayed = WORKFLOW_STATE[workflow_id][list(WORKFLOW_STATE[workflow_id].keys())[-1]]

        last_task_future = default_local_client.submit(last_task_delayed)
        WORKFLOW_FUTURE[workflow_id] = {"last": last_task_future}
        print("\ttask_future_dict:\n", WORKFLOW_FUTURE[workflow_id])

    return 1


@app.get("/workflows/{workflow_id}/result")
async def print_result_workflow(request: Request, workflow_id: str) -> HTMLResponse:
    if workflow_id in WORKFLOW_STATE and workflow_id in WORKFLOW_FUTURE:
        with workflow_state_lock:
            print("\ttask_delayed_dict:\n", WORKFLOW_STATE[workflow_id])
            print("\ttask_future_dict:\n", WORKFLOW_FUTURE[workflow_id])
            for k, v in WORKFLOW_FUTURE[workflow_id].items():
                print(k, v)

    return 2


@app.get("/test-dask/{key}")
async def test_dask(request: Request, key: int):
    from dask import bag as db

    client = Client(address="tcp://127.0.0.1:18000")

    def multiply_by_two(x: int) -> int:
        time.sleep(1)
        print(f"multiply_by_two({x})")
        return 2 * x

    N = key

    x = db.from_sequence(range(N))

    mults = x.map(multiply_by_two)

    summed = mults.sum()

    t0 = time.time()
    summed = client.compute(summed)

    # time.sleep(1.0)

    while not summed.done():
        # print("loop", key)
        time.sleep(0.1)
    t1 = time.time()

    delta = math.floor(t1 - t0)
    summed_result = summed.result()
    print(f"[{delta}s] `sum(range({N}))` on cluster: {summed_result}\t(should be {N * (N - 1)})")
    client.close()

    return {"2": delta, "key": key, "summed": summed_result}
