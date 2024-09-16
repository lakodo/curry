import typing
import uuid

from pydantic import BaseModel, ConfigDict, Field

from .errors import ProducerAlreadyRegistered
import json


class BlockProducer(BaseModel):
    format_name: str
    func: typing.Callable
    description: typing.Optional[str] = None
    tags: list[str] = []
    title: typing.Optional[str] = None


class BlockConnection(BaseModel):
    source_block_id: str
    source_output_name: str = "output"
    self_input_name: str


class Block(BaseModel):
    """
    A block is a unit of computation in a workflow. It can be connected to other blocks and produce outputs in different formats
    using producers.

    Attributes:
        id (str): The unique identifier of the block.
        name (str): The name of the block.
        description (str): The description of the block.
        method_id (str): The method ID associated with the block.
        parameters (dict[str, typing.Any]): The parameters of the block.
        connections (list[BlockConnection]): The connections of the block.
        producers (dict[str, BlockProducer]): The producers of the block
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: typing.Optional[str] = None
    description: typing.Optional[str] = None
    method_id: typing.Optional[str] = None
    parameters: dict[str, typing.Any] = {}
    connections: list[BlockConnection] = []

    producers: dict[str, BlockProducer] = {
        "html": BlockProducer(
            # format_name="html", func=lambda *args, **kwargs: json.dumps({"args": args, "kwargs": kwargs})
            format_name="html",
            func=lambda block, *args, **kwargs: block.id,
        )
    }

    def has_producer(self, format_name: str) -> bool:
        """
        Check if the block has a producer for the given format name.

        Parameters:
            format_name (str): The name of the format to check.

        Returns:
            bool: True if the block has a producer for the given format name, False otherwise.
        """
        return format_name in self.producers

    def produce(self, format_name: str, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        return self.producers[format_name].func(self, *args, **kwargs)

    def available_producers(self) -> list[str]:
        """
        Returns a list of available producers.

        Returns:
            list[str]: A list of available producers.
        """
        return list(self.producers.keys())

    def register_producer(self, producer: BlockProducer) -> None:
        # if producer.format_name in self.producers:
        #     raise ProducerAlreadyRegistered(producer.format_name)
        self.producers[producer.format_name] = producer

    @classmethod
    def from_func(cls, func: typing.Callable, **kwargs: typing.Any) -> "Block":
        """
        Create a Block instance from a given function.

        Args:
            cls (type): The class of the Block instance.
            func (typing.Callable): The function to create the Block from.
            **kwargs (typing.Any): Additional keyword arguments for the Block instance.

        Returns:
            Block: The created Block instance.

        """
        block = cls(**kwargs)
        block.name = kwargs.get("name") or func.__name__
        block.description = kwargs.get("description") or func.__doc__ or ""
        block.method_id = kwargs.get("method_id") or func.__name__
        return block
