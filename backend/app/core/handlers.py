import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Registra os handlers que padronizam o corpo de erro da API.

    Toda resposta de erro sai como `{code, message, details}` — o front tem um
    formato só para tratar, em vez de adivinhar entre o `detail` do FastAPI e o
    corpo dos erros de domínio.
    """

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # O 422 do FastAPI traz `detail` com uma lista de erros do Pydantic. Ele é
        # remontado no mesmo formato dos demais para o front não precisar de dois
        # caminhos de tratamento.
        return JSONResponse(
            status_code=422,
            content={
                "code": "validation_error",
                "message": "Erro de validação nos dados enviados.",
                "details": [
                    {
                        "field": ".".join(str(p) for p in err["loc"][1:]),
                        "message": err["msg"],
                        "type": err["type"],
                    }
                    for err in exc.errors()
                ],
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        # Erro não previsto vai inteiro para o log e sai genérico na resposta:
        # stack trace em corpo de API é superfície de ataque, não diagnóstico.
        logger.exception("Erro não tratado na requisição.", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "code": "internal_error",
                "message": "Erro interno do servidor.",
                "details": None,
            },
        )
