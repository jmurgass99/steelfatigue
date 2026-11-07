# steelfatigue

[Español](README.md) · **English**

Fatigue and brittle fracture of structural steel: EN 1993-1-9 and EN 1993-1-10.

[![CI](https://github.com/jmurgass99/steelfatigue/actions/workflows/ci.yml/badge.svg)](https://github.com/jmurgass99/steelfatigue/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## What it does

- Fatigue check by detail category with the EN 1993-1-9 trilinear S-N curve and Palmgren-Miner damage with γ_Mf.
- Maximum allowable thickness against brittle fracture (EN 1993-1-10).
- From a stress history: rainflow counting (ASTM E1049), mean-stress correction, hot-spot and notch stress (IIW), crack growth (Paris) and low-cycle fatigue (Coffin-Manson).
- AISC 360 and AS 4100 S-N curves for comparison.

## Install

```bash
pip install git+https://github.com/jmurgass99/steelfatigue.git
```

Optional extras: `api`, `memos`. Pure Python, no global state.

## Example

Cycles to failure of a category 160 detail at Δσ = 80 MPa:

```python
from steelfatigue.ec3_sn import ec3_cycles_to_failure
from steelfatigue.wohler_db import list_fat_categories

detail = list_fat_categories()[0]                    # category 160
print(f"{ec3_cycles_to_failure(80.0, detail):.3e}")    # 3.474e+07
```

More cases in [`examples/`](examples).

## What it does not do

- Obtain stresses from geometry and loads: there is no member or section model.
- The equivalent damage factor (λ) method of EN 1993-2 or EN 1993-6 (bridges, crane girders).
- EN 1993-1-9 Tables 8.1 to 8.10: the catalog has 12 categories with a short description; the final assignment is yours.
- The full Table 2.1 of EN 1993-1-10: the function takes the subgrade points and does not extrapolate.

Details are in [docs/LIMITACIONES.md](docs/LIMITACIONES.md) (in Spanish).

## Tests

```bash
pip install -e ".[test]"
pytest -q
```

## License

MIT. See [LICENSE](LICENSE). Author: [Jesús Murgas](https://github.com/jmurgass99).
