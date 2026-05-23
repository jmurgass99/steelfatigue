# FatigueJm

Analisis de fatiga estructural

[![CI](https://github.com/jmurgass99/fatiguejm/actions/workflows/ci.yml/badge.svg)](https://github.com/jmurgass99/fatiguejm/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-71.43%25-green?style=flat)](https://github.com/jmurgass99/fatiguejm)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red)]()

## Overview

Analisis de fatiga estructural. Parte del ecosistema **jmurgass99** de herramientas de ingenieria estructural.

## Installation

```bash
git clone https://github.com/jmurgass99/fatiguejm.git
cd fatiguejm
pip install -e .
# Optional extras:
pip install -e ".[test,api]"
```

## Quick start

```python
from fatiguejm import *  # see examples/ for usage
```

## REST API (if available)

```bash
uvicorn fatiguejm.api.app:app --reload
# Open http://localhost:8000/docs
```

## Testing

```bash
pytest -q                                # quick suite
pytest -m "not slow"                     # exclude slow tests
.\scripts\run_coverage.ps1               # coverage with gate
```

## Project structure

```
fatiguejm/
  services/       # service layer (pure functions)
  api/            # FastAPI app (REST endpoints)
  exceptions.py   # typed exception hierarchy
  _brand.py       # brand constants
tests/            # pytest suite
```

## Ecosystem

This project is part of the **jmurgass99 structural engineering ecosystem**:

- [fastsap](https://github.com/jmurgass99/fastsap) - orquestador SAP2000/ETABS
- [dynamicsjmpro](https://github.com/jmurgass99/dynamicsjmpro) - SaaS frontend + backend
- [dynamicsjm](https://github.com/jmurgass99/dynamicsjm) - motor dinamico
- [foundationdesignjm](https://github.com/jmurgass99/foundationdesignjm) - cimentaciones
- [windloadjm](https://github.com/jmurgass99/windloadjm) - cargas de viento
- [seismicrecordsjm](https://github.com/jmurgass99/seismicrecordsjm) - records sismicos
- [slopestabilityjm](https://github.com/jmurgass99/slopestabilityjm) - estabilidad de taludes
- [steelconnectionjm](https://github.com/jmurgass99/steelconnectionjm) - conexiones de acero
- [steeloptimizerjm](https://github.com/jmurgass99/steeloptimizerjm) - optimizacion GA
- [coldformedjm](https://github.com/jmurgass99/coldformedjm) - acero conformado en frio
- [fatiguejm](https://github.com/jmurgass99/fatiguejm) - analisis de fatiga
- [firesteeljm](https://github.com/jmurgass99/firesteeljm) - analisis termico al fuego
- [dxfstructuraljm](https://github.com/jmurgass99/dxfstructuraljm) - generacion DXF


## Master IEG Integrations

Modulo `fatiguejm.gusset_rbs` (integrado 2026-05-19 desde
`NEW CODES/STRUCTURAL/Master_IEG_Integrations/fatigue_gusset_rbs.py`):

- `FatigueGussetUFM` — Metodo de Fuerza Uniforme (IEG 3240) para fuerzas
  en interfaces viga/columna/gusset. Salida lista para combinar con SCF
  + curvas S-N de `sn_curves_multi`.
- `FatigueRBS.calculate_oligocyclic_damage` — dano Coffin-Manson
  (Engelhardt) sobre historial de rotaciones plasticas. Complementa
  `fatiguejm.lowcycle`.

```python
from fatiguejm.gusset_rbs import FatigueGussetUFM, FatigueRBS
g = FatigueGussetUFM(alpha=15, beta=20, ec=5, eb=5)
print(g.calculate_interface_forces(P_brace=1000, theta=0.785))
```

## License

Proprietary - (c) 2026 jmurgass99. All rights reserved.
