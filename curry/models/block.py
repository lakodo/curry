import typing
import uuid
from functools import wraps

from pydantic import BaseModel, ConfigDict, Field


class BlockConnection(BaseModel):
    source_block_id: str
    source_output_name: str = "output"
    self_input_name: str


class Block(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    method_id: typing.Optional[str] = None
    parameters: dict[str, typing.Any] = {}
    connections: list[BlockConnection] = []

    # This will store the registered producer methods
    _producers: dict[str, typing.Callable] = {}

    # Decorator for registering a format producer
    @classmethod
    def register_producer(cls, format_name: str):
        def decorator(func: typing.Callable):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                return func(self, *args, **kwargs)

            # Register the method in the _producers dict
            cls._producers[format_name] = func.__name__
            return wrapper

        return decorator

    # Check if a particular format producer is implemented
    def has_producer(self, format_name: str) -> bool:
        return format_name in self._producers

    # Get a list of implemented formats
    def available_producers(self) -> list[str]:
        return list(self._producers.keys())

    # HTML producer method
    @register_producer("html")
    def to_html(self) -> str:
        return f"<h2>Block ID: {self.id}</h2>"
