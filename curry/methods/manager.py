import inspect
import typing
from uuid import uuid4

from curry.models import Block


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
