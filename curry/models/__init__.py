import typing

from pydantic import BaseModel, ConfigDict


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
