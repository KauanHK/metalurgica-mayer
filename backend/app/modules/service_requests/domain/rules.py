from datetime import date

from app.core.exceptions import ValidationAppError


def ensure_due_date_not_before_request(
    requested_at: date, due_date: date | None
) -> None:
    """Garante que o prazo não vence antes de a solicitação ter sido feita."""

    if due_date is not None and due_date < requested_at:
        raise ValidationAppError(
            "O prazo não pode ser anterior à data da solicitação.",
            details=[
                {
                    "field": "due_date",
                    "message": "O prazo não pode ser anterior à data da solicitação.",
                    "type": "value_error",
                }
            ],
        )
