"""
Verificación a rotura frágil EN 1993-1-10 (EC3-1-10) — selección de subgrado /
espesor máximo admisible frente a fractura frágil.

Implementado aquí (SteelFatigue), NO en FireSteelJm: el propio docstring de
`steelfatigue.__init__` ya declara el paquete como "Fatigue and Brittle Fracture
Evaluation Engine", y dos fichas máster independientes (W01468, W01469 — misma
convocatoria de examen, transcripciones distintas, resultados coincidentes al
decimal) resuelven un ejemplo COMPLETO de EC3-1-10 de principio a fin: viga
IPE 500 / S355JR, T₀=−35°C, verificación de espesor máximo admisible frente a
rotura frágil. Ese es el "ejemplo completo" que habilita la excepción de la
tarea (ver CLAUDE.md del package): implementar aquí, no inventar más alcance.

Alcance deliberadamente MÍNIMO — solo lo que el ejemplo ancla:

    1. Temperatura de referencia (EN 1993-1-10 §2.2):
           T_Ed = T_md,1 + T_md,2 + ... ≈ T₀ − ΔT_r
       (aquí simplificado al término dominante T₀ − ΔT_r, tal como resuelven
       ambas fichas; ΔT_r = 5°C es el valor usado en los ejemplos).

    2. Resistencia reducida por espesor (EN 1993-1-10 Anexo B, ec. B.1):
           f_y(t) = f_y − 0.25 · t   [N/mm², t en mm]

    3. Espesor máximo admisible t_max frente a rotura frágil: interpolación
       LINEAL en la tabla EC3-1-10 (Tabla 2.1 / Anexo B, curvas por subgrado a
       T_Ed dada) en función de la relación de utilización σ_Ed / f_y(t).
       La tabla completa (todas las T_Ed y subgrados) NO está disponible en el
       workspace; este módulo NO la inventa — recibe los puntos calibrados
       como parámetro (`table_points`), tal como los transcriben las fichas
       para el caso S355JR a T_Ed=−40°C: (0.50, 25 mm), (0.75, 15 mm).

No se implementa mecánica de fractura LEFM (K_IC = √(E·G_C), K_d = σ√(πa)):
esa variante aparece en una única ficha (W01399) sin resultado cruzado por
una segunda fuente, así que NO se ancla (regla de oro: no fiarse de una ficha
sola). Si en el futuro aparece un segundo ejemplo LEFM independiente, añadir
como módulo separado.

Referencias de fichas máster: W01468 (Ex Fatigue 2, examen 2020-03-30, UPC —
"Análisis y Proyecto de Estructuras de Acero"), W01469 (misma convocatoria,
transcripción independiente — resultados idénticos, confirma el ejemplo).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

EC3110_DELTA_TR_DEFAULT_C: float = 5.0  # corrección típica usada en W01468/W01469
EC3110_THICKNESS_REDUCTION_PER_MM: float = 0.25  # EC3-1-10 Anexo B, ec. B.1


def reference_temperature(T0_C: float, delta_Tr_C: float = EC3110_DELTA_TR_DEFAULT_C) -> float:
    """Temperatura de referencia T_Ed simplificada (EN 1993-1-10 §2.2).

    T_Ed = T0 − ΔT_r. Las fichas W01468/W01469 resuelven T0=−35°C, ΔT_r=5°C
    → T_Ed=−40°C (término dominante; el Anexo A completo suma más términos
    T_md,i que no están anclados por ningún ejemplo del workspace).

    :param T0_C: temperatura mínima de servicio (°C).
    :param delta_Tr_C: corrección de temperatura (°C, valor positivo que se resta).
    """
    return T0_C - delta_Tr_C


def reduced_yield_strength(
    fy_MPa: float, t_mm: float, reduction_per_mm: float = EC3110_THICKNESS_REDUCTION_PER_MM
) -> float:
    """Resistencia reducida por espesor f_y(t) (EN 1993-1-10 Anexo B, ec. B.1).

    f_y(t) = f_y − 0.25 · t   [N/mm², t en mm].

    :param fy_MPa: límite elástico nominal f_y (MPa).
    :param t_mm: espesor del elemento (mm).
    :param reduction_per_mm: coeficiente de reducción (MPa/mm), 0.25 por defecto.
    """
    if fy_MPa <= 0:
        raise ValueError(f"f_y debe ser > 0 (recibido {fy_MPa})")
    if t_mm < 0:
        raise ValueError(f"t debe ser >= 0 (recibido {t_mm})")
    return fy_MPa - reduction_per_mm * t_mm


def interpolate_max_thickness(
    sigma_over_fy: float, table_points: Sequence[Tuple[float, float]]
) -> float:
    """Espesor máximo admisible t_max (mm) por interpolación lineal en la tabla
    de rotura frágil EC3-1-10 (Tabla 2.1 / Anexo B), para una T_Ed y subgrado
    dados.

    :param sigma_over_fy: relación de utilización σ_Ed / f_y(t) (adimensional).
    :param table_points: puntos calibrados de la tabla ``(ratio, t_max_mm)``,
        al menos 2. No se extrapola fuera del rango cubierto por los puntos.
    :returns: t_max (mm) interpolado linealmente entre los dos puntos que
        acotan ``sigma_over_fy``.
    :raises ValueError: si hay menos de 2 puntos o si ``sigma_over_fy`` cae
        fuera del rango cubierto por ``table_points`` (no se extrapola).
    """
    if len(table_points) < 2:
        raise ValueError("se requieren al menos 2 puntos de tabla para interpolar")
    pts = sorted(table_points, key=lambda p: p[0])
    ratios = [p[0] for p in pts]
    if sigma_over_fy < ratios[0] or sigma_over_fy > ratios[-1]:
        raise ValueError(
            f"sigma/fy={sigma_over_fy:.4f} fuera del rango de la tabla "
            f"[{ratios[0]}, {ratios[-1]}]; no se extrapola"
        )
    for (r0, t0), (r1, t1) in zip(pts, pts[1:]):
        if r0 <= sigma_over_fy <= r1:
            if r1 == r0:
                return t0
            frac = (sigma_over_fy - r0) / (r1 - r0)
            return t0 + frac * (t1 - t0)
    raise ValueError("no se pudo interpolar (revisar table_points)")  # pragma: no cover


@dataclass(frozen=True)
class BrittleFractureResult:
    """Resultado de la verificación EC3-1-10 (rotura frágil por espesor)."""

    fy_t_MPa: float
    sigma_over_fy: float
    t_max_admissible_mm: float
    t_mm: float
    ok: bool
    T_ref_C: float | None = None


def brittle_fracture_check(
    sigma_MPa: float,
    fy_MPa: float,
    t_mm: float,
    table_points: Sequence[Tuple[float, float]],
    *,
    T0_C: float | None = None,
    delta_Tr_C: float = EC3110_DELTA_TR_DEFAULT_C,
) -> BrittleFractureResult:
    """Verificación completa a rotura frágil EN 1993-1-10 (§2, Anexo B).

    Calcula f_y(t) reducida por espesor, la relación de utilización
    σ_Ed/f_y(t), interpola el espesor máximo admisible t_max en la tabla
    calibrada (``table_points``) y compara contra el espesor real t.

    :param sigma_MPa: tensión de diseño σ_Ed en la sección crítica (MPa).
    :param fy_MPa: límite elástico nominal f_y (MPa).
    :param t_mm: espesor real del elemento (mm).
    :param table_points: puntos calibrados ``(ratio, t_max_mm)`` de la tabla
        EC3-1-10 para la T_Ed y subgrado de acero considerados.
    :param T0_C: temperatura mínima de servicio (°C), opcional (solo para
        reportar T_ref en el resultado; no participa en el cálculo de t_max).
    :param delta_Tr_C: corrección de temperatura (°C), ver :func:`reference_temperature`.
    :returns: :class:`BrittleFractureResult` con ``ok = True`` si t ≤ t_max.
    """
    fy_t = reduced_yield_strength(fy_MPa, t_mm)
    ratio = sigma_MPa / fy_t
    t_max = interpolate_max_thickness(ratio, table_points)
    t_ref = reference_temperature(T0_C, delta_Tr_C) if T0_C is not None else None
    return BrittleFractureResult(
        fy_t_MPa=fy_t,
        sigma_over_fy=ratio,
        t_max_admissible_mm=t_max,
        t_mm=t_mm,
        ok=t_mm <= t_max,
        T_ref_C=t_ref,
    )


__all__ = [
    "EC3110_DELTA_TR_DEFAULT_C",
    "EC3110_THICKNESS_REDUCTION_PER_MM",
    "reference_temperature",
    "reduced_yield_strength",
    "interpolate_max_thickness",
    "BrittleFractureResult",
    "brittle_fracture_check",
]
