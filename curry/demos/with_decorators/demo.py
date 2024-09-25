import time
import typing

from curry.block import Block
from curry.flow import submit_workflow
from curry.methods import MethodManager

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

BLOCKS_AS_JSON: list[dict[str, typing.Any]] = [
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
s = submit_workflow(BLOCKS, render=True)
print("Result:", s["result"])
