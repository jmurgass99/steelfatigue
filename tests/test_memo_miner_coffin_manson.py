"""Tests para memoria handcalcs combinada Miner + Coffin-Manson."""
import pytest

from steelfatigue.memos import MinerMemoInput
from steelfatigue.memos.miner_coffin_manson import (
    CoffinMansonMemoInput,
    render_combined_fatigue_memo,
)


# ----- helpers -----

def _make_hcf_input() -> MinerMemoInput:
    return MinerMemoInput(
        detail_category=90,
        gamma_mf=1.35,
        spectrum=[
            {"label": "alta", "stress_range_MPa": 80, "cycles": 1e4},
            {"label": "media", "stress_range_MPa": 50, "cycles": 5e5},
        ],
    )


def _make_lcf_input() -> CoffinMansonMemoInput:
    return CoffinMansonMemoInput(
        sigma_f=900.0,
        b=-0.10,
        eps_f=0.30,
        c=-0.60,
        E=200_000.0,
        strain_amplitudes=[0.005, 0.010, 0.008, 0.012],
    )


# ----- tests -----

def test_render_produces_output():
    """El render retorna string no vacio tanto en latex como en markdown."""
    result = render_combined_fatigue_memo(
        hcf_input=_make_hcf_input(),
        lcf_input=_make_lcf_input(),
    )
    assert isinstance(result.markdown, str)
    assert len(result.markdown) > 0
    assert isinstance(result.latex, str)
    assert len(result.latex) > 0
    # Verify key sections are present in markdown
    assert "HCF" in result.markdown
    assert "LCF" in result.markdown
    assert "Resultado combinado" in result.markdown


def test_combined_damage_calculation():
    """D_total calculado correctamente como D_HCF + D_LCF."""
    result = render_combined_fatigue_memo(
        hcf_input=_make_hcf_input(),
        lcf_input=_make_lcf_input(),
    )
    assert result.D_total == pytest.approx(result.D_HCF + result.D_LCF)
    assert result.D_HCF > 0.0
    assert result.D_LCF > 0.0
    # Verify the HCF damage matches what render_miner_memo produces
    assert result.hcf_result is not None
    assert result.D_HCF == pytest.approx(result.hcf_result.total_damage)
    # Verify LCF damage matches sum of individual cycle damages
    lcf_damage_sum = sum(c.damage for c in result.lcf_cycles)
    assert result.D_LCF == pytest.approx(lcf_damage_sum)


def test_hcf_only_when_no_lcf():
    """Funciona sin datos LCF — D_LCF = 0, D_total = D_HCF."""
    result = render_combined_fatigue_memo(
        hcf_input=_make_hcf_input(),
        lcf_input=None,
    )
    assert result.D_LCF == 0.0
    assert result.D_total == pytest.approx(result.D_HCF)
    assert result.D_HCF > 0.0
    assert len(result.lcf_cycles) == 0
    assert result.hcf_result is not None
    # Markdown must still have both sections
    assert "HCF" in result.markdown
    assert "LCF" in result.markdown


def test_lcf_only_when_no_hcf():
    """Funciona sin datos HCF — D_HCF = 0, D_total = D_LCF."""
    result = render_combined_fatigue_memo(
        hcf_input=None,
        lcf_input=_make_lcf_input(),
    )
    assert result.D_HCF == 0.0
    assert result.D_total == pytest.approx(result.D_LCF)
    assert result.D_LCF > 0.0
    assert result.hcf_result is None
    assert len(result.lcf_cycles) > 0
    # Markdown must still have both sections
    assert "HCF" in result.markdown
    assert "LCF" in result.markdown
