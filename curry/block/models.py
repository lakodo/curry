import inspect
import typing
import uuid

from pydantic import BaseModel, ConfigDict, Field

from curry.utils.typing import AnyCallable, AnyDict

BlockProducteurFunction = typing.Callable[["Block"], typing.Any]


class BlockProducer(BaseModel):
    format_name: str
    func: BlockProducteurFunction
    description: typing.Optional[str] = None
    tags: list[str] = []
    title: typing.Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class BlockConnection(BaseModel):
    source_block_id: str
    source_output_name: str = "output"
    self_input_name: str


def block_as_html_default(block: "Block") -> str:
    return "<span>block html rendering not defined</span>"


def block_method_source_code_default(block: "Block"):
    from curry.methods import MethodManager

    return inspect.getsource(MethodManager.get_method_info(block.method_id).method)


class Block(BaseModel):
    """
    A block is a unit of computation in a workflow. It can be connected to other blocks and produce outputs in different formats
    using producers.

    Attributes:
        id (str): The unique identifier of the block.
        name (str): The name of the block.
        description (str): The description of the block.
        method_id (str): The method ID associated with the block.
        parameters (AnyDict): The parameters of the block.
        connections (list[BlockConnection]): The connections of the block.
        producers (dict[str, BlockProducer]): The producers of the block
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    method_id: str

    name: typing.Optional[str] = None
    description: typing.Optional[str] = None
    parameters: AnyDict = {}
    connections: list[BlockConnection] = []

    producers: dict[str, BlockProducer] = {
        "html": BlockProducer(format_name="html", func=block_as_html_default),
        "python_source": BlockProducer(
            format_name="python_source",
            description="Get the source code of the producer python function",
            func=block_method_source_code_default,
        ),
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

    def produce(self, format_name: str) -> typing.Any:
        return self.producers[format_name].func(self)

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
    def from_func(cls, func: AnyCallable, **kwargs: typing.Any) -> "Block":
        """
        Create a Block instance from a given function.

        Args:
            cls (type): The class of the Block instance.
            func (AnyCallable): The function to create the Block from.
            **kwargs (typing.Any): Additional keyword arguments for the Block instance.

        Returns:
            Block: The created Block instance.

        """

        block_name = kwargs.get("name") or func.__name__
        kwargs["name"] = block_name

        block_description = kwargs.get("description") or func.__doc__ or ""
        kwargs["description"] = block_description

        block_method_id = kwargs.get("method_id") or func.__name__
        kwargs["method_id"] = block_method_id

        block = cls(**kwargs)

        return block
