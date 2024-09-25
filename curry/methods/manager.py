import inspect
import typing
from functools import wraps
from inspect import Signature
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, validate_call
from pydantic.types import UUID4

from curry.block import Block
from curry.utils.string.uuid import deterministic_uuid_v4
from curry.utils.typing import AnyCallable
from curry.utils.typing.typing import AnyDict


class NotRegisteredError(Exception):
    def __init__(self, method_name: str):
        super().__init__(f"Method '{method_name}' is not registered.")


class MethodInfo(BaseModel):
    id: UUID4 = Field(
        description="Each method should have unique id provided (default is deterministically generated from name and version)"
    )
    version: str = Field(
        description="A same function can be enlisted several times, this property should follow semver versionning."
    )
    tags: list[str] = []
    name: str = Field(description="A human readable name of the function (default to `original_name`)")
    original_name: str = Field(description="The true python name of thefunction (should not be set manually)")
    description: typing.Optional[str] = Field(description="A description of the method")
    method: AnyCallable
    method_code: str = ""
    # inputs: dict[str, Parameter] = Field({}, description="List of the input parameters of the method")
    # output: Parameter = Field(description="Output parameter of the method")
    signature: Signature = Field(description="Function signature")
    model_config = ConfigDict(arbitrary_types_allowed=True)


class MethodManager:
    _registry: typing.ClassVar[dict[str, MethodInfo]] = {}

    @classmethod
    def register(
        #
        cls,
        *,
        name: typing.Optional[str] = None,
        description: typing.Optional[str] = None,
        version: typing.Optional[str] = None,
    ) -> AnyCallable:
        """Decorator to register methods as block templates."""

        def wrapper(func: AnyCallable) -> AnyCallable:
            method_name = name or func.__name__
            method_version = version or "0.1.0"
            sig = inspect.signature(func)
            code = inspect.getsource(func)
            code = "\n".join([line for line in code.splitlines() if not line.startswith('@MethodManager')])


            # Register method with automatic input/output discovery
            cls._registry[method_name] = MethodInfo(
                id=deterministic_uuid_v4(method_name + method_version),
                version=method_version,
                name=method_name,
                original_name=func.__name__,
                description=description or func.__doc__ or "",
                method=func,
                method_code=code,
                signature=sig,
                # inputs={k: v.annotation for k, v in sig.parameters.items()},
                # output=sig.return_annotation,
            )

            @wraps(func)
            def inner(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
                return validate_call(func)(*args, **kwargs)

            return inner

        return wrapper

    @classmethod
    def get_block_template(cls, *, method_name: str, block_modifications: typing.Optional[AnyDict] = None) -> Block:
        """Generate a block instance for a registered method."""
        method_info = cls._registry.get(method_name)
        if not method_info:
            raise NotRegisteredError(method_name)

        # Automatically set up the block
        block_modifications = block_modifications or {}
        block_modifications["id"] = block_modifications.get("id", str(uuid4()))
        block_modifications["method_id"] = method_name
        block_modifications["parameters"] = block_modifications.get("parameters", {})
        block_modifications["connections"] = block_modifications.get("connections", [])

        # instantiate the block
        block = Block(**block_modifications)
        return block

    @classmethod
    def get_method_info(cls, method_name: str) -> MethodInfo:
        """Retrieve method information."""
        method_info = cls._registry.get(method_name)
        if not method_info:
            raise NotRegisteredError(method_name)
        return method_info

    @classmethod
    def get_registry(cls):
        return cls._registry
