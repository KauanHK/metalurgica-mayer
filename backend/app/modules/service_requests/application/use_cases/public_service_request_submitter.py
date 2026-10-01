import logging

from sqlalchemy.exc import IntegrityError

from app.core.dates import today_br
from app.modules.clients.domain.entities import Client, NewClient
from app.modules.service_requests.application.dtos.commands import (
    SubmitPublicServiceRequestCommand,
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

logger = logging.getLogger(__name__)

SITE_CLIENT_NOTES = "Cadastrado pelo site"
"""Marca, na ficha, que o cliente nasceu de um envio do formulário público."""


class PublicServiceRequestSubmitter:
    """Registra a solicitação enviada pelo formulário público do site.

    Tudo numa única transação: acha (ou cadastra) o cliente e grava a solicitação,
    de modo que nunca sobra um cliente sem a solicitação que o originou.

    Decisões:

    - O cliente é procurado pelo documento (se informado) e, na falta dele, pelo
      e-mail, sem diferenciar maiúsculas. Se o documento informado não existe e o
      e-mail pertence a um cliente com *outro* documento, trata-se de outra
      pessoa/empresa: cadastra-se um cliente novo em vez de misturar os dois.
    - Cliente existente é reaproveitado **mesmo inativo**: o histórico não pode
      se perder nem se fragmentar em fichas duplicadas. Ele não é reativado, e a
      equipe decide o que fazer ao triar o pedido (`origin = website`). A regra
      de "cliente ativo" do fluxo interno (`ServiceRequestsCreator`) não vale
      aqui, porque quem decide é o visitante do site, não um usuário do ERP.
    - Dados do formulário **não sobrescrevem** o cliente existente: quem envia
      não está autenticado, e qualquer um poderia trocar telefone ou nome de
      um cliente só sabendo o e-mail dele.
    - A solicitação nasce `OPEN`, origem `WEBSITE`, datada de hoje.
    """

    def __init__(self, uow: ServiceRequestsUnitOfWorkProtocol) -> None:
        self._uow = uow

    async def submit(self, data: SubmitPublicServiceRequestCommand) -> ServiceRequest:
        try:
            return await self._submit_once(data)
        except IntegrityError:
            # Dois envios simultâneos com o mesmo documento novo: o segundo
            # esbarra na unicidade do documento. Na segunda tentativa o cliente
            # já existe (commitado pelo primeiro) e é só reaproveitá-lo.
            logger.info("Envio concorrente do mesmo documento; tentando de novo.")
            return await self._submit_once(data)

    async def _submit_once(
        self, data: SubmitPublicServiceRequestCommand
    ) -> ServiceRequest:
        async with self._uow as uow:
            client = await self._find_client(uow, data)
            if client is None:
                client = await uow.clients.create(
                    NewClient(
                        name=data.name,
                        document=data.document,
                        phone=data.phone,
                        email=data.email,
                        zip_code=None,
                        street=None,
                        number=None,
                        complement=None,
                        neighborhood=None,
                        city=None,
                        state=None,
                        notes=SITE_CLIENT_NOTES,
                        is_active=True,
                    )
                )
            return await uow.service_requests.create(
                NewServiceRequest(
                    client_id=client.id,
                    title=data.title,
                    description=data.description,
                    status=ServiceRequestStatus.OPEN,
                    origin=ServiceRequestOrigin.WEBSITE,
                    requested_at=today_br(),
                    due_date=None,
                )
            )

    @staticmethod
    async def _find_client(
        uow: ServiceRequestsUnitOfWorkProtocol,
        data: SubmitPublicServiceRequestCommand,
    ) -> Client | None:
        """Cliente já cadastrado a que o solicitante corresponde, se houver."""

        if data.document is not None:
            by_document = await uow.clients.get_by_document_or_none(data.document)
            if by_document is not None:
                return by_document

        if data.email is not None:
            by_email = await uow.clients.get_by_email_or_none(data.email)
            # Com documento informado, só vale o e-mail de um cliente que ainda
            # não tem documento (ou o mesmo, já tratado acima); documento
            # diferente é outra pessoa usando o mesmo e-mail.
            if by_email is not None and (
                data.document is None or by_email.document is None
            ):
                return by_email

        return None
