from typing import List, Optional
from uuid import UUID

from sqlalchemy.schema import Column
from sqlalchemy.types import JSON
from sqlmodel import Field

from joj.horse.schemas.base import BaseModel, BaseORMSchema, IDMixin, TimestampMixin


class ProblemConfigBase(BaseORMSchema):
    commit_message: str = Field(
        "", index=False, nullable=False, sa_column_kwargs={"server_default": ""}
    )
    data_version: int = Field(
        2, index=False, nullable=False, sa_column_kwargs={"server_default": "2"}
    )


class ProblemConfigCommit(BaseModel):
    pass


class ProblemConfig(ProblemConfigBase, IDMixin):
    languages: List[str] = Field(
        [],
        index=False,
        sa_column=Column(JSON, nullable=False, server_default="[]"),
    )
    commit_id: str = Field(
        "", index=False, nullable=False, sa_column_kwargs={"server_default": ""}
    )
    committer_id: Optional[UUID] = None


class ProblemConfigDetail(TimestampMixin, ProblemConfig):
    pass
