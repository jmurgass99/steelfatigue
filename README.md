# SteelFatigue

Evaluación de fatiga y rotura frágil en acero estructural según **EN 1993-1-9** y **EN 1993-1-10**, con conteo rainflow, acumulación de daño Palmgren-Miner, fatiga oligocíclica, tensión de punto caliente y propagación de grieta.

[![CI](https://github.com/jmurgass99/steelfatigue/actions/workflows/ci.yml/badge.svg)](https://github.com/jmurgass99/steelfatigue/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Paquete Python puro e independiente: solo depende de `numpy` y `fatpack`.

## Instalación

```bash
pip install git+https://github.com/jmurgass99/steelfatigue.git
```

Extras opcionales:

```bash
pip install "steelfatigue[api] @ git+https://github.com/jmurgass99/steelfatigue.git"    # REST API (FastAPI)
pip install "steelfatigue[memos] @ git+https://github.com/jmurgass99/steelfatigue.git"  # memorias de cálculo (handcalcs)
```

Para desarrollo:

```bash
git clone https://github.com/jmurgass99/steelfatigue.git
cd steelfatigue
pip install -e ".[test,api,memos]"
pytest -q
```

## Inicio rápido

### Daño Palmgren-Miner con la curva trilineal EN 1993-1-9 §7

Ejemplo clásico: viga IPE 240, categoría de detalle 80, método *safe-life* (γ_Mf = 1,15).

```python
from steelfatigue.ec3_sn import palmgren_miner_ec3

spectrum = [
    {"stress_range_MPa": 75.16, "cycles": 1.0e6},
    {"stress_range_MPa": 8.67, "cycles": 2.0e6},   # por debajo del cut-off: no daña
]
res = palmgren_miner_ec3(spectrum, detail=80, gamma_Mf=1.15)

print(res["total_damage"])   # 0.63  -> D <= 1.0, OK
print(res["ok"])             # True
print(res["blocks"][0]["N_i"])  # 1.59e6 ciclos resistentes
```

La curva implementa los tres tramos del Eurocódigo: pendiente m = 3 hasta el límite de amplitud constante Δσ_D (N = 5·10⁶), pendiente m = 5 hasta el cut-off Δσ_L (N = 10⁸) y daño nulo por debajo. El factor parcial γ_Mf se aplica una sola vez, sobre la resistencia de diseño Δσ_C / γ_Mf.

### Ciclos resistentes para un rango de tensión

```python
from steelfatigue.ec3_sn import ec3_cycles_to_failure, constant_amplitude_limit, cutoff_limit

ec3_cycles_to_failure(100.0, detail=112)   # N para Δσ = 100 MPa, FAT 112
constant_amplitude_limit(112)              # Δσ_D ≈ 82.5 MPa
cutoff_limit(112)                          # Δσ_L ≈ 45.3 MPa
```

### Conteo rainflow (ASTM E1049) de un historial de tensiones

```python
from steelfatigue.rainflow_fatpack import rainflow_count

history = [0, 80, -20, 60, 10, 90, -40, 0]
for c in rainflow_count(history):
    print(c.range, c.mean, c.count)   # rango, media y nº de ciclos (0.5 = semiciclo)
```

### Corrección por tensión media

```python
from steelfatigue.mean_stress import equivalent_reversed_stress

equivalent_reversed_stress(sigma_a=60.0, sigma_m=40.0, Su=490.0, criterion="goodman")   # 65.33 MPa
```

## Módulos

| Módulo | Contenido |
|---|---|
| `ec3_sn` | Curva S-N trilineal EN 1993-1-9 §7 y Palmgren-Miner con γ_Mf |
| `ec3_brittle_fracture` | Selección de tenacidad y espesor máximo, EN 1993-1-10 |
| `wohler_db` | Catálogo de categorías de detalle (FAT) |
| `sn_curves`, `sn_curves_multi` | Curvas S-N de pendiente única (AISC / AS / ASME) |
| `rainflow_fatpack` | Conteo rainflow sobre `fatpack` |
| `variable_amplitude` | Daño acumulado desde historial o ciclos contados |
| `mean_stress` | Goodman, Gerber y Soderberg |
| `hotspot` | Tensión de punto caliente (extrapolación lineal y cuadrática, IIW) |
| `notch_stress` | Tensión de entalla (IIW tipo c) |
| `lowcycle` | Fatiga oligocíclica Coffin-Manson |
| `multiaxial` | Criterios multiaxiales |
| `paris_law` | Integración de la ley de Paris (propagación de grieta) |
| `endurance_factors` | Factores de corrección del límite de fatiga |
| `corrosion` | Curvas S-N modificadas por corrosión |
| `gusset_rbs` | Método de Fuerza Uniforme en cartelas y daño en RBS |
| `services/` | Capa de servicio con funciones puras |
| `api/` | REST API con FastAPI (extra `api`) |
| `memos/` | Memorias de cálculo paso a paso con handcalcs (extra `memos`) |

## REST API

```bash
pip install -e ".[api]"
uvicorn steelfatigue.api.app:app --reload
# http://localhost:8000/docs
```

## Validación

Los tests golden de `ec3_sn` y `ec3_brittle_fracture` anclan los resultados a ejemplos resueltos a mano según EN 1993-1-9 (codo Δσ_D y cut-off Δσ_L tabulados, ejemplo Miner con γ_Mf = 1,15), no a reejecuciones de la propia función. El conteo rainflow se valida contra el ejemplo de ASTM E1049. Consulta `docs/QC_CHECKLIST.md` para el alcance de lo verificado.

## Licencia

MIT. Consulta [LICENSE](LICENSE).

---

Parte del toolkit estructural de código abierto **Loadpath**, de [Jesús Murgas](https://github.com/jmurgass99).
