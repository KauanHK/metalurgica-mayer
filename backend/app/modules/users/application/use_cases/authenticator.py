from app.core.exceptions import UnauthorizedError
from app.core.security.passwords import hash_password, verify_password
from app.modules.users.application.ports.unit_of_work import UsersUnitOfWorkProtocol
from app.modules.users.domain.entities import User

# Hash de uma senha que nunca é usada para logar, conferido quando o e-mail não
# existe. Sem isso, o login responde mais rápido para um e-mail inexistente do
# que para uma senha errada — uma diferença de tempo que permite descobrir
# quais e-mails têm conta só de tentar e cronometrar a resposta.
_DUMMY_HASH = hash_password("senha-que-nunca-autentica-ninguem")


class Authenticator:
    """Confere e-mail e senha e devolve o usuário autenticado."""

    def __init__(self, uow: UsersUnitOfWorkProtocol) -> None:
        self._uow = uow

    async def authenticate(self, email: str, password: str) -> User:
        async with self._uow as uow:
            credentials = await uow.users.get_credentials_by_email(email)

        password_hash = credentials.password_hash if credentials else _DUMMY_HASH
        password_ok = verify_password(password, password_hash)
        if credentials is None or not password_ok:
            raise UnauthorizedError("E-mail ou senha inválidos.")
        if not credentials.user.is_active:
            raise UnauthorizedError("Usuário inativo. Procure um administrador.")
        return credentials.user
