from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, StrictInt, StrictStr, field_validator

from .data import entities as models


class ProjectCategory(BaseModel):
    name: StrictStr

    def __str__(self) -> str:
        return f"{self.name}"

    model_config = {"from_attributes": True}


class Task(BaseModel):
    id: StrictInt
    name: StrictStr
    project_category: ProjectCategory | None = None

    def __str__(self) -> str:
        if self.project_category is None:
            return f"#{self.id} {self.name}"
        return f"#{self.id} {self.project_category}/{self.name}"

    @field_validator("project_category", mode="before")
    @classmethod
    def pony_set_project_category(cls, value: models.ProjectCategory | None) -> Any:
        if value is None:
            return None
        return value.to_dict()

    model_config = {"from_attributes": True}


class WorkEntry(BaseModel):
    id: StrictInt
    task: Task
    start: datetime
    end: Optional[datetime]

    def __str__(self) -> str:
        datetime_format = "%H:%M"
        if self.end is None:
            return f"{self.start.strftime(datetime_format)} - ??:?? ({self.task})"
        return f"{self.start.strftime(datetime_format)} - {self.end.strftime(datetime_format)} ({self.task})"

    model_config = {"from_attributes": True}

