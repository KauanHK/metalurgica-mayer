import dataclasses
from typing import Any, ClassVar, Protocol


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]


class _UnsetType:
    """Sentinel para "campo não informado", distinto de `None`.

    Um PATCH precisa separar "não mandei este campo" de "mandei explicitamente
    nulo" — sem o sentinel, os dois chegariam como `None` e apagariam dado que
    ninguém pediu para apagar.
    """

    def __repr__(self) -> str:
        return "UNSET"

    def __bool__(self) -> bool:
        return False


UNSET = _UnsetType()
Unset = _UnsetType


def is_unset(value: object) -> bool:
    """Indica se um valor é o sentinel `UNSET`."""

    return isinstance(value, _UnsetType)


@dataclasses.dataclass(frozen=True, slots=True)
class BaseCommand:
    """Base dos comandos (entrada dos use cases)."""

    def to_dict(self) -> dict[str, Any]:
        """Converte o comando em dicionário."""

        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True, slots=True)
class BaseCreateCommand(BaseCommand):
    """Base dos comandos de criação."""


@dataclasses.dataclass(frozen=True, slots=True)
class BaseUpdateCommand(BaseCommand):
    """Base dos comandos de atualização, que usam `UNSET` nos campos opcionais."""

    def defined_values(self) -> dict[str, Any]:
        """Retorna só os campos efetivamente informados (não `UNSET`)."""

        return {
            field.name: getattr(self, field.name)
            for field in dataclasses.fields(self)
            if not isinstance(getattr(self, field.name), _UnsetType)
        }

    def has_changes(self) -> bool:
        """Indica se ao menos um campo foi informado."""

        return bool(self.defined_values())
