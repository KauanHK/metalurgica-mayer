from app.core.dates import today_br
from app.core.exceptions import ValidationAppError
from app.modules.service_requests.application.dtos.commands import (
    CreateServiceRequestCommand,
)
from app.modules.service_requests.application.ports.unit_of_work import (
    ServiceRequestsUnitOfWorkProtocol,
)
from app.modules.service_requests.domain.entities import (
    NewServiceRequest,
    ServiceRequest,
    ServiceRequestOrigin,
    ServiceRequestStatus,
)
from app.modules.service_requests.domain.rules import (
    ensure_due_date_not_before_request,
)


class ServiceRequestsCreator:
    """Registra uma solicitação de serviço de um cliente.

    A solicitação nasce `OPEN` e com origem `INTERNAL` (quem cadastra é um
    usuário do ERP). O cliente precisa existir e estar ativo: cliente inativo é
    quem saiu da operação, e abrir pedido novo para ele é quase sempre engano.
    """

    def __init__(self, uow: ServiceRequestsUnitOfWorkProtocol) -> None:
        self._uow = uow

    async def create(self, data: CreateServiceRequestCommand) -> ServiceRequest:
        requested_at = data.requested_at or today_br()
        ensure_due_date_not_before_request(requested_at, data.due_date)

        async with self._uow as uow:
            client = await uow.clients.get_by_id_or_none(data.client_id)
            if client is None:
                raise ValidationAppError(
                    "Cliente não encontrado.",
                    details=[
                        {
                            "field": "client_id",
                            "message": "Cliente não encontrado.",
                            "type": "value_error",
                        }
                    ],
                )
            if not client.is_active:
                raise ValidationAppError(
                    "Cliente inativo não pode receber novas solicitações.",
                    details=[
                        {
                            "field": "client_id",
                            "message": "Cliente inativo.",
                            "type": "value_error",
                        }
                    ],
                )
            return await uow.service_requests.create(
                NewServiceRequest(
                    client_id=data.client_id,
                    title=data.title,
                    description=data.description,
                    status=ServiceRequestStatus.OPEN,
                    origin=ServiceRequestOrigin.INTERNAL,
                    requested_at=requested_at,
                    due_date=data.due_date,
                )
            )
