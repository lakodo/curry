import typing

from curry.demos.existing_functions.fake_methods import constant, filter_data, load_data, merge_data, sum_data
from curry.methods import MethodManager
from curry.models import Block
from curry.workflow import submit_workflow

# Enlisting the example methods
MethodManager.register(name="constant")(constant)
MethodManager.register(name="load_data")(load_data)
MethodManager.register(name="filter_data")(filter_data)
MethodManager.register(name="sum_data")(sum_data)
MethodManager.register(name="merge_data")(merge_data)


BLOCKS_AS_JSON:list[dict[str,typing.Any]] = [
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
