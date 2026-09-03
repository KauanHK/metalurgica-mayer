import logging

from app.core.settings import settings

_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


def configure_logging() -> None:
    """Configura o root logger da aplicação.

    O uvicorn só configura os loggers `uvicorn`/`uvicorn.error`/`uvicorn.access`
    (com `propagate=False`); sem isto, `logger.info`/`logger.debug` de qualquer
    módulo `app.*` some silenciosamente — só `warning`/`error` apareceriam, pelo
    handler de último recurso do Python.
    """

    logging.basicConfig(level=settings.LOG_LEVEL, format=_FORMAT, force=True)
