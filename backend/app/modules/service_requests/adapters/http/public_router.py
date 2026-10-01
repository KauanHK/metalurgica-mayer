"""Entrada pública de solicitações, para o formulário do site institucional.

**Sem autenticação** — é de propósito: o visitante do site não tem conta. Por
isso este router é separado do `router` autenticado e nada aqui devolve dados de
clientes. O envio sempre vira uma solicitação `origin = website`, vinculada a um
cliente (existente ou recém-cadastrado) pelo `PublicServiceRequestSubmitter`.
"""

import uuid

from fastapi import APIRouter, status

from app.modules.service_requests.adapters.http.dependencies import (
    ServiceRequestsUnitOfWorkDep,
)
from app.modules.service_requests.adapters.http.schemas import (
    PublicServiceRequestCreate,
    PublicServiceRequestReceipt,
)
from app.modules.service_requests.application.dtos.commands import (
    SubmitPublicServiceRequestCommand,
)
from app.modules.service_requests.application.use_cases.public_service_request_submitter import (  # noqa: E501
    PublicServiceRequestSubmitter,
)
from app.modules.service_requests.domain.entities import ServiceRequestStatus

public_router = APIRouter()


@public_router.post(
    "",
    response_model=PublicServiceRequestReceipt,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar solicitação pelo site",
)
async def submit_service_request(
    data: PublicServiceRequestCreate, uow: ServiceRequestsUnitOfWorkDep
) -> PublicServiceRequestReceipt:
    """Registra o pedido do formulário do site e o vincula a um cliente.

    Cliente é localizado pelo documento ou e-mail; se não existir, é cadastrado.
    A resposta traz só o id da solicitação e o status, para não revelar se o
    solicitante já era cliente.
    """

    if data.is_bot:
        # Honeypot: responde igual a um envio aceito, sem gravar nada, para o
        # robô não aprender que foi detectado.
        return PublicServiceRequestReceipt(
            id=uuid.uuid4(), status=ServiceRequestStatus.OPEN
        )

    service_request = await PublicServiceRequestSubmitter(uow=uow).submit(
        SubmitPublicServiceRequestCommand(
            name=data.name,
            email=data.email,
            phone=data.phone,
            document=data.document,
            title=data.title,
            description=data.description,
        )
    )
    return PublicServiceRequestReceipt(
        id=service_request.id, status=service_request.status
    )
