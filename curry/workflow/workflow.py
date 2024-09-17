import typing

from dask import delayed
from dask.delayed import Delayed
from dask.distributed import Client

from curry.methods import MethodManager
from curry.models import Block

client = Client()  # Ensure this is initialized at the top level


# Function to create a Dask workflow based on the blocks
def submit_workflow(
    blocks: list[Block],
    execute: bool = True,
    render: bool = False,
    render_format: typing.Optional[str] = "png",
    render_filename: typing.Optional[str] = None,
) -> dict:
    task_dict: dict[str, Delayed] = {}

    # Iterate through the blocks of the workflow
    for block in blocks:
        block_id = block.id
        block_method_id = block.method_id or "no_method"

        print("\t- Processing block", block_id, "with method", block_method_id)

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
    final_task: Delayed = task_dict[list(task_dict.keys())[-1]]

    # Execute the Dask workflow
    result_future = None
    if execute:
        # result = final_task.compute()
        result_future = client.compute(final_task)

    render_result = None
    if render:
        render_result = final_task.visualize(format=render_format, filename=render_filename)

    return {
        "result_future": result_future,
        # "executed": execute,
        # "result": result if execute else None,
        # "rendered": render,
        # "final_result": final_task,
        "render_result": render_result,
    }
