"""Hash de senha com bcrypt.

Usa a biblioteca `bcrypt` diretamente, sem `passlib`: o passlib está sem
manutenção desde 2020 e quebra ao inspecionar `bcrypt.__about__`, removido no
bcrypt 4.1+. Uma dependência a menos, e o custo é uma função de três linhas.
"""

import bcrypt

# O bcrypt trunca em 72 bytes e, desde a versão 4, levanta erro em vez de cortar
# em silêncio. O corte é explícito aqui para que uma senha longa continue sendo
# aceita — e sempre da mesma forma no hash e na verificação.
_MAX_PASSWORD_BYTES = 72

# Custo do bcrypt: cada +1 dobra o tempo. 12 é o equilíbrio usual entre resistir
# a força bruta e não travar o login.
_ROUNDS = 12


def _encode(password: str) -> bytes:
    return password.encode("utf-8")[:_MAX_PASSWORD_BYTES]


def hash_password(password: str) -> str:
    """Gera o hash da senha, com salt novo a cada chamada."""

    return bcrypt.hashpw(_encode(password), bcrypt.gensalt(rounds=_ROUNDS)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Confere a senha contra o hash guardado."""

    try:
        return bcrypt.checkpw(_encode(password), password_hash.encode("utf-8"))
    except ValueError:
        # Hash malformado no banco: é senha inválida, não erro 500 no login.
        return False
