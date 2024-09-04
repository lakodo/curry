import typing

from dask import delayed

from curry.methods import MethodManager
from curry.models import Block


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
