"""Capa de servicios: funciones puras tipadas que envuelven la API existente."""
from .fatigue_service import (
    FatigueInput,
    FatigueResult,
    StressBlock,
    evaluate_fatigue,
)
from .lowcycle_service import (
    LowCycleInput,
    LowCycleResult,
    UFMInput,
    UFMResult,
    evaluate_lowcycle,
    evaluate_ufm,
)
from .hotspot_service import (
    HotSpotAnalysisInput,
    HotSpotAnalysisResult,
    run_hotspot_analysis,
)

__all__ = [
    "FatigueInput",
    "FatigueResult",
    "StressBlock",
    "evaluate_fatigue",
    "UFMInput",
    "UFMResult",
    "evaluate_ufm",
    "LowCycleInput",
    "LowCycleResult",
    "evaluate_lowcycle",
    "HotSpotAnalysisInput",
    "HotSpotAnalysisResult",
    "run_hotspot_analysis",
]
