"""Regresion: FatigueEvaluator no debe fabricar aprobados silenciosos.

La ausencia se propaga como ausencia. Un dato que falta (categoria de detalle
nula, bloque de espectro sin rango o sin ciclos) NO puede convertirse en un dano
0.0 que el informe imprime como ``PASS`` / ``Fatigue life is adequate``.

``fatiguejm.services.fatigue_service`` ya validaba esto con
:class:`DetailCategoryError` / :class:`SpectrumError`; el evaluador subyacente
(publico y usable directamente) no lo hacia.
"""
from __future__ import annotations

import pytest

from fatiguejm.exceptions import DetailCategoryError, SpectrumError
from fatiguejm.sn_curves import FatigueEvaluator


class TestCategoriaDetalleInvalida:
    def test_categoria_nula_no_puede_rendir_pass(self) -> None:
        """Delta_sigma_C = 0 es resistencia a fatiga NULA: jamas puede dar PASS."""
        with pytest.raises(DetailCategoryError):
            FatigueEvaluator(detail_category=0.0)

    def test_categoria_negativa_rechazada(self) -> None:
        with pytest.raises(DetailCategoryError):
            FatigueEvaluator(detail_category=-90.0)

    def test_gamma_mf_no_positivo_rechazado(self) -> None:
        with pytest.raises(DetailCategoryError):
            FatigueEvaluator(detail_category=90.0, gamma_mf=0.0)


class TestBloqueIncompletoNoSeIgnora:
    def test_bloque_sin_stress_range_rechazado(self) -> None:
        """Sin rango de tension no hay dano calculable: no vale asumir 0 MPa."""
        ev = FatigueEvaluator(detail_category=90.0)
        with pytest.raises(SpectrumError):
            ev.calculate_damage([{"cycles": 1.0e9}])

    def test_bloque_sin_cycles_rechazado(self) -> None:
        ev = FatigueEvaluator(detail_category=90.0)
        with pytest.raises(SpectrumError):
            ev.calculate_damage([{"stress_range": 200.0}])

    def test_informe_no_declara_vida_adecuada_con_bloque_incompleto(self) -> None:
        """El string 'Fatigue life is adequate' no puede salir de un dato ausente."""
        ev = FatigueEvaluator(detail_category=90.0)
        with pytest.raises(SpectrumError):
            ev.evaluation_report([{"cycles": 1.0e9}])


class TestCapacidadNulaTrasMutarElAtributo:
    """``detail_category`` es un atributo PUBLICO y mutable: la validacion del
    constructor se puede sortear asignandolo despues. Ese camino tambien debe
    fallar ruidosamente en vez de saltarse el bloque con dano 0.0."""

    def test_categoria_anulada_despues_del_constructor(self) -> None:
        ev = FatigueEvaluator(detail_category=90.0)
        ev.detail_category = 0.0
        with pytest.raises(SpectrumError):
            ev.calculate_damage([{"stress_range": 200.0, "cycles": 1.0e9}])


class TestCaminoValidoIntacto:
    def test_espectro_completo_sigue_funcionando(self) -> None:
        ev = FatigueEvaluator(detail_category=90.0, gamma_mf=1.35)
        d = ev.calculate_damage(
            [{"stress_range": 80.0, "cycles": 1.0e4},
             {"stress_range": 50.0, "cycles": 5.0e5}]
        )
        assert d > 0.0
        assert ev.evaluation_report(
            [{"stress_range": 80.0, "cycles": 1.0e4}]
        )["status"] == "PASS"

    def test_rango_nulo_explicito_es_dano_cero(self) -> None:
        """Un 0.0 DECLARADO por el usuario si es un dato: no produce dano."""
        ev = FatigueEvaluator(detail_category=90.0)
        assert ev.calculate_damage([{"stress_range": 0.0, "cycles": 1.0e9}]) == 0.0
