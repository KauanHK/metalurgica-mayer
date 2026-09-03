from collections.abc import Sequence
from math import ceil

from pydantic import BaseModel, Field, computed_field


class PaginationParams(BaseModel):
    """Query params de paginação, comuns a todas as listagens."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        """Deslocamento correspondente à página atual."""

        return (self.page - 1) * self.page_size


class PaginatedResponse[T](BaseModel):
    """Envelope de resposta das listagens."""

    data: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_pages(self) -> int:
        """Número de páginas, derivado do total e do tamanho da página."""

        return ceil(self.total / self.page_size) if self.total > 0 else 0


def build_paginated_response[T](
    *,
    items: Sequence[T],
    total: int,
    page: int,
    page_size: int,
) -> PaginatedResponse[T]:
    """Monta a resposta paginada a partir dos itens já serializados."""

    return PaginatedResponse[T](
        data=list(items),
        total=total,
        page=page,
        page_size=page_size,
    )
