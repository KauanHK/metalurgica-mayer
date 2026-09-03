"""Cria o usuário administrador inicial do ERP.

Execução (a partir de `backend/`, com o banco no ar e as migrations aplicadas):

    uv run python -m scripts.seed.initial_user

O módulo `users` só ganha casos de uso na Sprint 2, então a inserção aqui é
feita direto pelo model SQLAlchemy. Quando o cadastro de usuários existir, este
script deve passar a chamar o caso de uso em vez de escrever na tabela.

Nome, e-mail e senha vêm de `SEED_USER_NAME`, `SEED_USER_EMAIL` e
`SEED_USER_PASSWORD` — as mesmas chaves do `.env.example` da raiz. Elas não
moram em `Settings` porque `Settings` usa `extra="forbid"`: são variáveis deste
script, não configuração da aplicação.
"""

import asyncio
import os
import sys

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.actors.roles import UserRole
from app.core.db.session import db
from app.core.security.passwords import hash_password
from app.modules.users.adapters.db.models import User

# Precisam bater com o `.env.example` da raiz: quem sobe o compose sem editar
# nada tem que conseguir entrar com estas credenciais.
DEFAULT_NAME = "Administrador"
DEFAULT_EMAIL = "admin@metalurgicamayer.com.br"
DEFAULT_PASSWORD = "admin123"


def _env(name: str, default: str) -> str:
    """Lê a variável de ambiente, tratando string vazia como ausente."""

    return os.getenv(name, "").strip() or default


def _warn_if_default_password(password: str) -> None:
    """Alerta quando a senha usada é a do `.env.example`.

    Essa senha está versionada no repositório: qualquer pessoa com acesso ao
    código a conhece. O aviso existe para que ninguém publique um ambiente com
    ela sem perceber.
    """

    if password != DEFAULT_PASSWORD:
        return

    print("")
    print("=" * 72)
    print("ATENÇÃO: a senha usada é a padrão do .env.example, publicada no")
    print("repositório e portanto conhecida por qualquer pessoa que veja o")
    print("código. Defina SEED_USER_PASSWORD antes de rodar este seed em")
    print("homologação ou produção, ou troque a senha no primeiro acesso.")
    print("=" * 72)
    print("")


async def seed_initial_user() -> int:
    """Insere o administrador se ele ainda não existir. Devolve o código de saída."""

    name = _env("SEED_USER_NAME", DEFAULT_NAME)
    email = _env("SEED_USER_EMAIL", DEFAULT_EMAIL).lower()
    password = _env("SEED_USER_PASSWORD", DEFAULT_PASSWORD)

    db.init()
    try:
        async with db.create_session() as session:
            existing = await session.scalar(select(User).where(User.email == email))
            if existing is not None:
                print(
                    f"Usuário '{email}' já existe (perfil: {existing.role.value}). "
                    "Nada foi alterado."
                )
                print(
                    "A senha de um usuário existente nunca é redefinida por este "
                    "seed — use a troca de senha do sistema."
                )
                return 0

            session.add(
                User(
                    name=name,
                    email=email,
                    password_hash=hash_password(password),
                    role=UserRole.ADMIN,
                    is_active=True,
                )
            )
            try:
                await session.commit()
            except IntegrityError:
                # A consulta acima não impede duas execuções simultâneas de
                # tentarem inserir o mesmo e-mail; quem garante a unicidade é o
                # índice da tabela. Cair aqui significa que a outra execução
                # venceu, e o resultado desejado já está no banco.
                await session.rollback()
                print(f"Usuário '{email}' já havia sido criado. Nada foi alterado.")
                return 0

        print(f"Usuário administrador criado: {name} <{email}> (perfil: admin).")
        _warn_if_default_password(password)
        return 0
    except SQLAlchemyError as exc:
        print(f"Falha ao acessar o banco de dados: {exc}", file=sys.stderr)
        print(
            "Confira se o Postgres está no ar e se as migrations foram "
            "aplicadas (`uv run alembic upgrade head`).",
            file=sys.stderr,
        )
        return 1
    finally:
        await db.close()


def main() -> int:
    return asyncio.run(seed_initial_user())


if __name__ == "__main__":
    raise SystemExit(main())
