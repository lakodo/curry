from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel  # type: ignore [partially]


class Flow(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: Optional[str] = Field(description="Human readable name for the flow")
    
