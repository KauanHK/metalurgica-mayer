from typing import Any


class AppError(Exception):
    """Base dos erros de aplicação.

    O handler em `app/core/handlers.py` converte qualquer subclasse na resposta
    JSON `{code, message, details}` com o `status_code` da classe — por isso os
    use cases levantam estas exceções em vez de `HTTPException`: o domínio não
    precisa conhecer HTTP.
    """

    status_code = 400
    code = "app_error"
    message = "Erro na aplicação."

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message or self.message)
        self.message = message or self.message
        self.details = details


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"
    message = "Recurso não encontrado."


class ConflictError(AppError):
    status_code = 409
    code = "conflict"
    message = "Conflito com o estado atual do recurso."


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"
    message = "Credenciais inválidas."


class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"
    message = "Você não tem permissão para executar esta ação."


class ValidationAppError(AppError):
    status_code = 422
    code = "validation_error"
    message = "Erro de validação."


class ServiceUnavailableError(AppError):
    status_code = 503
    code = "service_unavailable"
    message = "Serviço indisponível."
