"""Testes dos validadores de CPF/CNPJ da borda HTTP."""

import pytest

from app.core.validators import (
    validate_cnpj,
    validate_cpf,
    validate_cpf_or_cnpj,
)


class TestValidateCpf:
    def test_aceita_cpf_valido_formatado_e_devolve_so_digitos(self) -> None:
        assert validate_cpf("529.982.247-25") == "52998224725"

    def test_aceita_cpf_valido_sem_formatacao(self) -> None:
        assert validate_cpf("52998224725") == "52998224725"

    def test_rejeita_cpf_com_quantidade_errada_de_digitos(self) -> None:
        with pytest.raises(ValueError, match="11 dígitos"):
            validate_cpf("123")

    def test_rejeita_sequencia_repetida(self) -> None:
        with pytest.raises(ValueError, match="inválido"):
            validate_cpf("111.111.111-11")

    def test_rejeita_digito_verificador_incorreto(self) -> None:
        with pytest.raises(ValueError, match="inválido"):
            validate_cpf("529.982.247-24")


class TestValidateCnpj:
    def test_aceita_cnpj_valido_formatado_e_devolve_so_digitos(self) -> None:
        assert validate_cnpj("11.222.333/0001-81") == "11222333000181"

    def test_rejeita_cnpj_com_quantidade_errada_de_digitos(self) -> None:
        with pytest.raises(ValueError, match="14 dígitos"):
            validate_cnpj("11222333")

    def test_rejeita_digito_verificador_incorreto(self) -> None:
        with pytest.raises(ValueError, match="inválido"):
            validate_cnpj("11.222.333/0001-80")


class TestValidateCpfOrCnpj:
    def test_decide_por_cpf_quando_tem_11_digitos(self) -> None:
        assert validate_cpf_or_cnpj("529.982.247-25") == "52998224725"

    def test_decide_por_cnpj_quando_tem_14_digitos(self) -> None:
        assert validate_cpf_or_cnpj("11.222.333/0001-81") == "11222333000181"

    def test_rejeita_documento_com_tamanho_invalido(self) -> None:
        with pytest.raises(ValueError, match=r"CPF .* ou CNPJ"):
            validate_cpf_or_cnpj("123456")
