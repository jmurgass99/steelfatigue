# steelfatigue

**Español** · [English](README.en.md)

Fatiga y rotura frágil del acero estructural: EN 1993-1-9 y EN 1993-1-10.

[![CI](https://github.com/jmurgass99/steelfatigue/actions/workflows/ci.yml/badge.svg)](https://github.com/jmurgass99/steelfatigue/actions/workflows/ci.yml)
[![Licencia: MIT](https://img.shields.io/badge/licencia-MIT-green)](LICENSE)

## Qué hace

- Comprobación a fatiga por categoría de detalle con la curva S-N trilineal de EN 1993-1-9 y daño de Palmgren-Miner con γ_Mf.
- Espesor máximo admisible frente a rotura frágil (EN 1993-1-10).
- Desde una historia de tensiones: conteo rainflow (ASTM E1049), corrección por tensión media, tensión de punto caliente y de entalla (IIW), propagación de grieta (Paris) y fatiga oligocíclica (Coffin-Manson).
- Curvas S-N de AISC 360 y AS 4100 para comparar.

## Instalación

```bash
pip install git+https://github.com/jmurgass99/steelfatigue.git
```

Extras opcionales: `api`, `memos`. Python puro, sin estado global.

## Ejemplo

Ciclos resistentes de un detalle de categoría 160 con Δσ = 80 MPa:

```python
from steelfatigue.ec3_sn import ec3_cycles_to_failure
from steelfatigue.wohler_db import list_fat_categories

detalle = list_fat_categories()[0]                   # categoría 160
print(f"{ec3_cycles_to_failure(80.0, detalle):.3e}")   # 3.474e+07
```

Más casos en [`examples/`](examples).

## Qué no hace

- Obtener tensiones desde geometría y cargas: no hay modelo de barras ni de secciones.
- El método de los coeficientes de daño equivalente λ de EN 1993-2 o EN 1993-6 (puentes, vigas carrileras).
- Las Tablas 8.1 a 8.10 de EN 1993-1-9: el catálogo tiene 12 categorías con una descripción corta; la asignación final es tuya.
- La Tabla 2.1 completa de EN 1993-1-10: la función recibe los puntos del subgrado y no extrapola.

El detalle está en [docs/LIMITACIONES.md](docs/LIMITACIONES.md).

## Pruebas

```bash
pip install -e ".[test]"
pytest -q
```

## Licencia

MIT. Ver [LICENSE](LICENSE). Autor: [Jesús Murgas](https://github.com/jmurgass99).
