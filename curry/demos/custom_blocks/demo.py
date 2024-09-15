import typing

from curry.methods import MethodManager
from curry.models import Block, BlockConnection, BlockProducer
from curry.workflow import submit_workflow


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
    def my_custom_html_renderer(self) -> str:
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


# Executing the workflow
s = submit_workflow(BLOCKS)
s["final_result"].visualize()  # Visualize the Dask graph
print("Result:", s["result"])
