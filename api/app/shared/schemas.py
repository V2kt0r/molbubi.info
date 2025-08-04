import math
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses"""
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response wrapper"""
    data: list[T]
    meta: PaginationMeta


def create_pagination_meta(skip: int, limit: int, total: int) -> PaginationMeta:
    """Create pagination metadata from skip/limit/total"""
    page = (skip // limit) + 1
    pages = math.ceil(total / limit) if total > 0 else 1
    has_next = skip + limit < total
    has_prev = skip > 0
    
    return PaginationMeta(
        page=page,
        per_page=limit,
        total=total,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )