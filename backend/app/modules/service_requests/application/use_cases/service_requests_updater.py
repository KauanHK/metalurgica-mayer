import uuid

from app.core.exceptions import ConflictError
from app.core.types import Unset
from app.modules.service_requests.application.dtos.commands import (
    UpdateServiceRequestCommand,
)
from app.modules.service_requests.application.ports.unit_of_work import (
    ServiceRequestsUnitOfWorkProtocol,
)
from app.modules.service_requests.domain.entities import (
    ServiceRequest,
    ServiceRequestStatus,
    UpdateServiceRequest,
)
from app.modules.service_requests.domain.rules import (
    ensure_due_date_not_before_request,
)


class ServiceRequestsUpdater:
    """Altera os campos informados de uma solicitação, inclusive o status.

    Entre os estados em andamento (`OPEN`, `IN_ANALYSIS`, `IN_PROGRESS`) a troca
    é livre — a equipe avança e também volta uma solicitação quando o escopo
    muda. `COMPLETED` e `CANCELLED` são terminais: de lá não há saída (409).
    """

    def __init__(self, uow: ServiceRequestsUnitOfWorkProtocol) -> None:
        self._uow = uow

    async def update(
        self, id_: uuid.UUID, data: UpdateServiceRequestCommand
    ) -> ServiceRequest:
        async with self._uow as uow:
            current = await uow.service_requests.get_by_id(id_)

            if (
                not isinstance(data.status, Unset)
                and current.is_terminal
                and data.status != current.status
            ):
                situacao = (
                    "concluída"
                    if current.status == ServiceRequestStatus.COMPLETED
                    else "cancelada"
                )
                raise ConflictError(
                    f"Uma solicitação {situacao} não pode mudar de status. "
                    "Cadastre uma nova solicitação."
                )

            # Valida o prazo sobre o resultado da mescla: mudar só o
            # `requested_at` pode deixar o `due_date` já gravado para trás.
            requested_at = (
                current.requested_at
                if isinstance(data.requested_at, Unset)
                else data.requested_at
            )
            due_date = (
                current.due_date if isinstance(data.due_date, Unset) else data.due_date
            )
            ensure_due_date_not_before_request(requested_at, due_date)

            return await uow.service_requests.update(
                id_, UpdateServiceRequest(**data.defined_values())
            )
