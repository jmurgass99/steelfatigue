"""Pruebas de la jerarquia de excepciones."""
from __future__ import annotations

import pytest

from fatiguejm.exceptions import (
    DetailCategoryError,
    FatigueError,
    SpectrumError,
    ValidationError,
)


@pytest.mark.unit
def test_jerarquia_base() -> None:
    assert issubclass(ValidationError, FatigueError)
    assert issubclass(DetailCategoryError, ValidationError)
    assert issubclass(SpectrumError, ValidationError)


@pytest.mark.unit
def test_detail_category_atrapable_como_base() -> None:
    with pytest.raises(FatigueError):
        raise DetailCategoryError("categoria invalida")


@pytest.mark.unit
def test_spectrum_es_validation() -> None:
    with pytest.raises(ValidationError):
        raise SpectrumError("espectro vacio")


@pytest.mark.unit
def test_mensaje_se_preserva() -> None:
    exc = SpectrumError("bloque negativo")
    assert str(exc) == "bloque negativo"
