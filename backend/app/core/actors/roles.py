from enum import StrEnum


class UserRole(StrEnum):
    """Perfil de acesso do usuário do ERP.

    Vive no core, e não no módulo `users`, porque `UserActor` precisa dele e
    **`app/core` nunca importa `app/modules`** — a dependência aponta sempre dos
    módulos para o core. O módulo `users` importa daqui.

    A autorização por perfil é entregue na Sprint 2; a coluna já nasce aqui para
    que o cadastro não precise de migration de dados depois.
    """

    ADMIN = "admin"
    """Acesso total, incluindo o cadastro de outros usuários."""

    OPERATOR = "operator"
    """Acesso à operação do dia a dia (clientes, solicitações, orçamentos)."""
