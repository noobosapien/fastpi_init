from pydantic import BaseModel, StringConstraints
from typing import Annotated, Optional


class CategoryBase(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1)]
    slug: Annotated[str, StringConstraints(min_length=1)]
    is_active: Optional[bool] = False
    level: Optional[int] = 100
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryDeleteReturn(BaseModel):
    id: int
    name: Annotated[str, StringConstraints(min_length=1)]


class CategoryReturn(CategoryBase):
    id: int
