from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa dos models SQLAlchemy.

    É o `Base.metadata` desta classe que o Alembic compara com o banco para
    gerar as migrations — um model que não herde daqui é invisível para o
    autogenerate (ver `migrations/env.py`).
    """
