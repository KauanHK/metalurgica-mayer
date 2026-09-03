"""Validadores de documentos brasileiros, usados nos schemas da borda HTTP."""

from typing import Annotated

from pydantic import BeforeValidator


def _only_digits(value: str) -> str:
    return "".join(filter(str.isdigit, value))


def validate_cpf(value: str) -> str:
    """Valida um CPF pelos dígitos verificadores e devolve só os dígitos."""

    digits = _only_digits(value)

    if len(digits) != 11:
        raise ValueError("CPF deve conter 11 dígitos.")

    # Sequências repetidas (000.000.000-00 e afins) passam no cálculo dos
    # dígitos verificadores, então precisam ser barradas à parte.
    if len(set(digits)) == 1:
        raise ValueError("CPF inválido.")

    def calc_digit(partial: str, weight: int) -> int:
        total = sum(
            int(d) * w for d, w in zip(partial, range(weight, 1, -1), strict=True)
        )
        remainder = (total * 10) % 11
        return 0 if remainder == 10 else remainder

    if calc_digit(digits[:9], weight=10) != int(digits[9]):
        raise ValueError("CPF inválido.")
    if calc_digit(digits[:10], weight=11) != int(digits[10]):
        raise ValueError("CPF inválido.")

    return digits


def validate_cnpj(value: str) -> str:
    """Valida um CNPJ pelos dígitos verificadores e devolve só os dígitos."""

    digits = _only_digits(value)

    if len(digits) != 14:
        raise ValueError("CNPJ deve conter 14 dígitos.")

    if len(set(digits)) == 1:
        raise ValueError("CNPJ inválido.")

    def calc_digit(partial: str, weights: list[int]) -> int:
        total = sum(int(d) * w for d, w in zip(partial, weights, strict=True))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    weights_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    if calc_digit(digits[:12], weights_1) != int(digits[12]):
        raise ValueError("CNPJ inválido.")
    if calc_digit(digits[:13], weights_2) != int(digits[13]):
        raise ValueError("CNPJ inválido.")

    return digits


def validate_cpf_or_cnpj(value: str) -> str:
    """Aceita CPF ou CNPJ, decidindo pelo número de dígitos."""

    digits = _only_digits(value)

    if len(digits) == 11:
        return validate_cpf(value)
    if len(digits) == 14:
        return validate_cnpj(value)
    raise ValueError("Documento deve ser um CPF (11 dígitos) ou CNPJ (14 dígitos).")


Cpf = Annotated[str, BeforeValidator(validate_cpf)]
Cnpj = Annotated[str, BeforeValidator(validate_cnpj)]
CpfOrCnpj = Annotated[str, BeforeValidator(validate_cpf_or_cnpj)]
