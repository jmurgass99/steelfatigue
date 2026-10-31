from __future__ import annotations

"""Aplicacion FastAPI ligera para FatigueJm.
"""
from typing import Any
from pydantic import BaseModel, Field


class StressBlockPayload(BaseModel):
    stress_range: float = Field(..., ge=0, description="Rango de tensiones [MPa]")
    cycles: float = Field(..., ge=0, description="Numero de ciclos aplicados")


class FatiguePayload(BaseModel):
    detail_category: float = Field(..., gt=0, description="Categoria del detalle")
    gamma_mf: float = Field(1.35, gt=0, description="Factor parcial de seguridad")
    spectrum: list[StressBlockPayload]


class UFMPayload(BaseModel):
    alpha: float = Field(..., gt=0)
    beta: float = Field(..., gt=0)
    ec: float = Field(..., ge=0)
    eb: float = Field(..., ge=0)
    P_brace: float = Field(...)
    theta_rad: float = Field(...)


class LowCyclePayload(BaseModel):
    plastic_rotation_history: list[float] = Field(..., min_length=1)
    eps_f: float = Field(0.30, gt=0)
    c: float = Field(-0.60, lt=0)
    geometric_factor: float = Field(0.50, gt=0)


class HotSpotPayload(BaseModel):
    sigma_t_half: float
    sigma_3t_half: float
    thickness_mm: float = Field(..., gt=0)
    method: str = "linear"
    sigma_5t_half: float | None = None


class HotSpotAnalysisPayload(BaseModel):
    sigma_t_half: float
    sigma_3t_half: float
    thickness_mm: float = Field(..., gt=0)
    weld_type: str = "butt"
    fat_class: float = Field(90.0, gt=0)
    method: str = "linear"
    sigma_5t_half: float | None = None
    gamma_mf: float = Field(1.0, gt=0)


class ParisPayload(BaseModel):
    a_initial_mm: float = Field(..., gt=0, description="Tamaño inicial de grieta")
    a_critical_mm: float = Field(..., gt=0, description="Tamaño crítico de grieta")
    delta_sigma_MPa: float = Field(..., gt=0, description="Rango de tensión")
    Y: float = Field(1.12, gt=0, description="Factor geométrico")
    C: float = Field(6.9e-12, gt=0, description="Constante de Paris")
    m: float = Field(3.0, gt=0, description="Exponente de Paris")
    n_increments: int = Field(200, ge=10)


class MeanStressPayload(BaseModel):
    sigma_a_MPa: float = Field(..., ge=0, description="Amplitud de tensión")
    sigma_m_MPa: float = Field(..., description="Tensión media")
    Se_MPa: float = Field(..., gt=0, description="Límite de fatiga")
    Su_MPa: float = Field(..., gt=0, description="Resistencia última")
    Sy_MPa: float | None = Field(None, description="Límite elástico (Soderberg)")
    criterion: str = Field("goodman", description="goodman | gerber | soderberg")


class EndurancePayload(BaseModel):
    Su_MPa: float = Field(..., gt=0, description="Resistencia última")
    finish: str = Field("machined", description="ground|machined|hot-rolled|as-forged")
    d_mm: float = Field(10.0, gt=0, description="Diámetro/dimensión")
    loading: str = Field("bending", description="bending|axial|torsion")
    T_C: float = Field(20.0, description="Temperatura [°C]")
    reliability: float = Field(0.5, gt=0, lt=1, description="Confiabilidad")
    rotating: bool = True


def create_router() -> Any:
    """Devuelve el APIRouter con los endpoints. Mountable en gateway."""
    from fastapi import APIRouter, HTTPException

    from ..exceptions import ValidationError
    from ..services import (
        FatigueInput,
        LowCycleInput,
        StressBlock,
        UFMInput,
        evaluate_fatigue,
        evaluate_lowcycle,
        evaluate_ufm,
    )

    router = APIRouter()

    @router.get("/api/fatigue/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @router.post("/api/fatigue/evaluate", summary="Evaluación de daño por fatiga acumulada según Palmgren-Miner (EN 1993-1-9)")
    def evaluate(payload: FatiguePayload) -> dict[str, Any]:
        try:
            data = FatigueInput(
                detail_category=payload.detail_category,
                gamma_mf=payload.gamma_mf,
                spectrum=[
                    StressBlock(stress_range=b.stress_range, cycles=b.cycles)
                    for b in payload.spectrum
                ],
            )
            result = evaluate_fatigue(data)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return result.to_dict()

    @router.post("/api/fatigue/ufm", summary="Método de la fuerza unificada (UFM) para uniones y detalles de fatiga")
    def ufm(payload: UFMPayload) -> dict[str, Any]:
        try:
            return evaluate_ufm(UFMInput(**payload.model_dump())).to_dict()
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @router.post("/api/fatigue/lowcycle", summary="Fatiga de bajo número de ciclos (LCF) según Coffin-Manson / Morrow")
    def lowcycle(payload: LowCyclePayload) -> dict[str, Any]:
        try:
            return evaluate_lowcycle(LowCycleInput(**payload.model_dump())).to_dict()
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @router.post("/api/fatigue/hotspot", summary="Cálculo de tensiones en puntos calientes (Hot-Spot Stresses) según IIW")
    def hotspot(payload: HotSpotPayload) -> dict[str, float]:
        from ..hotspot import HotSpotInput, hot_spot_stress
        try:
            sigma_hs = hot_spot_stress(HotSpotInput(**payload.model_dump()))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {"sigma_hot_spot_MPa": sigma_hs}

    @router.post("/api/fatigue/hotspot/analysis")
    def hotspot_analysis(payload: HotSpotAnalysisPayload) -> dict[str, Any]:
        from ..services.hotspot_service import run_hotspot_analysis
        try:
            result = run_hotspot_analysis(**payload.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return result.to_dict()

    @router.post("/api/fatigue/paris", summary="Propagación de fisuras por fatiga según ley de Paris-Erdogan")
    def paris(payload: ParisPayload) -> dict[str, Any]:
        """Crecimiento de grieta por ley de Paris (integración da/dN)."""
        from ..paris_law import ParisInput, integrate_paris
        try:
            r = integrate_paris(ParisInput(**payload.model_dump()))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        a_vs_N = r.a_vs_N.tolist() if hasattr(r.a_vs_N, "tolist") else list(r.a_vs_N)
        return {"N_cycles": r.N_cycles, "failure": r.failure, "a_vs_N": a_vs_N}

    @router.post("/api/fatigue/mean-stress", summary="Corrección por tensión media en fatiga según Goodman, Gerber y Soderberg")
    def mean_stress(payload: MeanStressPayload) -> dict[str, Any]:
        """Corrección por tensión media (Goodman/Gerber/Soderberg)."""
        from ..mean_stress import (
            MeanStressInput,
            equivalent_reversed_stress,
            safety_factors,
        )
        from ..validation import require_in
        try:
            crit = require_in(
                payload.criterion.lower(),
                ["goodman", "gerber", "soderberg"],
                "criterion",
            )
            sigma_rev = equivalent_reversed_stress(
                payload.sigma_a_MPa, payload.sigma_m_MPa, payload.Su_MPa,
                criterion=crit, Sy=payload.Sy_MPa,
            )
            sf = safety_factors(MeanStressInput(
                sigma_a_MPa=payload.sigma_a_MPa, sigma_m_MPa=payload.sigma_m_MPa,
                Se_MPa=payload.Se_MPa, Su_MPa=payload.Su_MPa, Sy_MPa=payload.Sy_MPa,
            ))
        # ValidationError (fatiguejm) NO hereda de ValueError: sin capturarla
        # explicitamente, un criterio desconocido o Soderberg sin Sy escapaban
        # como 500 en vez de 422.
        except (ValueError, ValidationError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {"sigma_equivalent_reversed_MPa": sigma_rev, "safety_factors": sf}

    @router.post("/api/fatigue/endurance", summary="Límite de fatiga corregido por factores de Marin (Shigley) — superficie, tamaño, carga, temperatura, confiabilidad")
    def endurance(payload: EndurancePayload) -> dict[str, Any]:
        """Límite de fatiga corregido (factores de Marin ka·kb·kc·kd·ke)."""
        from ..endurance_factors import EnduranceInput, endurance_limit
        try:
            return endurance_limit(EnduranceInput(**payload.model_dump()))
        # `finish` y `loading` son cadenas libres en el payload y las valida el
        # dominio con ValidationError, que NO hereda de ValueError: un acabado o
        # una carga desconocidos daban 500 en vez de 422.
        except (ValueError, ValidationError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return router


def create_app() -> Any:
    """Crea y devuelve la app FastAPI standalone."""
    from fastapi import FastAPI

    app = FastAPI(title="FatigueJm API", version="1.0.0")
    app.include_router(create_router())
    return app

