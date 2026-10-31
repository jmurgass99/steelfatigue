"""Jerarquia de excepciones de SteelFatigue.

Todas las excepciones del paquete heredan de :class:`FatigueError`.
"""
from __future__ import annotations


class FatigueError(Exception):
    """Excepcion base para todos los errores del paquete SteelFatigue."""


class ValidationError(FatigueError):
    """Error de validacion de datos de entrada (categoria, espectro, factores)."""


class DetailCategoryError(ValidationError):
    """Categoria de detalle invalida (<= 0)."""


class SpectrumError(ValidationError):
    """Espectro de tensiones invalido (bloques mal formados o negativos)."""
