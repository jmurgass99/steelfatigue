# steelfatigue — fatigue and brittle fracture of structural steel (EN 1993-1-9 and EN 1993-1-10)

[Español](README.md) · **English** · [Português](README.pt.md) · [Italiano](README.it.md)

Fatigue checks of structural steel details by detail category with the trilinear S-N curve of EN 1993-1-9 and Palmgren-Miner damage with γ_Mf; maximum permissible thickness against brittle fracture to EN 1993-1-10; and the full path from a measured or simulated stress history: rainflow counting (ASTM E1049), mean-stress correction, hot-spot and notch stress (IIW), crack growth (Paris) and low-cycle fatigue (Coffin-Manson). Pure Python, no global state, with the functions anchored to worked examples solved by hand.

[![CI](https://github.com/jmurgass99/steelfatigue/actions/workflows/ci.yml/badge.svg)](https://github.com/jmurgass99/steelfatigue/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## What problem it solves

You have a spectrum of stress ranges (or a history σ(t)) at a welded or bolted detail and need to know how many cycles it withstands, how much damage it accumulates over its design life, and which detail category or thickness you need. The package does that part: the resistance curve, the cycle counting and the damage accumulation. You bring the stresses, from your model or your measurements.

**Use it when**

- you check an EN 1993-1-9 detail against a block spectrum {Δσ, n} with a γ_Mf from Table 3.1;
- you start from a stress history (sensor, dynamic analysis, moving loads) and want to reach the damage with rainflow and, if needed, a mean-stress correction;
- you have shell-model readings at t/2 and 3t/2 from a weld toe and need the IIW hot-spot stress;
- you want the maximum permissible thickness against brittle fracture of an S355 member at low temperature, with the EN 1993-1-10 Table 2.1 points entered by hand;
- you screen the residual life of a detected crack (Paris) or the low-cycle damage of an RBS connection under a seismic protocol.

**Don't use it for**

- obtaining stresses from geometry and loads: there is no frame or section model;
- the damage-equivalent factor λ method of EN 1993-2 or EN 1993-6 (bridges, crane runway girders): not implemented;
- looking up Tables 8.1 to 8.10 of EN 1993-1-9: the package catalogue holds 12 categories with a short description, and the final assignment is yours;
- the full Table 2.1 of EN 1993-1-10: the function takes the (ratio, t_max) points for the subgrade and temperature that apply to you and does not extrapolate beyond them;
- reducing the compressive part of the range to 60 % in non-welded details (EN 1993-1-9 §7.2.1(1)): not implemented;
- fracture mechanics with K_IC and flaw size for the brittle-fracture verdict: only the thickness method of EN 1993-1-10.

## Installation

```bash
pip install git+https://github.com/jmurgass99/steelfatigue.git
pip install "steelfatigue[api,memos] @ git+https://github.com/jmurgass99/steelfatigue.git"   # REST API and handcalcs reports
```

Dependencies: `numpy` and `fatpack`. For development: `git clone`, `pip install -e ".[test,api,memos]"`, `pytest -q` (27 test files). On Windows, if the console is not UTF-8, run the examples with `python -X utf8 examples/<name>.py`.

## Capabilities

| Capability | Modules | Code or reference | Use cases |
|---|---|---|---|
| Fatigue by detail category: trilinear S-N curve (m = 3/5, knee at 5·10⁶, cut-off at 10⁸), Palmgren-Miner with γ_Mf, FAT catalogue | `ec3_sn`, `wohler_db`, `sn_curves` | EN 1993-1-9 §7.1, §3 Table 3.1, §A.6 | [6 cases](#1-fatigue-by-detail-category-en-1993-1-9) |
| Brittle fracture: T_Ed, f_y(t) reduced for thickness, t_max interpolated in the subgrade table | `ec3_brittle_fracture` | EN 1993-1-10 §2.2, Annex B eq. B.1, Table 2.1 | [5 cases](#2-brittle-fracture-by-thickness-en-1993-1-10) |
| From stress history to damage: rainflow, mean stress (Goodman, Gerber, Soderberg, ASME, Langer), variable amplitude, equivalent range | `rainflow_fatpack`, `variable_amplitude`, `mean_stress` | ASTM E1049-85 §5.4.4, Shigley §6-12, AISC 360-22 App. 3 | [5 cases](#3-from-stress-history-to-damage) |
| Local stresses in welds: IIW hot spot (linear and quadratic), effective notch FAT 225, thickness factor, environmental factors, AISC/AS/ASME curves | `hotspot`, `services.hotspot_service`, `notch_stress`, `corrosion`, `sn_curves_multi` | IIW XIII-2151-07 (Hobbacher 2008) §2.2.3 and §2.2.4, EN 1993-1-9 §7.2.1, AISC 360-22 App. 3, AS 4100 §11, ASME VIII-2 | [5 cases](#4-local-stresses-in-welds-and-s-n-curves-of-other-codes) |
| Component and low-cycle fatigue: Marin factors, Smith-Watson-Topper with critical plane, Paris law, Coffin-Manson in RBS, UFM forces in gusset plates | `endurance_factors`, `multiaxial`, `paris_law`, `lowcycle`, `gusset_rbs` | Shigley §6-9 to §6-18, SWT 1970, Paris-Erdogan 1963 with Barsom-Rolfe C, Engelhardt 2007 / FEMA 350, AISC Manual Part 13 | [5 cases](#5-component-fatigue-crack-growth-and-low-cycle-fatigue) |
| Calculation reports (Markdown and LaTeX) and REST API | `memos`, `api` | — | [3 cases](#6-calculation-reports-and-rest-api) |

The 29 scripts in `examples/` were run in a clean environment before publishing; their output is in `examples/output/` and is what is reproduced here.

## Use cases

The outputs are reproduced exactly as the scripts print them, in Spanish.

### 1. Fatigue by detail category (EN 1993-1-9)

#### Crane runway girder: damage by detail category and γ_Mf

A 50-year service spectrum evaluated for six FAT categories and the three γ_Mf of Table 3.1. It helps decide which construction detail is admissible before drawing the weld.

<details><summary>Actual output of <code>python examples/crane_runway_girder_miner_by_detail_category_en1993_1_9.py</code></summary>

```text
Daño acumulado D = Σ n_i/N_i (D <= 1 cumple)

  FAT | γ_Mf=1.00 | γ_Mf=1.15 | γ_Mf=1.35
--------------------------------------------
  160 |    0.012   |    0.033   |    0.068  
  112 |    0.084   |    0.143   |    0.321  
   90 |    0.196   |    0.396   |    0.681  
   71 |    0.550   |    0.889   |    1.569 ✗
   56 |    1.253 ✗ |    2.293 ✗ |    3.900 ✗
   36 |    6.207 ✗ |    9.918 ✗ |   17.091 ✗

Detalle FAT 71, γ_Mf = 1,15:
  Δσ =  120.0 MPa  n = 2.00e+04  N = 2.72e+05  daño = 0.0734
  Δσ =   90.0 MPa  n = 1.50e+05  N = 6.46e+05  daño = 0.2323
  Δσ =   60.0 MPa  n = 8.00e+05  N = 2.18e+06  daño = 0.3671
  Δσ =   35.0 MPa  n = 4.00e+06  N = 1.85e+07  daño = 0.2157
  Δσ =   20.0 MPa  n = 2.00e+07  N = ∞  daño = 0.0000
  D total = 0.889  →  CUMPLE
```

</details>

#### IPE 500 beam with a cantilever under two repeated loads: fatigue at two sections

Problem from the UPC exam of 2020-03-30 (records W01468/W01469 of the master's course extraction). The same category 80 passes at midspan and fails at the cantilever root: the fatigue-critical section is decided by the stress range per cycle, not by the static moment. Record results: N_B = 13 811, D_B = 0.40, D_C = 1.07.

<details><summary>Actual output of <code>python examples/ipe500_cantilever_beam_two_sections_exam_w01468.py</code></summary>

```text
IPE 500, W_el,y = 1928.1 cm³; categoría 80, γ_Mf = 1.35
Δσ_C,d = 59.26 MPa

σ1,B = 207.46 MPa (P1 en vano), σ2,B = 103.73 MPa (P2 en voladizo)

1) P1 = P2 = 200 kN alternadas, sección B, 10 000 ciclos
  Δσ =  311.19 MPa   n =     10000   N =       13811   n/N = 0.7240
  D = 0.724  →  VERIFICA

2) P1 = 100 kN × 1e5 y P2 = 200 kN × 5e4, sección B
  Δσ =  103.73 MPa   n =    100000   N =      372904   n/N = 0.2682
  Δσ =  103.73 MPa   n =     50000   N =      372904   n/N = 0.1341
  D = 0.402  →  VERIFICA

3) P2 = 200 kN × 5e4, sección C
  Δσ =  207.46 MPa   n =     50000   N =       46613   n/N = 1.0727
  D = 1.073  →  NO VERIFICA

La misma categoría de detalle verifica en B y falla en C: la sección crítica a fatiga no es la de mayor momento estático sino la de mayor rango y ciclos.
```

</details>

#### Admissible load for a required life (inverted S-N curve)

Exercise 7b of the master's course (record W01508): which load exactly exhausts 500 000 cycles in a category 80 detail and in a category 36 one. Solved by bisection on the trilinear curve and checked against the closed form of the m = 3 branch. Record result: 376.3 kN and 102.4 kN.

<details><summary>Actual output of <code>python examples/admissible_load_for_required_life_exam_w01508.py</code></summary>

```text
Vida requerida N = 500,000 ciclos, γ_Mf = 1.35

Apoyo interior, soldadura transversal (cat. 80)
  Δσ_C,d = 59.26 MPa, codo Δσ_D,d = 43.66 MPa
  Δσ admisible = 94.07 MPa (tramo m = 3); forma cerrada m=3: 94.07 MPa
  P admisible  = 376.3 kN

Conexión a un solo lado (cat. 36)
  Δσ_C,d = 26.67 MPa, codo Δσ_D,d = 19.65 MPa
  Δσ admisible = 42.33 MPa (tramo m = 3); forma cerrada m=3: 42.33 MPa
  P admisible  = 102.4 kN

Gobierna la categoría 36: P = 102.4 kN frente a 376.3 kN (27% de la carga del detalle de categoría 80).
```

</details>

#### Railway bridge stringer: life in years from the daily train spectrum

Damage per day with the trilinear curve, life as 1/(D·365) and damage split by block. It compares a transverse butt splice (71) with a continuous longitudinal weld (112): the better category multiplies the life by ten.

<details><summary>Actual output of <code>python examples/railway_bridge_stringer_life_from_daily_train_spectrum.py</code></summary>

```text

Detalle: empalme a tope transversal (categoría 71)
  γ_Mf = 1.00 (tolerante al daño, consecuencia baja): D/día = 1.038e-04  vida =       26 años  → NO cumple (100 años)
  γ_Mf = 1.15 (vida segura, consecuencia baja): D/día = 1.693e-04  vida =       16 años  → NO cumple (100 años)
  γ_Mf = 1.35 (vida segura, consecuencia alta): D/día = 2.996e-04  vida =        9 años  → NO cumple (100 años)
  Reparto del daño por bloque (γ_Mf = 1,35):
    Δσ =  72.0 MPa  n/día =    40  N =  7.79e+05   17.1% del daño
    Δσ =  52.0 MPa  n/día =   320  N =  2.07e+06   51.6% del daño
    Δσ =  34.0 MPa  n/día =   900  N =  9.62e+06   31.2% del daño
    Δσ =  19.0 MPa  n/día =  2400  N =         ∞    0.0% del daño

Detalle: cordón longitudinal continuo (categoría 112)
  γ_Mf = 1.00 (tolerante al daño, consecuencia baja): D/día = 1.040e-05  vida =      263 años  → cumple (100 años)
  γ_Mf = 1.15 (vida segura, consecuencia baja): D/día = 2.087e-05  vida =      131 años  → cumple (100 años)
  γ_Mf = 1.35 (vida segura, consecuencia alta): D/día = 5.117e-05  vida =       54 años  → NO cumple (100 años)
  Reparto del daño por bloque (γ_Mf = 1,35):
    Δσ =  72.0 MPa  n/día =    40  N =  3.06e+06   25.6% del daño
    Δσ =  52.0 MPa  n/día =   320  N =  1.12e+07   55.7% del daño
    Δσ =  34.0 MPa  n/día =   900  N =  9.39e+07   18.7% del daño
    Δσ =  19.0 MPa  n/día =  2400  N =         ∞    0.0% del daño
```

</details>

#### Knee, cut-off and m = 5 branch of each category against a single m = 3 line

Table of Δσ_D and Δσ_L from the catalogue (matching the UPC notes, record W01419) and how far off a single-slope line is in the m = 5 branch and below the cut-off. It explains when to use `ec3_sn` and when `FatigueEvaluator` is enough.

<details><summary>Actual output of <code>python examples/sn_curve_knee_cutoff_table_vs_single_slope.py</code></summary>

```text
     FAT  Δσ_D [MPa]  Δσ_L [MPa] |  Δσ=0,9·Δσ_D  N trilineal  N recta m=3  ratio
----------------------------------------------------------------------------------
 FAT 160       117.9        64.8 |        106.1    8.468e+06    6.859e+06   1.23
 FAT 140       103.2        56.7 |         92.8    8.468e+06    6.859e+06   1.23
 FAT 125        92.1        50.6 |         82.9    8.468e+06    6.859e+06   1.23
 FAT 112        82.5        45.3 |         74.3    8.468e+06    6.859e+06   1.23
 FAT 100        73.7        40.5 |         66.3    8.468e+06    6.859e+06   1.23
  FAT 90        66.3        36.4 |         59.7    8.468e+06    6.859e+06   1.23
  FAT 80        58.9        32.4 |         53.1    8.468e+06    6.859e+06   1.23
  FAT 71        52.3        28.7 |         47.1    8.468e+06    6.859e+06   1.23
  FAT 63        46.4        25.5 |         41.8    8.468e+06    6.859e+06   1.23
  FAT 50        36.8        20.2 |         33.2    8.468e+06    6.859e+06   1.23
  FAT 45        33.2        18.2 |         29.8    8.468e+06    6.859e+06   1.23
  FAT 36        26.5        14.6 |         23.9    8.468e+06    6.859e+06   1.23

Por debajo del cut-off la curva trilineal no acumula daño; la recta única sí:
  FAT 90, Δσ = 32.8 MPa (< Δσ_L = 36.4): N trilineal = inf,  N recta m=3 = 4.139e+07

Usa `ec3_sn` para EN 1993-1-9; `FatigueEvaluator` queda para espectros de alta tensión donde todo cae en el tramo m = 3 o para normas de pendiente única.
```

</details>

#### Choosing the detail category from the catalogue

Keyword search, lookup by code and life of each category for the same range. The descriptions are summaries; the final assignment is made with Tables 8.1 to 8.10 of the code.

<details><summary>Actual output of <code>python examples/select_detail_category_from_catalogue.py</code></summary>

```text
Catálogo FAT (EN 1993-1-9):
   FAT 160  Acero base, sin soldadura                        N(Δσ=100) = 1.14e+07
   FAT 140  Soldadura a tope longitudinal continuo           N(Δσ=100) = 5.84e+06
   FAT 125  Soldadura a tope transversal calidad B           N(Δσ=100) = 3.91e+06
   FAT 112  Cordón a tope con plancha respaldo               N(Δσ=100) = 2.81e+06
   FAT 100  Soldadura cruciforme con full penetration        N(Δσ=100) = 2.00e+06
    FAT 90  Soldadura de filete + transverse stiffener       N(Δσ=100) = 1.46e+06
    FAT 80  Soldadura filete longitudinal                    N(Δσ=100) = 1.02e+06
    FAT 71  Soldadura a tope transversal con offset          N(Δσ=100) = 7.16e+05
    FAT 63  Pernos pretensados ASTM A325/A490                N(Δσ=100) = 5.00e+05
    FAT 50  Soldadura a corte filete con carga               N(Δσ=100) = 2.50e+05
    FAT 45  Pernos no pretensados a corte                    N(Δσ=100) = 1.82e+05
    FAT 36  Detalles severos / áreas de concentración        N(Δσ=100) = 9.33e+04

Búsqueda «atiesador»: FAT 90, FAT 80

Búsqueda «tope»: FAT 140, FAT 125, FAT 112, FAT 71

Búsqueda «perno»: FAT 63, FAT 45

lookup_fat('fat 71') → FAT 71: Soldadura a tope transversal con offset / Empalmes simples
lookup_fat('FAT 999') → None
```

</details>

### 2. Brittle fracture by thickness (EN 1993-1-10)

#### IPE 500 flange in S355JR at −35 °C: maximum permissible thickness

Brittle-fracture part of the same exam (records W01468/W01469): T_Ed = T₀ − ΔT_r = −40 °C, f_y(t) = f_y − 0.25·t, linear interpolation between the two Table 2.1 points transcribed by the records for S355JR at −40 °C. Record result: t_max ≈ 21.4 mm > 16 mm.

<details><summary>Actual output of <code>python examples/brittle_fracture_ipe500_s355jr_minus35c_exam_w01468.py</code></summary>

```text
σ_Ed = 207.46 N/mm² (M = 400 kN·m, W_el,y = 1928.1 cm³)
T_Ed = -40 °C (T₀ = -35 °C, ΔT_r = 5 °C)
f_y(t) = 351.0 N/mm² (f_y − 0,25·t, Anexo B)

σ_Ed / f_y(t) = 0.591
t_max admisible (interpolado en la tabla S355JR, T_Ed = -40 °C) = 21.4 mm
t_f = 16.0 mm  →  VERIFICA
```

</details>

#### Plate girder: choosing the flange thickness for service at −35 °C

Sweep of candidate thicknesses with the stress estimated from the flange couple. When the utilisation falls outside the available table points the package says so and does not extrapolate: more Table 2.1 points must be supplied.

<details><summary>Actual output of <code>python examples/brittle_fracture_plate_girder_flange_thickness_choice.py</code></summary>

```text
M_Ed = 1800 kN·m, ala 400 mm, alma 1200 mm, S355JR, T₀ = -35 °C

 t [mm]     σ_Ed   f_y(t)  ratio   t_max  veredicto
   12.0    309.4    352.0  0.879       —  ratio por encima de los puntos de tabla: sigma/fy=0.8790 fuera del rango de la tabla [0.5, 0.75]; no se extrapola
   15.0    246.9    351.2  0.703    16.9  OK
   18.0    205.3    350.5  0.586    21.6  OK
   20.0    184.4    350.0  0.527    23.9  OK
   25.0    146.9    348.8  0.421       —  ratio por debajo de los puntos de tabla: sigma/fy=0.4213 fuera del rango de la tabla [0.5, 0.75]; no se extrapola
```

</details>

#### Sensitivity of the permissible thickness to the stress level

For a 20 mm flange, the σ_Ed beyond which it stops passing. It includes the limiting ratio solved from the interpolation line.

<details><summary>Actual output of <code>python examples/brittle_fracture_stress_level_sensitivity.py</code></summary>

```text
S355JR, t = 20 mm, f_y(t) = 350.0 N/mm², T_Ed = −40 °C

σ_Ed [MPa]  ratio t_max [mm]  t = 20 mm
       175  0.500       25.0  OK
       185  0.529       23.9  OK
       195  0.557       22.7  OK
       205  0.586       21.6  OK
       215  0.614       20.4  OK
       225  0.643       19.3  NO
       235  0.671       18.1  NO
       245  0.700       17.0  NO
       255  0.729       15.9  NO
       265  0.757          —  ratio > 0,75: fuera de los puntos de tabla, no se extrapola

Ratio límite para t = 20 mm: 0.625 → σ_Ed,lim = 218.8 N/mm²
Comprobación: t_max(0.625) = 20.00 mm
```

</details>

#### Thick plates: effect of the Annex B f_y(t) reduction

From 10 to 100 mm the 0.25 N/mm² per millimetre reduction raises the utilisation and lowers t_max while the actual thickness grows: in thick plates both effects add up.

<details><summary>Actual output of <code>python examples/brittle_fracture_thick_plate_reduced_yield.py</code></summary>

```text
σ_Ed = 190 N/mm², S355JR

 t [mm]   f_y(t)   ratio  t_max [mm]  espesor real frente a t_max
     10    352.5   0.539        23.4  OK
     20    350.0   0.543        23.3  OK
     30    347.5   0.547        23.1  NO
     40    345.0   0.551        23.0  NO
     60    340.0   0.559        22.6  NO
     80    335.0   0.567        22.3  NO
    100    330.0   0.576        22.0  NO
```

</details>

#### Batch check of the members of a building in a cold region

List of members with their thickness and stress, verdict per row and count. Rows outside the table range are flagged instead of receiving an invented number.

<details><summary>Actual output of <code>python examples/brittle_fracture_batch_check_members.py</code></summary>

```text
S355JR, T₀ = -35 °C → T_Ed = −40 °C

Elemento                     t   σ_Ed  ratio  t_max  veredicto
Ala viga carrilera          16    207  0.590   21.4  OK
Platabanda inferior         22    185  0.529   23.8  OK
Chapa de nudo celosía       25    180  0.516   24.4  NO VERIFICA
Alma del pilar              12    230  0.653   18.9  OK
Cartela de apoyo            30    150  0.432      —  fuera de los puntos de tabla

3 verifican, 1 no verifican, 1 sin veredicto por falta de puntos de tabla.
```

</details>

### 3. From stress history to damage

#### Signal of the ASTM E1049-85 §5.4.4 example

The count reproduces the table of the standard (range 3: 0.5; 4: 1.5; 6: 0.5; 8: 1.0; 9: 0.5). Until this version the residue was walked two by two and three of the six half cycles were lost, including the largest range; this is fixed and pinned by a test.

<details><summary>Actual output of <code>python examples/rainflow_astm_e1049_example_signal.py</code></summary>

```text
Ciclos devueltos por rainflow_count:
  rango =  4.1  media =   1.0  count = 1.0
  rango =  3.1  media =  -0.5  count = 0.5
  rango =  4.1  media =  -1.0  count = 0.5
  rango =  8.0  media =   1.0  count = 0.5
  rango =  9.0  media =   0.5  count = 0.5
  rango =  8.0  media =   0.0  count = 0.5
  rango =  6.0  media =   1.0  count = 0.5

Rango → ciclos (paquete)  |  tabla ASTM E1049
   3 →  0.5  |   0.5
   4 →  1.5  |   1.5
   6 →  0.5  |   0.5
   8 →  1.0  |   1.0
   9 →  0.5  |   0.5

Total ciclos: paquete 4.0, ASTM 4.0

Versión vectorizada: 7 entradas, rango máximo 9.0, Σ counts = 4.0
Conteo exacto en float64 (use_float64_exact=True): 4.0 ciclos; coincide con fatpack en esta señal de enteros (los rangos redondeados al entero; la cuantización en 64 niveles de fatpack aparece cuando los valores no caen en su malla)
```

</details>

#### Footbridge: from one measured day of history to damage in 50 years

History σ(t) → rainflow → range spectrum → Miner with the trilinear curve → extrapolation to the design life and list of the most damaging ranges.

<details><summary>Actual output of <code>python examples/footbridge_measured_history_rainflow_to_damage.py</code></summary>

```text
Historial: 20000 puntos, σ entre -24.0 y 143.0 MPa
Ciclos rainflow extraídos: 2588 (semiciclos cuentan 0.5)

Daño por día (FAT 80, γ_Mf = 1.15): D = 4.310e-04
Daño en 50 años:               D = 7.866
→ NO CUMPLE. Vida estimada: 6.4 años

Rangos más dañinos:
  Δσ =  167.0 MPa  n/día =    0.5  daño/día = 3.46e-06
  Δσ =   93.9 MPa  n/día =    1.0  daño/día = 1.23e-06
  Δσ =   93.9 MPa  n/día =    1.0  daño/día = 1.23e-06
  Δσ =   93.9 MPa  n/día =    1.0  daño/día = 1.23e-06
  Δσ =  117.4 MPa  n/día =    0.5  daño/día = 1.20e-06
```

</details>

#### Crane girder: mean-stress correction on a history with self-weight

The same history evaluated with Goodman, with Gerber and centred on zero, on AISC 360-22 category C. It quantifies how much the tensile mean stress adds to the damage.

<details><summary>Actual output of <code>python examples/crane_girder_history_mean_stress_correction_aisc_category.py</code></summary>

```text
Historia: 12000 puntos, σ ∈ [35.6, 128.5] MPa, media 85.8 MPa
Curva: AISC cat. C, Δσ_C = 69.0 MPa, m = 3

Goodman, historia real
  ciclos contados = 3151, D/hora = 1.090e-04, D/año = 3.269e-01, vida = 3 años (NO cumple 50 años)
  ciclo más dañino: Δσ_eq = 111.6 MPa, N = 4.73e+05
Gerber, historia real
  ciclos contados = 3151, D/hora = 7.919e-05, D/año = 2.376e-01, vida = 4 años (NO cumple 50 años)
  ciclo más dañino: Δσ_eq = 94.5 MPa, N = 7.78e+05
Goodman, historia centrada (media 0)
  ciclos contados = 3151, D/hora = 7.495e-05, D/año = 2.249e-01, vida = 4 años (NO cumple 50 años)
  ciclo más dañino: Δσ_eq = 91.4 MPa, N = 8.60e+05
```

</details>

#### Machinery support bracket: safety factors in the Haigh diagram

Modified Goodman, Gerber, Soderberg, ASME elliptic and Langer for the same pair (σ_a, σ_m), and the equivalent fully reversed stress to enter an S-N curve with R = −1.

<details><summary>Actual output of <code>python examples/haigh_diagram_safety_factors_machine_support_bracket.py</code></summary>

```text
σ_a = 60.0 MPa, σ_m = 40.0 MPa, S_e = 200.0, S_u = 490.0, S_y = 355.0 MPa

Factor de seguridad n por criterio (n < 1 → fallo previsto):
  goodman        n =  2.620
  gerber         n =  3.117
  soderberg      n =  2.423
  asme_elliptic  n =  3.120
  langer         n =  3.550

Tensión equivalente totalmente alternada σ_ar (R = −1):
  goodman    σ_ar =  65.33 MPa  (+8.9% sobre σ_a)
  gerber     σ_ar =  60.40 MPa  (+0.7% sobre σ_a)
  soderberg  σ_ar =  67.62 MPa  (+12.7% sobre σ_a)

Con media de compresión no hay penalización:
  σ_m = −40 MPa → σ_ar = 60.00 MPa
```

</details>

#### Wind turbine tower: damage-equivalent load (DEL) from rainflow

It extrapolates the 10-minute count to 20 years, computes the DEL for m = 3 and N_ref = 10⁷ and checks that a single block reproduces the damage of the full spectrum on a single-slope line. With the trilinear curve of EN 1993-1-9 most of the small cycles fall below the cut-off.

<details><summary>Actual output of <code>python examples/wind_turbine_tower_damage_equivalent_range_from_rainflow.py</code></summary>

```text
Ventana de 10 min: 2382 ciclos rainflow, Δσ máx = 44.7 MPa, Σn = 2376.5
Extrapolación a 20 años: 1051200 ventanas, Σn = 2.498e+09 ciclos

Δσ_eq (m = 3, N_ref = 1e+07, 20 años) = 61.24 MPa
Daño del espectro completo (recta m = 3, sin cut-off) = 3.2077
Daño del bloque equivalente                          = 3.2077  (diferencia relativa 6.7e-16)

Mismo espectro con la curva trilineal EN 1993-1-9 (FAT 71, γ_Mf = 1): D = 0.3599; 2373 de 2382 niveles quedan bajo el cut-off y no dañan.
```

</details>

### 4. Local stresses in welds and S-N curves of other codes

#### IIW hot-spot stress from shell-model readings

Linear (type a) and quadratic (type b) extrapolation to the weld toe of a 20 mm plate and life estimated by the service with FAT 100 and FAT 90.

<details><summary>Actual output of <code>python examples/hot_spot_stress_iiw_from_fem_readings_tubular_joint.py</code></summary>

```text
Lecturas FEM: σ(t/2) = 142.0, σ(3t/2) = 118.0, σ(5t/2) = 104.0 MPa
σ_hs lineal (tipo a)    = 158.1 MPa
σ_hs cuadrática (tipo b) = 168.4 MPa  (+6.5% frente a la lineal)

FAT 100 (cordón no portante), linear   : σ_hs =  158.1 MPa, N ≈ 3.33e+05 ciclos (γ_Mf = 1,15, recta m = 3)
FAT 100 (cordón no portante), quadratic: σ_hs =  168.4 MPa, N ≈ 2.75e+05 ciclos (γ_Mf = 1,15, recta m = 3)
FAT 90 (cordón portante), linear   : σ_hs =  158.1 MPa, N ≈ 2.43e+05 ciclos (γ_Mf = 1,15, recta m = 3)
FAT 90 (cordón portante), quadratic: σ_hs =  168.4 MPa, N ≈ 2.01e+05 ciclos (γ_Mf = 1,15, recta m = 3)

FAT 90 lineal con la curva trilineal de EN 1993-1-9 (use_trilinear_ec3=True): N ≈ 2.43e+05 frente a 2.43e+05 con la recta m = 3 (iguales: el rango está por encima del codo de 5·10⁶)
```

</details>

#### Hot spot when the mesh has no nodes at t/2 and 3t/2

Interpolation between the available nodes to obtain σ(t/2) and σ(3t/2), compared with direct extrapolation from the nodes closest to the weld, which picks up the notch peak.

<details><summary>Actual output of <code>python examples/hot_spot_from_arbitrary_fem_node_distances.py</code></summary>

```text
Lecturas FEM (distancia al pie del cordón → tensión):
    4.0 mm →  171.0 MPa
    8.0 mm →  152.0 MPa
   14.0 mm →  134.0 MPa
   22.0 mm →  125.0 MPa
   35.0 mm →  112.0 MPa

σ(t/2 = 10 mm) interpolada  = 146.0 MPa
σ(3t/2 = 30 mm) interpolada = 117.0 MPa
σ_hs IIW lineal sobre esas dos lecturas = 165.4 MPa
σ_hs extrapolando los dos nodos más cercanos al cordón (4 y 8 mm) = 190.0 MPa

La extrapolación con los nodos más cercanos recoge el pico de entalla y sobreestima; el esquema IIW a t/2 y 3t/2 es el que corresponde a las categorías hot-spot.
```

</details>

#### Effective notch stress (fictitious 1 mm radius) for three weld types

K_t estimated by weld type and t/r ratio, comparison with FAT 225 and verdict for 2·10⁶ and 10⁷ cycles.

<details><summary>Actual output of <code>python examples/effective_notch_stress_iiw_fat225_weld_types.py</code></summary>

```text
σ_nom = 80.0 MPa, t = 12.0 mm, r_ref = 1 mm, código IIW

cordón        K_t  σ_notch   FAT  N=2e6  N=1e7
butt         1.94    154.8   225    OK    NO
fillet       2.96    236.7   225    NO    NO
cruciform    3.51    280.4   225    NO    NO

Mismo cordón en ángulo evaluado con las categorías de entalla que el paquete asigna a otros códigos:
  IIW   FAT =   225, σ_notch = 236.7 MPa
  AISC  FAT =   200, σ_notch = 236.7 MPa
  AS    FAT =   215, σ_notch = 236.7 MPa
  NSR   FAT =   220, σ_notch = 236.7 MPa
```

</details>

#### Jacket brace weld: marine environment and thickness effect

The package's indicative environmental factors combined with k_s = (25/t)^0.2 of EN 1993-1-9 §7.2.1 on a single-slope curve.

<details><summary>Actual output of <code>python examples/offshore_brace_weld_corrosion_and_thickness_effect.py</code></summary>

```text
Categoría base 71 MPa, t = 40 mm → k_s = 0.910, Δσ = 50.0 MPa

ambiente           factor  Δσ_C amb  Δσ_C amb·k_s    N (amb)   N (amb+t)
seawater             0.50      35.5          32.3   7.16e+05    5.40e+05
marine_atmosphere    0.70      49.7          45.2   1.96e+06    1.48e+06
industrial           0.80      56.8          51.7   2.93e+06    2.21e+06
urban                0.85      60.4          54.9   3.52e+06    2.65e+06
rural                1.00      71.0          64.6   5.73e+06    4.32e+06

Los factores ambientales son valores orientativos del paquete; para proyecto, usar la curva en agua de mar con o sin protección catódica de la norma aplicable (p. ej. DNV-RP-C203).
```

</details>

#### S-N curves of EN 1993-1-9, AS 4100, AISC 360-22 and ASME for the same range

Multi-code comparison, size effect and categories equivalent to a given Δσ_C.

<details><summary>Actual output of <code>python examples/multicode_sn_curves_en_aisc_as_asme.py</code></summary>

```text
Ciclos resistentes para Δσ = 80.0 MPa

EN 1993-1-9 (catálogo FAT, curva trilineal de ec3_sn):
   FAT 160  Δσ_C =  160.0 MPa  N = 3.474e+07
   FAT 140  Δσ_C =  140.0 MPa  N = 1.782e+07
   FAT 125  Δσ_C =  125.0 MPa  N = 1.011e+07
   FAT 112  Δσ_C =  112.0 MPa  N = 5.840e+06
   FAT 100  Δσ_C =  100.0 MPa  N = 3.906e+06
    FAT 90  Δσ_C =   90.0 MPa  N = 2.848e+06
    FAT 80  Δσ_C =   80.0 MPa  N = 2.000e+06
    FAT 71  Δσ_C =   71.0 MPa  N = 1.398e+06

AS 4100 §11 (recta única m = 3 con cut-off a 1e8):
  Cat. 160  Δσ_C =  160.0 MPa  N = 1.600e+07
  Cat. 125  Δσ_C =  125.0 MPa  N = 7.629e+06
  Cat. 100  Δσ_C =  100.0 MPa  N = 3.906e+06
  Cat.  80  Δσ_C =   80.0 MPa  N = 2.000e+06
  Cat.  63  Δσ_C =   63.0 MPa  N = 9.767e+05
  Cat.  50  Δσ_C =   50.0 MPa  N = 4.883e+05
  Cat.  36  Δσ_C =   36.0 MPa  N = 1.823e+05

AISC 360-22 Apéndice 3:
  Cat.  A  Δσ_C =  165.0 MPa  m = 3  N = 1.755e+07
  Cat.  B  Δσ_C =  110.0 MPa  m = 3  N = 5.199e+06
  Cat. B'  Δσ_C =   83.0 MPa  m = 3  N = 2.234e+06
  Cat.  C  Δσ_C =   69.0 MPa  m = 3  N = 1.283e+06
  Cat. C'  Δσ_C =   55.0 MPa  m = 3  N = 6.499e+05
  Cat.  D  Δσ_C =   48.0 MPa  m = 3  N = 4.320e+05
  Cat.  E  Δσ_C =   31.0 MPa  m = 3  N = 1.164e+05
  Cat. E'  Δσ_C =   18.0 MPa  m = 3  N = 2.278e+04

Efecto de tamaño (t = 50 mm): k_s = 0.871
  B': Δσ_C 83.0 → 72.3 MPa, N 2.23e+06 → 1.47e+06

Categorías equivalentes a Δσ_C = 90 MPa:
   US       B'  Δσ_C = 83.0 MPa
   AU      100  Δσ_C = 100.0 MPa
   AU       80  Δσ_C = 80.0 MPa
  ASME   AD-100  Δσ_C = 100.0 MPa
```

</details>

### 5. Component fatigue, crack growth and low-cycle fatigue

#### Hot-rolled shaft: endurance limit corrected by the Marin factors

S_e' = 0.5·S_u and Shigley's factors k_a to k_e for different finishes, load types, temperature and reliability.

<details><summary>Actual output of <code>python examples/marin_factors_endurance_limit_hot_rolled_shaft_shigley.py</code></summary>

```text
Eje S_u = 620 MPa, d = 40 mm, confiabilidad 99 %

laminado en caliente, flexión      ka=0.570 kb=0.836 kc=1.00 kd=0.999 ke=0.814  S_e' = 310 → S_e = 120.2 MPa
mecanizado, flexión                ka=0.821 kb=0.836 kc=1.00 kd=0.999 ke=0.814  S_e' = 310 → S_e = 172.9 MPa
rectificado, flexión               ka=0.915 kb=0.836 kc=1.00 kd=0.999 ke=0.814  S_e' = 310 → S_e = 192.8 MPa
mecanizado, carga axial            ka=0.821 kb=1.000 kc=0.85 kd=0.999 ke=0.814  S_e' = 310 → S_e = 175.9 MPa
mecanizado, torsión                ka=0.821 kb=0.836 kc=0.59 kd=0.999 ke=0.814  S_e' = 310 → S_e = 102.0 MPa
mecanizado, flexión, 250 °C        ka=0.821 kb=0.836 kc=1.00 kd=1.000 ke=0.814  S_e' = 310 → S_e = 173.1 MPa
mecanizado, flexión, conf. 50 %    ka=0.821 kb=0.836 kc=1.00 kd=0.999 ke=1.000  S_e' = 310 → S_e = 212.5 MPa
```

</details>

#### SWT multiaxial fatigue: critical plane from a non-proportional stress history

Search for the plane that maximises σ_max·ε_a and solution of N_f on the Basquin–Coffin-Manson curve. The default parameters are generic and must be replaced by those of the tested steel.

<details><summary>Actual output of <code>python examples/swt_multiaxial_critical_plane_from_fem_stress_history.py</code></summary>

```text
Plano crítico: θ = 0.0°
  σ_max = 120.0 MPa, ε_a = 6.000e-04, P_SWT = 0.0720 MPa
  N_f (SWT, parámetros por defecto) = 8.176e+08 ciclos

Mismo plano con amplitudes de deformación crecientes (daño plástico):
  ε_a = 0.0008 → N_f = 1.965e+08
  ε_a = 0.0015 → N_f = 9.274e+06
  ε_a = 0.0030 → N_f = 4.310e+05
  ε_a = 0.0060 → N_f = 3.797e+04

Con include_shear=True cada criterio busca su propio plano (elástico, Δγ = Δτ/G):
  SWT          θ =   0.0°  P_SWT = 0.0720 MPa
  Findley      θ =   0.0°  P_F = τ_a + 0,30·σ_n,max = 96.0 MPa (τ_a = 60.0 MPa)
  Brown-Miller θ =   0.0°  P_BM = Δγ/2 + Δε_n = 1.980e-03
```

</details>

#### Crack detected in a bridge girder flange: residual life by the Paris law

Critical size from K_IC, integration of da/dN = C·ΔK^m with the Barsom-Rolfe C (m/cycle with ΔK in MPa·√m) and inspection interval. Until this version ΔK was evaluated in MPa·√mm with that same C, which divided the life by √1000 = 31.6; this is fixed and pinned by a test against the closed form.

<details><summary>Actual output of <code>python examples/paris_law_remaining_life_bridge_girder_flange_crack.py</code></summary>

```text
a_c = (K_IC/(Y·σ_max))²/π = 40.6 mm
N de 2.0 mm a 40.6 mm = 1.279e+06 ciclos = 0.9 años
Intervalo de inspección propuesto (vida/2): 0.4 años

Crecimiento de la grieta (N acumulado → a):
         39136 ciclos (  0.0 años) → a =  2.00 mm
        765861 ciclos (  0.5 años) → a =  6.84 mm
        969579 ciclos (  0.6 años) → a = 11.67 mm
       1075604 ciclos (  0.7 años) → a = 16.51 mm
       1143234 ciclos (  0.8 años) → a = 21.35 mm
       1191165 ciclos (  0.8 años) → a = 26.19 mm
       1227413 ciclos (  0.8 años) → a = 31.02 mm
       1256064 ciclos (  0.8 años) → a = 35.86 mm

La mitad de la vida se consume mientras la grieta es menor de 5.3 mm: detectarla pronto es lo que cuenta.

Umbral ΔK_th = 2.0 MPa·√m (delta_K_th_MPa_sqrt_m):
  Δσ =   80 MPa: ΔK inicial = 7.10 MPa·√m → N = 1.279e+06 ciclos
  Δσ =   20 MPa: ΔK inicial = 1.78 MPa·√m → N = inf ciclos (por debajo del umbral: la grieta no crece)
```

</details>

#### RBS connection under the AISC 341 loading protocol: low-cycle damage

Plastic rotation per protocol cycle, N_f by Coffin-Manson with A992-type parameters, Miner damage and number of complete sequences to failure.

<details><summary>Actual output of <code>python examples/rbs_connection_low_cycle_fatigue_aisc341_loading_protocol.py</code></summary>

```text
Protocolo AISC 341: 30 ciclos, 8 con rotación plástica
Daño acumulado D = 0.047, ε_p máx = 0.0150 → OK: Daño 0.047 < 0.5

N_f por amplitud de rotación plástica:
  θ_p = 0.005 rad → ε_p = 0.0025 → N_f =   1459.7
  θ_p = 0.010 rad → ε_p = 0.0050 → N_f =    459.8
  θ_p = 0.020 rad → ε_p = 0.0100 → N_f =    144.8
  θ_p = 0.030 rad → ε_p = 0.0150 → N_f =     73.7
  θ_p = 0.040 rad → ε_p = 0.0200 → N_f =     45.6

Secuencias completas del protocolo hasta D = 1: 21.43
```

</details>

#### Bracing gusset plate: interface forces by the Uniform Force Method

Forces at the gusset-to-beam and gusset-to-column interfaces with θ implied by the geometry, equilibrium check with an imposed angle and a compression case.

<details><summary>Actual output of <code>python examples/gusset_plate_uniform_force_method_brace_connection.py</code></summary>

```text
θ implícito = atan((β+e_b)/(α+e_c)) = 42.24°
  Interfaz cartela-viga:   H_b =   476.0 kN   V_b =   222.9 kN
  Interfaz cartela-pilar:  H_c =   190.4 kN   V_c =   382.0 kN
  ΣH = 666.3 kN frente a P·cos θ = 666.3 kN
  ΣV = 605.0 kN frente a P·sin θ = 605.0 kN

Con θ = 42° impuesto: equilibrio UFM NO se cumple (residuo α − β·tanθ − (e_c·tanθ − e_b) = 146.5 mm)
  Las componentes no cambian (dependen solo de la geometría): H_b = 476.0 kN, V_c = 382.0 kN, pero ΣH = 666.3 ≠ P·cos 42° = 668.8 kN

Diagonal a compresión (P = −900 kN): H_b = -476.0 kN, V_c = -382.0 kN (signos invertidos)
```

</details>

### 6. Calculation reports and REST API

#### Palmgren-Miner report in Markdown and LaTeX

The same worked master's example that anchors the curve (record W01510, Exercise 9): D = 0.63. Requires the `memos` extra.

<details><summary>Actual output of <code>python examples/calculation_memo_miner_handcalcs_markdown.py</code></summary>

```text
D total = 0.631 → CUMPLE
  P1 (vano)      Δσ =  75.16 MPa  n = 1.0e+06  N =  1.586e+06  n/N = 0.6306
  P2 (voladizo)  Δσ =   8.67 MPa  n = 2.0e+06  N =  3.611e+10  n/N = 0.0001

--- Markdown (primeras líneas) ---
# Memoria — Daño acumulado Palmgren-Miner (EN 1993-1-9)

**Categoría de detalle:** Δσ_C = 80.0 MPa
**Factor parcial:** γ_Mf = 1.15
**Resistencia de diseño:** Δσ_C,d = 69.6 MPa

## Espectro de tensiones

| Bloque | Δσ [MPa] | n_i | N_i | D_i |
|---|---|---|---|---|
| P1 (vano) | 75.2 | 1.00e+06 | 1.59e+06 | 0.6306 |
| P2 (voladizo) | 8.7 | 2.00e+06 | 3.61e+10 | 0.0001 |

**Daño total:** D = 0.631
**Verificación:** D ≤ 1.0 → ✅ PASS

LaTeX: 131 caracteres generados
```

</details>

#### Combined report: high-cycle in service plus low-cycle in an earthquake

It adds D_HCF (Miner) and D_LCF (Basquin + Coffin-Manson) and issues a single report.

<details><summary>Actual output of <code>python examples/calculation_memo_combined_hcf_lcf_seismic_connection.py</code></summary>

```text
D_HCF = 0.8144   D_LCF = 0.0225   D_total = 0.8369 → CUMPLE

Ciclos LCF (amplitud de deformación → N_f, daño):
  #1   ε_a = 0.0040 → N_f =    2046.7  n/N = 0.0005
  #2   ε_a = 0.0040 → N_f =    2046.7  n/N = 0.0005
  #3   ε_a = 0.0040 → N_f =    2046.7  n/N = 0.0005
  #4   ε_a = 0.0040 → N_f =    2046.7  n/N = 0.0005
  #5   ε_a = 0.0040 → N_f =    2046.7  n/N = 0.0005
  #6   ε_a = 0.0040 → N_f =    2046.7  n/N = 0.0005
  … 14 ciclos en total

--- Markdown (primeras líneas) ---
# Memoria -- Fatiga combinada HCF + LCF

## Fatiga de alto ciclo -- Palmgren-Miner (HCF)

Daño acumulado Palmgren-Miner (EN 1993-1-9)

**Categoría de detalle:** Δσ_C = 71.0 MPa
**Factor parcial:** γ_Mf = 1.15
**Resistencia de diseño:** Δσ_C,d = 61.7 MPa

## Espectro de tensiones

| Bloque | Δσ [MPa] | n_i | N_i | D_i |
|---|---|---|---|---|
```

</details>

#### REST API without a server, with FastAPI's TestClient

`/api/fatigue/evaluate`, `/api/fatigue/hotspot` and `/api/fatigue/paris`; an incomplete input returns 422, not 500. The same application is served with `uvicorn steelfatigue.api.app:app`.

<details><summary>Actual output of <code>python examples/rest_api_fatigue_evaluate_with_testclient.py</code></summary>

```text
GET /api/fatigue/health → 200 {'status': 'ok'}

POST /api/fatigue/evaluate → 200
{
  "detail_category": 80.0,
  "total_damage": 0.6325,
  "status": "PASS",
  "message": "Fatigue life is adequate"
}

POST /api/fatigue/hotspot → 200 {'sigma_hot_spot_MPa': 158.07999999999998}

POST /api/fatigue/paris → 200 {'N_cycles': 1295428.1, 'failure': True} (199 puntos (N, a) en 'a_vs_N')

Bloque sin 'stress_range' → 422 (422: validación de entrada, no 500)
```

</details>

## Verification

- The golden tests of `ec3_sn` and `ec3_brittle_fracture` anchor the results to the hand-solved examples of the UPC master's course (records W01419, W01510, W01468/W01469, W01508, W01407, W01445) and to the full category 90 curve derived from the text of EN 1993-1-9 §7.1. No expected value is obtained by re-running the function under test.
- Rainflow counting reproduces the table of the ASTM E1049-85 §5.4.4 example (`tests/test_rainflow_residue_astm_golden.py`).
- The Paris integration matches the closed form for constant Y within the discretisation error (`tests/test_paris_closed_form_golden.py`).
- Two errata in the source records were documented in the tests and not anchored: W01419 writes Δσ_L = 0.549·Δσ_C (correct is 0.549·Δσ_D) and W01407 picks the m = 5 branch by the number of applied cycles instead of by Δσ against Δσ_D.
- Fixes in this revision (1.1.0): the rainflow residue is counted as consecutive half cycles (previously one of every two segments was lost, including the largest range); the Paris law evaluates ΔK in MPa·√m, consistent with the default C (previously the life came out divided by 31.6); removed a division-by-zero warning in Coffin-Manson with zero rotations.

## Limitations

- `rainflow_count` uses `fatpack` by default, which quantises the reversals into 64 levels between the minimum and maximum of the signal: ranges come out with an error of up to 1.6 % of the maximum range (the number of cycles is not affected). With `use_float64_exact=True` it counts with the ASTM E1049 four-point rule without quantisation.
- `services.hotspot_service` estimates the life with a single-slope line m = 3 by default; with `use_trilinear_ec3=True` it uses the trilinear curve of EN 1993-1-9.
- The K_t values of `notch_stress` are the package's own fits by weld type, not the IIW tables; the notch categories assigned to AISC, AS and NSR are package equivalences.
- The environmental factors of `corrosion` are indicative. For design, use the seawater curves of the applicable code.
- `paris_law`: constant Y and no stress-ratio R effect; the threshold `delta_K_th_MPa_sqrt_m` is 0 by default (no threshold); the default C is the Barsom-Rolfe upper bound for ferritic-pearlitic steels.
- `lowcycle.CoffinMansonRBS` converts plastic rotation into strain with a constant geometric factor (0.5 by default); the default parameters are those of A992.
- `multiaxial.critical_plane_search` takes ε = σ/E on the normal plane (elastic) for SWT; with `include_shear=True` it adds Findley (k = 0.30 by default) and Brown-Miller with Δγ = Δτ/G, also elastic. Each criterion is maximised on its own plane: up to 1.1.0, Findley and Brown-Miller were evaluated on the SWT plane (110 MPa → 65.4 MPa in the regression test).
- `sn_curves.FatigueEvaluator` is the legacy single-slope implementation without knee or cut-off; for EN 1993-1-9 use `ec3_sn`.
- `gusset_rbs` duplicates UFM and Coffin-Manson with simplified formulas for compatibility; the reference versions are in `lowcycle`. Since 1.1.2 `FatigueRBS` counts cycles like `lowcycle` (up to 1.1.1 it took reversals as cycles and gave half the damage). With σ′_f > 0 it adds Basquin to the capacity but compares it with the plastic strain: an approximation on the unsafe side.
- EN 1993-1-10: T_Ed is simplified to the dominant term T₀ − ΔT_r; the other Annex A terms and the full Table 2.1 are not in the package.

## Codes and references

- EN 1993-1-9:2005, Eurocode 3, Part 1-9: Fatigue. §3 (γ_Mf, Table 3.1), §7.1 (S-N curve, eq. 7.1, Fig. 7.1), §7.2.1 (size effect), Annex A.6 (Palmgren-Miner).
- EN 1993-1-10:2005, Part 1-10: Material toughness and through-thickness properties. §2.2, Table 2.1, Annex B.
- ASTM E1049-85 (2017), Standard Practices for Cycle Counting in Fatigue Analysis, §5.4.4.
- Hobbacher, A. (2008), Recommendations for Fatigue Design of Welded Joints and Components, IIW XIII-2151-07 / XV-1254-07.
- AISC 360-22, Appendix 3; AS 4100 §11; ASME BPVC VIII Div. 2.
- Budynas, R. and Nisbett, J. K., Shigley's Mechanical Engineering Design, ch. 6.
- Paris, P. and Erdogan, F. (1963); Barsom, J. M. and Rolfe, S. T., Fracture and Fatigue Control in Structures.
- Smith, K. N., Watson, P. and Topper, T. H. (1970).
- Engelhardt, M. D. (2007), FEMA 350; AISC 341-16 §K2.4b (loading protocol).
- Thornton, W. A. and Muir, L. S., AISC Manual Part 13 (Uniform Force Method).
- Records of the Master's in Structural and Construction Engineering (UPC) cited by WorkID in the docstrings of `tests/`.

## License

MIT. See [LICENSE](LICENSE).

---

Part of **Loadpath**, the collection of open-source structural libraries by [Jesús Murgas](https://github.com/jmurgass99).
