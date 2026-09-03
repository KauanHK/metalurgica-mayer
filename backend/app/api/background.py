"""Composição das tasks de background da aplicação.

Mesmo papel de `app/api/router.py`: é este módulo que conhece os módulos de
domínio, para que `app/core/startup.py` só consuma a lista sem importar
`app/modules` — a regra de dependência do core.

A Sprint 1 não tem worker. A lista existe desde já para que o primeiro (o
alerta de estoque mínimo, previsto na Sprint 5) tenha onde ser registrado sem
mexer no core.
"""

from collections.abc import Callable, Coroutine
from typing import Any

BackgroundTask = Callable[[], Coroutine[Any, Any, None]]

BACKGROUND_TASKS: list[BackgroundTask] = []
