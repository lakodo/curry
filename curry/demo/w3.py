import inspect
import time
import typing
from uuid import uuid4

from dask import delayed
from pydantic import BaseModel, ConfigDict


# BlockConnection and Block definition
class BlockConnection(BaseModel):
    source_block_id: str
    source_output_name: str = "output"
    self_input_name: str


class Block(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    id: str
    method_id: str
    parameters: dict[str, typing.Any] = {}
    connections: list[BlockConnection]
    # inputs: list[tuple[str, typing.Any]]
    # output: typing.Any


class NotRegisteredError(Exception):
    def __init__(self, method_name: str):
        super().__init__(f"Method '{method_name}' is not registered.")


class MethodManager:
    _registry: typing.ClassVar[dict[str, dict]] = {}

    @classmethod
    def register(
        cls, *, name: typing.Optional[str] = None, description: typing.Optional[str] = None
    ) -> typing.Callable:
        """Decorator to register methods as block templates."""

        def wrapper(func: typing.Callable) -> typing.Callable:
            method_name = name or func.__name__
            sig = inspect.signature(func)

            # Register method with automatic input/output discovery
            cls._registry[method_name] = {
                "name": method_name,
                "original_name": func.__name__,
                "description": description or func.__doc__ or "",
                "method": func,
                "inputs": {k: v.annotation for k, v in sig.parameters.items()},
                "output": sig.return_annotation,
            }

            def inner(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
                return func(*args, **kwargs)

            return inner

        return wrapper

    @classmethod
    def get_block_template(cls, *, method_name: str, block_modifications: typing.Optional[dict] = None) -> Block:
        """Retrieve block template for a registered method."""
        method_info = cls._registry.get(method_name)
        if not method_info:
            raise NotRegisteredError(method_name)

        # Automatically set up the block with inputs/outputs
        block_modifications = block_modifications or {}
        block_modifications["id"] = block_modifications.get("id", str(uuid4()))
        block_modifications["method_id"] = method_name
        block_modifications["parameters"] = block_modifications.get("parameters", {})
        block_modifications["connections"] = block_modifications.get("connections", [])
        # block_modifications["inputs"] = list(method_info["inputs"].items())
        # block_modifications["output"] = method_info["output"]

        print("Block modifications for block", block_modifications["id"], ":", block_modifications)

        # Automatically set up the block with inputs/outputs
        block = Block(**block_modifications)
        return block

    @classmethod
    def get_method_info(cls, method_name: str) -> dict:
        """Retrieve method information."""
        method_info = cls._registry.get(method_name)
        if not method_info:
            raise NotRegisteredError(method_name)
        return method_info


# Function to create a Dask workflow based on the blocks
def submit_workflow(blocks: list[Block]) -> dict:
    task_dict: dict = {}

    # Iterate through the blocks of the workflow
    for block in blocks:
        block_id = block.id
        block_method_id = block.method_id

        print("Processing block", block_id, "with method", block_method_id)

        # Retrieve the function corresponding to the block type
        block_method_info = MethodManager.get_method_info(block_method_id)
        block_method: typing.Callable = block_method_info["method"]

        # Merge block parameters with block connections
        block_parameters = {}
        if len(block.connections) > 0 or len(block.parameters) > 0:
            block_parameters = {
                **block.parameters,
                **{
                    connection.self_input_name: task_dict[connection.source_block_id]
                    for connection in block.connections
                },
            }
            print("Block parameters for block", block_id, ":", block_parameters)

        # Create the Dask task for the block
        task_dict[block_id] = delayed(block_method)(**block_parameters)

    # Retrieve the final block
    final_result = task_dict[list(task_dict.keys())[-1]]

    # Execute the Dask workflow
    result = final_result.compute()

    return {
        "status": "Workflow executed",
        "result": result,
        "final_result": final_result,
    }


# Defining the example methods


@MethodManager.register(name="constant")
def constant(value: int) -> int:
    """Returns a constant value."""
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
    time.sleep(5)
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
    time.sleep(3)
    return data0 + data1


# BLOCKS = [
#     MethodManager.get_block_template(
#         method_name="constant", block_modifications={"id": "constant-0", "parameters": {"value": 2}}
#     ),
#     MethodManager.get_block_template(
#         method_name="load_data", block_modifications={"id": "load-data-0", "parameters": {"path": "/data/sample.csv"}}
#     ),
#     MethodManager.get_block_template(
#         method_name="constant", block_modifications={"id": "constant-1", "parameters": {"value": 5}}
#     ),
#     MethodManager.get_block_template(
#         method_name="load_data", block_modifications={"id": "load-data-1", "parameters": {"path": "/data/sample.csv"}}
#     ),
#     MethodManager.get_block_template(
#         method_name="filter_data",
#         block_modifications={
#             "id": "filter_data-0",
#             "connections": [
#                 BlockConnection(source_block_id="constant-0", self_input_name="threshold"),
#                 BlockConnection(source_block_id="load-data-0", self_input_name="data"),
#             ],
#         },
#     ),
#     MethodManager.get_block_template(
#         method_name="filter_data",
#         block_modifications={
#             "id": "filter_data-1",
#             "connections": [
#                 BlockConnection(source_block_id="constant-1", self_input_name="threshold"),
#                 BlockConnection(source_block_id="load-data-1", self_input_name="data"),
#             ],
#         },
#     ),
#     MethodManager.get_block_template(
#         method_name="merge_data",
#         block_modifications={
#             "id": "3",
#             "connections": [
#                 BlockConnection(source_block_id="filter_data-0", self_input_name="data0"),
#                 BlockConnection(source_block_id="filter_data-1", self_input_name="data1"),
#             ],
#         },
#     ),
#     MethodManager.get_block_template(
#         method_name="sum_data",
#         block_modifications={
#             "id": "sum_data-0",
#             "connections": [BlockConnection(source_block_id="3", self_input_name="data")],
#         },
#     ),
# ]
# BLOCKS_AS_JSON = [block.model_dump_json() for block in BLOCKS]
# print("Blocks as JSON:", BLOCKS_AS_JSON)

BLOCKS_AS_JSON = [
    {"id": "constant-0", "method_id": "constant", "parameters": {"value": 2}, "connections": []},
    {"id": "load-data-0", "method_id": "load_data", "parameters": {"path": "/data/sample.csv"}, "connections": []},
    {"id": "constant-1", "method_id": "constant", "parameters": {"value": 5}, "connections": []},
    {"id": "load-data-1", "method_id": "load_data", "parameters": {"path": "/data/sample.csv"}, "connections": []},
    {
        "id": "filter_data-0",
        "method_id": "filter_data",
        "parameters": {},
        "connections": [
            {"source_block_id": "constant-0", "source_output_name": "output", "self_input_name": "threshold"},
            {"source_block_id": "load-data-0", "source_output_name": "output", "self_input_name": "data"},
        ],
    },
    {
        "id": "filter_data-1",
        "method_id": "filter_data",
        "parameters": {},
        "connections": [
            {"source_block_id": "constant-1", "source_output_name": "output", "self_input_name": "threshold"},
            {"source_block_id": "load-data-1", "source_output_name": "output", "self_input_name": "data"},
        ],
    },
    {
        "id": "3",
        "method_id": "merge_data",
        "parameters": {},
        "connections": [
            {"source_block_id": "filter_data-0", "source_output_name": "output", "self_input_name": "data0"},
            {"source_block_id": "filter_data-1", "source_output_name": "output", "self_input_name": "data1"},
        ],
    },
    {
        "id": "sum_data-0",
        "method_id": "sum_data",
        "parameters": {},
        "connections": [{"source_block_id": "3", "source_output_name": "output", "self_input_name": "data"}],
    },
]


BLOCKS = [Block.model_validate(block) for block in BLOCKS_AS_JSON]

# Executing the workflow
s = submit_workflow(BLOCKS)
s["final_result"].visualize()  # Visualize the Dask graph
print("Result:", s["result"])


