"""Data e hora no fuso da operação.

Os containers rodam em UTC, então `date.today()` e `datetime.now()` respondem em
UTC — e depois das 21h em Brasília o "hoje" do processo já é o dia seguinte.
Como o dia é regra de negócio em vários pontos do ERP (data da solicitação,
validade do orçamento, movimentação de estoque), toda data "de hoje" do domínio
passa por aqui em vez de perguntar ao relógio do sistema.

Carimbos técnicos (auditoria, expiração de token) seguem em `datetime.now(UTC)`.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

# Fuso da empresa (Massaranduba/SC). Não use o TZ do sistema: a data de negócio
# não pode depender de como o container foi configurado.
BR_TZ = ZoneInfo("America/Sao_Paulo")


def now_br() -> datetime:
    """Agora no fuso da operação, com offset preenchido."""

    return datetime.now(BR_TZ)


def today_br() -> date:
    """Data de hoje no fuso da operação."""

    return now_br().date()
