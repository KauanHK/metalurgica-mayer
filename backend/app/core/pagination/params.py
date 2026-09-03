from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PageParams:
    """Parâmetros de paginação, já validados na borda HTTP."""

    page: int = 1
    page_size: int = 20


@dataclass(frozen=True, slots=True)
class Page[T]:
    """Uma página de resultados, com o total para o front montar o paginador."""

    items: list[T]
    total: int
    page: int
    page_size: int
