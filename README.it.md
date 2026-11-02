# steelfatigue — fatica e rottura fragile dell'acciaio strutturale (EN 1993-1-9 e EN 1993-1-10)

[Español](README.md) · [English](README.en.md) · [Português](README.pt.md) · **Italiano**

Verifica a fatica dei dettagli in acciaio strutturale per categoria di dettaglio con la curva S-N trilineare della EN 1993-1-9 e il danno di Palmgren-Miner con γ_Mf; spessore massimo ammissibile contro la rottura fragile secondo la EN 1993-1-10; e il percorso completo a partire da una storia di tensioni misurata o simulata: conteggio rainflow (ASTM E1049), correzione per la tensione media, tensione di hot spot e di intaglio (IIW), propagazione della cricca (Paris) e fatica a basso numero di cicli (Coffin-Manson). Python puro, senza stato globale, con le funzioni ancorate a esempi risolti a mano.

[![CI](https://github.com/jmurgass99/steelfatigue/actions/workflows/ci.yml/badge.svg)](https://github.com/jmurgass99/steelfatigue/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Quale problema risolve

Hai uno spettro di escursioni di tensione (o una storia σ(t)) in un dettaglio saldato o bullonato e devi sapere quanti cicli resiste, quale danno accumula nella vita di progetto e quale categoria di dettaglio o quale spessore ti serve. Il pacchetto fa questa parte: la curva di resistenza, il conteggio dei cicli e l'accumulo del danno. Le tensioni le porti tu, dal tuo modello o dalle tue misure.

**Usalo quando**

- verifichi un dettaglio della EN 1993-1-9 con uno spettro a blocchi {Δσ, n} e un γ_Mf della Tabella 3.1;
- parti da una storia di tensioni (sensore, analisi dinamica, transito di carichi) e vuoi arrivare al danno con il rainflow e, se serve, la correzione per la tensione media;
- hai letture di un modello a guscio a t/2 e 3t/2 da un cordone e ti serve la tensione di hot spot IIW;
- vuoi lo spessore massimo ammissibile a rottura fragile di un elemento S355 a bassa temperatura con i punti della Tabella 2.1 della EN 1993-1-10 inseriti a mano;
- fai uno screening della vita residua di una cricca rilevata (Paris) o del danno a basso numero di cicli di un collegamento RBS sotto un protocollo sismico.

**Non usarlo per**

- ottenere tensioni da geometria e carichi: non c'è un modello di aste né di sezioni;
- il metodo dei fattori di danno equivalente λ della EN 1993-2 o della EN 1993-6 (ponti, vie di corsa): non è implementato;
- consultare le Tabelle da 8.1 a 8.10 della EN 1993-1-9: il catalogo del pacchetto ha 12 categorie con una descrizione breve e l'assegnazione definitiva spetta a te;
- la Tabella 2.1 completa della EN 1993-1-10: la funzione riceve i punti (rapporto, t_max) della sottoqualità e della temperatura che si applicano al tuo caso e non estrapola oltre;
- ridurre al 60 % la parte di compressione dell'escursione nei dettagli non saldati (EN 1993-1-9 §7.2.1(1)): non è implementato;
- la meccanica della frattura con K_IC e dimensione del difetto per il giudizio di rottura fragile: solo il metodo dello spessore della EN 1993-1-10.

## Installazione

```bash
pip install git+https://github.com/jmurgass99/steelfatigue.git
pip install "steelfatigue[api,memos] @ git+https://github.com/jmurgass99/steelfatigue.git"   # API REST e relazioni handcalcs
```

Dipendenze: `numpy` e `fatpack`. Per lo sviluppo: `git clone`, `pip install -e ".[test,api,memos]"`, `pytest -q` (26 file di test). Su Windows, se la console non è UTF-8, esegui gli esempi con `python -X utf8 examples/<nome>.py`.

## Funzionalità

| Funzionalità | Moduli | Norma o riferimento | Casi d'uso |
|---|---|---|---|
| Fatica per categoria di dettaglio: curva S-N trilineare (m = 3/5, ginocchio a 5·10⁶, cut-off a 10⁸), Palmgren-Miner con γ_Mf, catalogo FAT | `ec3_sn`, `wohler_db`, `sn_curves` | EN 1993-1-9 §7.1, §3 Tabella 3.1, §A.6 | [6 casi](#1-fatica-per-categoria-di-dettaglio-en-1993-1-9) |
| Rottura fragile: T_Ed, f_y(t) ridotta per lo spessore, t_max interpolato nella tabella della sottoqualità | `ec3_brittle_fracture` | EN 1993-1-10 §2.2, Allegato B eq. B.1, Tabella 2.1 | [5 casi](#2-rottura-fragile-per-spessore-en-1993-1-10) |
| Dalla storia delle tensioni al danno: rainflow, tensione media (Goodman, Gerber, Soderberg, ASME, Langer), ampiezza variabile, escursione equivalente | `rainflow_fatpack`, `variable_amplitude`, `mean_stress` | ASTM E1049-85 §5.4.4, Shigley §6-12, AISC 360-22 App. 3 | [5 casi](#3-dalla-storia-delle-tensioni-al-danno) |
| Tensioni locali nelle saldature: hot spot IIW (lineare e quadratico), intaglio efficace FAT 225, fattore di spessore, fattori ambientali, curve AISC/AS/ASME | `hotspot`, `services.hotspot_service`, `notch_stress`, `corrosion`, `sn_curves_multi` | IIW XIII-2151-07 (Hobbacher 2008) §2.2.3 e §2.2.4, EN 1993-1-9 §7.2.1, AISC 360-22 App. 3, AS 4100 §11, ASME VIII-2 | [5 casi](#4-tensioni-locali-nelle-saldature-e-curve-s-n-di-altre-norme) |
| Fatica dei componenti e a basso numero di cicli: fattori di Marin, Smith-Watson-Topper con piano critico, legge di Paris, Coffin-Manson nelle RBS, forze UFM nei fazzoletti | `endurance_factors`, `multiaxial`, `paris_law`, `lowcycle`, `gusset_rbs` | Shigley §6-9 a §6-18, SWT 1970, Paris-Erdogan 1963 con C di Barsom-Rolfe, Engelhardt 2007 / FEMA 350, AISC Manual Part 13 | [5 casi](#5-fatica-dei-componenti-propagazione-della-cricca-e-fatica-a-basso-numero-di-cicli) |
| Relazioni di calcolo (Markdown e LaTeX) e API REST | `memos`, `api` | — | [3 casi](#6-relazioni-di-calcolo-e-api-rest) |

I 29 script di `examples/` sono stati eseguiti in un ambiente pulito prima della pubblicazione; il loro output è in `examples/output/` ed è quello riprodotto qui.

## Casi d'uso

Gli output sono riportati esattamente come li stampano gli script, in spagnolo.

### 1. Fatica per categoria di dettaglio (EN 1993-1-9)

#### Trave di via di corsa di carroponte: danno per categoria di dettaglio e γ_Mf

Uno spettro di servizio di 50 anni valutato per sei categorie FAT e i tre γ_Mf della Tabella 3.1. Serve a decidere quale dettaglio costruttivo è ammissibile prima di disegnare la saldatura.

<details><summary>Output reale di <code>python examples/crane_runway_girder_miner_by_detail_category_en1993_1_9.py</code></summary>

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

#### Trave IPE 500 con sbalzo sotto due carichi ripetuti: fatica in due sezioni

Problema dell'esame UPC del 2020-03-30 (schede W01468/W01469 dell'estrazione del master). La stessa categoria 80 è verificata in mezzeria e non lo è all'incastro dello sbalzo: la sezione critica a fatica la decide l'escursione di tensione per ciclo, non il momento statico. Risultati della scheda: N_B = 13 811, D_B = 0,40, D_C = 1,07.

<details><summary>Output reale di <code>python examples/ipe500_cantilever_beam_two_sections_exam_w01468.py</code></summary>

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

#### Carico ammissibile per una vita richiesta (curva S-N invertita)

Exercise 7b del master (scheda W01508): quale carico esaurisce esattamente 500 000 cicli in un dettaglio di categoria 80 e in uno di categoria 36. Si risolve per bisezione sulla curva trilineare e si confronta con la forma chiusa del tratto m = 3. Risultato della scheda: 376,3 kN e 102,4 kN.

<details><summary>Output reale di <code>python examples/admissible_load_for_required_life_exam_w01508.py</code></summary>

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

#### Longherina di ponte ferroviario: vita in anni dallo spettro giornaliero dei treni

Danno giornaliero con la curva trilineare, vita come 1/(D·365) e ripartizione del danno per blocco. Confronta un giunto testa a testa trasversale (71) con un cordone longitudinale continuo (112): il dettaglio di categoria migliore moltiplica la vita per dieci.

<details><summary>Output reale di <code>python examples/railway_bridge_stringer_life_from_daily_train_spectrum.py</code></summary>

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

#### Ginocchio, cut-off e tratto m = 5 di ogni categoria contro una retta unica m = 3

Tabella di Δσ_D e Δσ_L del catalogo (coincide con le dispense UPC, scheda W01419) e quanto sbaglia una retta a pendenza unica nel tratto m = 5 e sotto il cut-off. Spiega quando usare `ec3_sn` e quando basta `FatigueEvaluator`.

<details><summary>Output reale di <code>python examples/sn_curve_knee_cutoff_table_vs_single_slope.py</code></summary>

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

#### Scegliere la categoria di dettaglio dal catalogo

Ricerca per parola chiave, consultazione per codice e vita di ogni categoria per la stessa escursione. Le descrizioni sono sintesi; l'assegnazione definitiva si fa con le Tabelle da 8.1 a 8.10 della norma.

<details><summary>Output reale di <code>python examples/select_detail_category_from_catalogue.py</code></summary>

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

### 2. Rottura fragile per spessore (EN 1993-1-10)

#### Ala IPE 500 in S355JR a −35 °C: spessore massimo ammissibile

Parte di rottura fragile dello stesso esame (schede W01468/W01469): T_Ed = T₀ − ΔT_r = −40 °C, f_y(t) = f_y − 0,25·t, interpolazione lineare tra i due punti della Tabella 2.1 trascritti dalle schede per S355JR a −40 °C. Risultato della scheda: t_max ≈ 21,4 mm > 16 mm.

<details><summary>Output reale di <code>python examples/brittle_fracture_ipe500_s355jr_minus35c_exam_w01468.py</code></summary>

```text
σ_Ed = 207.46 N/mm² (M = 400 kN·m, W_el,y = 1928.1 cm³)
T_Ed = -40 °C (T₀ = -35 °C, ΔT_r = 5 °C)
f_y(t) = 351.0 N/mm² (f_y − 0,25·t, Anexo B)

σ_Ed / f_y(t) = 0.591
t_max admisible (interpolado en la tabla S355JR, T_Ed = -40 °C) = 21.4 mm
t_f = 16.0 mm  →  VERIFICA
```

</details>

#### Trave composta saldata: scegliere lo spessore dell'ala per servizio a −35 °C

Scansione degli spessori candidati con la tensione stimata dalla coppia delle ali. Quando l'utilizzo esce dai punti di tabella disponibili il pacchetto lo segnala e non estrapola: servono altri punti della Tabella 2.1.

<details><summary>Output reale di <code>python examples/brittle_fracture_plate_girder_flange_thickness_choice.py</code></summary>

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

#### Sensibilità dello spessore ammissibile al livello di tensione

Per un'ala di 20 mm, da quale σ_Ed in poi smette di essere verificata. Include il rapporto limite ricavato dalla retta di interpolazione.

<details><summary>Output reale di <code>python examples/brittle_fracture_stress_level_sensitivity.py</code></summary>

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

#### Lamiere spesse: effetto della riduzione di f_y(t) dell'Allegato B

Da 10 a 100 mm la riduzione di 0,25 N/mm² per millimetro alza l'utilizzo e abbassa t_max, mentre lo spessore reale cresce: nelle lamiere spesse i due effetti si sommano.

<details><summary>Output reale di <code>python examples/brittle_fracture_thick_plate_reduced_yield.py</code></summary>

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

#### Verifica in blocco degli elementi di un capannone in zona fredda

Elenco degli elementi con spessore e tensione, giudizio per riga e conteggio. Le righe fuori dall'intervallo della tabella vengono segnalate invece di ricevere un numero inventato.

<details><summary>Output reale di <code>python examples/brittle_fracture_batch_check_members.py</code></summary>

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

### 3. Dalla storia delle tensioni al danno

#### Segnale dell'esempio della ASTM E1049-85 §5.4.4

Il conteggio riproduce la tabella della norma (escursione 3: 0,5; 4: 1,5; 6: 0,5; 8: 1,0; 9: 0,5). Fino a questa versione il residuo veniva percorso a due a due e si perdevano tre dei sei semicicli, tra cui quello di escursione maggiore; è corretto e fissato da un test.

<details><summary>Output reale di <code>python examples/rainflow_astm_e1049_example_signal.py</code></summary>

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

#### Passerella pedonale: dalla storia misurata di un giorno al danno in 50 anni

Storia σ(t) → rainflow → spettro delle escursioni → Miner con la curva trilineare → estrapolazione alla vita di progetto ed elenco delle escursioni più dannose.

<details><summary>Output reale di <code>python examples/footbridge_measured_history_rainflow_to_damage.py</code></summary>

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

#### Trave di via di corsa: correzione per la tensione media su una storia con peso proprio

La stessa storia valutata con Goodman, con Gerber e centrata sullo zero, sulla categoria C della AISC 360-22. Quantifica quanto aggiunge al danno la tensione media di trazione.

<details><summary>Output reale di <code>python examples/crane_girder_history_mean_stress_correction_aisc_category.py</code></summary>

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

#### Mensola di supporto di un macchinario: coefficienti di sicurezza nel diagramma di Haigh

Goodman modificato, Gerber, Soderberg, ASME ellittico e Langer per la stessa coppia (σ_a, σ_m), e la tensione completamente alternata equivalente per entrare in una curva S-N con R = −1.

<details><summary>Output reale di <code>python examples/haigh_diagram_safety_factors_machine_support_bracket.py</code></summary>

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

#### Torre eolica: escursione equivalente di danno (DEL) dal rainflow

Estrapola il conteggio di 10 minuti a 20 anni, calcola il DEL per m = 3 e N_ref = 10⁷ e verifica che un unico blocco riproduce il danno dello spettro completo su una retta a pendenza unica. Con la curva trilineare della EN 1993-1-9 la maggior parte dei cicli piccoli resta sotto il cut-off.

<details><summary>Output reale di <code>python examples/wind_turbine_tower_damage_equivalent_range_from_rainflow.py</code></summary>

```text
Ventana de 10 min: 2382 ciclos rainflow, Δσ máx = 44.7 MPa, Σn = 2376.5
Extrapolación a 20 años: 1051200 ventanas, Σn = 2.498e+09 ciclos

Δσ_eq (m = 3, N_ref = 1e+07, 20 años) = 61.24 MPa
Daño del espectro completo (recta m = 3, sin cut-off) = 3.2077
Daño del bloque equivalente                          = 3.2077  (diferencia relativa 6.7e-16)

Mismo espectro con la curva trilineal EN 1993-1-9 (FAT 71, γ_Mf = 1): D = 0.3599; 2373 de 2382 niveles quedan bajo el cut-off y no dañan.
```

</details>

### 4. Tensioni locali nelle saldature e curve S-N di altre norme

#### Hot spot IIW da letture di un modello a guscio

Estrapolazione lineare (tipo a) e quadratica (tipo b) al piede del cordone di una lamiera da 20 mm e vita stimata dal servizio con FAT 100 e FAT 90.

<details><summary>Output reale di <code>python examples/hot_spot_stress_iiw_from_fem_readings_tubular_joint.py</code></summary>

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

#### Hot spot quando la mesh non ha nodi a t/2 e 3t/2

Interpolazione tra i nodi disponibili per ottenere σ(t/2) e σ(3t/2) e confronto con l'estrapolazione diretta dai nodi più vicini al cordone, che raccoglie il picco di intaglio.

<details><summary>Output reale di <code>python examples/hot_spot_from_arbitrary_fem_node_distances.py</code></summary>

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

#### Tensione di intaglio efficace (raggio fittizio di 1 mm) per tre tipi di cordone

K_t stimato per tipo di cordone e rapporto t/r, confronto con FAT 225 e giudizio per 2·10⁶ e 10⁷ cicli.

<details><summary>Output reale di <code>python examples/effective_notch_stress_iiw_fat225_weld_types.py</code></summary>

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

#### Saldatura di un controvento di jacket: ambiente marino ed effetto dello spessore

Fattori ambientali indicativi del pacchetto combinati con k_s = (25/t)^0,2 della EN 1993-1-9 §7.2.1 su una curva a pendenza unica.

<details><summary>Output reale di <code>python examples/offshore_brace_weld_corrosion_and_thickness_effect.py</code></summary>

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

#### Curve S-N di EN 1993-1-9, AS 4100, AISC 360-22 e ASME per la stessa escursione

Confronto tra norme, effetto scala e categorie equivalenti a un Δσ_C dato.

<details><summary>Output reale di <code>python examples/multicode_sn_curves_en_aisc_as_asme.py</code></summary>

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

### 5. Fatica dei componenti, propagazione della cricca e fatica a basso numero di cicli

#### Albero laminato a caldo: limite di fatica corretto con i fattori di Marin

S_e' = 0,5·S_u e i fattori da k_a a k_e di Shigley per diverse finiture, tipi di carico, temperatura e affidabilità.

<details><summary>Output reale di <code>python examples/marin_factors_endurance_limit_hot_rolled_shaft_shigley.py</code></summary>

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

#### Fatica multiassiale SWT: piano critico da una storia di tensioni non proporzionale

Ricerca del piano che massimizza σ_max·ε_a e soluzione di N_f sulla curva di Basquin–Coffin-Manson. I parametri predefiniti sono generici e vanno sostituiti con quelli dell'acciaio provato.

<details><summary>Output reale di <code>python examples/swt_multiaxial_critical_plane_from_fem_stress_history.py</code></summary>

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

#### Cricca rilevata nell'ala di una trave da ponte: vita residua con la legge di Paris

Dimensione critica da K_IC, integrazione di da/dN = C·ΔK^m con la C di Barsom-Rolfe (m/ciclo con ΔK in MPa·√m) e intervallo di ispezione. Fino a questa versione ΔK veniva valutato in MPa·√mm con la stessa C, il che divideva la vita per √1000 = 31,6; è corretto e fissato da un test contro la forma chiusa.

<details><summary>Output reale di <code>python examples/paris_law_remaining_life_bridge_girder_flange_crack.py</code></summary>

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

#### Collegamento RBS sotto il protocollo di carico della AISC 341: danno a basso numero di cicli

Rotazione plastica per ciclo del protocollo, N_f con Coffin-Manson e parametri tipo A992, danno di Miner e numero di sequenze complete fino alla rottura.

<details><summary>Output reale di <code>python examples/rbs_connection_low_cycle_fatigue_aisc341_loading_protocol.py</code></summary>

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

#### Fazzoletto di controvento: forze alle interfacce con il Metodo della Forza Uniforme

Forze alle interfacce fazzoletto-trave e fazzoletto-colonna con θ implicito nella geometria, verifica dell'equilibrio con un angolo imposto e caso di compressione.

<details><summary>Output reale di <code>python examples/gusset_plate_uniform_force_method_brace_connection.py</code></summary>

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

### 6. Relazioni di calcolo e API REST

#### Relazione di Palmgren-Miner in Markdown e LaTeX

Lo stesso esempio risolto del master che ancora la curva (scheda W01510, Exercise 9): D = 0,63. Richiede l'extra `memos`.

<details><summary>Output reale di <code>python examples/calculation_memo_miner_handcalcs_markdown.py</code></summary>

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

#### Relazione combinata: alto numero di cicli in servizio più basso numero di cicli nel sisma

Somma D_HCF (Miner) e D_LCF (Basquin + Coffin-Manson) ed emette un'unica relazione.

<details><summary>Output reale di <code>python examples/calculation_memo_combined_hcf_lcf_seismic_connection.py</code></summary>

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

#### API REST senza server, con il TestClient di FastAPI

`/api/fatigue/evaluate`, `/api/fatigue/hotspot` e `/api/fatigue/paris`; un input incompleto restituisce 422, non 500. La stessa applicazione si serve con `uvicorn steelfatigue.api.app:app`.

<details><summary>Output reale di <code>python examples/rest_api_fatigue_evaluate_with_testclient.py</code></summary>

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

## Verifica

- I test golden di `ec3_sn` e `ec3_brittle_fracture` ancorano i risultati agli esempi risolti a mano del master UPC (schede W01419, W01510, W01468/W01469, W01508, W01407, W01445) e alla curva completa della categoria 90 ricavata dal testo della EN 1993-1-9 §7.1. Nessun valore atteso si ottiene rieseguendo la funzione sotto test.
- Il conteggio rainflow riproduce la tabella dell'esempio della ASTM E1049-85 §5.4.4 (`tests/test_rainflow_residue_astm_golden.py`).
- L'integrazione di Paris coincide con la forma chiusa per Y costante entro l'errore di discretizzazione (`tests/test_paris_closed_form_golden.py`).
- Due errata delle schede di origine sono documentati nei test e non ancorati: la W01419 scrive Δσ_L = 0,549·Δσ_C (il corretto è 0,549·Δσ_D) e la W01407 sceglie il tratto m = 5 in base al numero di cicli applicati invece che in base a Δσ rispetto a Δσ_D.
- Correzioni di questa revisione (1.1.0): il residuo del rainflow si conta come semicicli consecutivi (prima si perdeva un tratto su due, incluso quello di escursione maggiore); la legge di Paris valuta ΔK in MPa·√m, coerente con la C predefinita (prima la vita usciva divisa per 31,6); eliminato un avviso di divisione per zero in Coffin-Manson con rotazioni nulle.

## Limitazioni

- `rainflow_count` usa per impostazione predefinita `fatpack`, che quantizza le inversioni in 64 livelli tra il minimo e il massimo del segnale: le escursioni hanno un errore fino all'1,6 % dell'escursione massima (il numero di cicli non ne risente). Con `use_float64_exact=True` conta con la regola dei 4 punti della ASTM E1049 senza quantizzare.
- `services.hotspot_service` stima per impostazione predefinita la vita con una retta a pendenza unica m = 3; con `use_trilinear_ec3=True` usa la curva trilineare della EN 1993-1-9.
- I K_t di `notch_stress` sono adattamenti propri del pacchetto per tipo di cordone, non le tabelle IIW; le categorie di intaglio assegnate ad AISC, AS e NSR sono equivalenze del pacchetto.
- I fattori ambientali di `corrosion` sono indicativi. Per il progetto, usa le curve in acqua di mare della norma applicabile.
- `paris_law`: Y costante e nessun effetto del rapporto di tensione R; la soglia `delta_K_th_MPa_sqrt_m` vale 0 per impostazione predefinita (nessuna soglia); la C predefinita è il limite superiore di Barsom-Rolfe per acciai ferritico-perlitici.
- `lowcycle.CoffinMansonRBS` converte la rotazione plastica in deformazione con un fattore geometrico costante (0,5 per default); i parametri predefiniti sono quelli dell'A992.
- `multiaxial.critical_plane_search` prende ε = σ/E sul piano normale (elastico) per SWT; con `include_shear=True` aggiunge Findley (k = 0,30 per impostazione predefinita) e Brown-Miller con Δγ = Δτ/G, anch'essi elastici. Ogni criterio è massimizzato sul proprio piano: fino alla 1.1.0 Findley e Brown-Miller erano valutati sul piano di SWT (110 MPa → 65,4 MPa nel test di regressione).
- `sn_curves.FatigueEvaluator` è l'implementazione ereditata a pendenza unica senza ginocchio né cut-off; per la EN 1993-1-9 usa `ec3_sn`.
- `gusset_rbs` duplica UFM e Coffin-Manson con formule semplificate per compatibilità; le versioni di riferimento sono in `lowcycle`. Per impostazione predefinita `FatigueRBS` prende (ε_p/ε_f)^(1/c) come N_f, che nell'equazione di Coffin-Manson sono inversioni (2N_f): dà metà del danno di `lowcycle`, a sfavore di sicurezza. `use_half_reversals=True` o σ′_f > 0 (Basquin) contano in cicli.
- EN 1993-1-10: T_Ed si semplifica al termine dominante T₀ − ΔT_r; gli altri termini dell'Allegato A e la Tabella 2.1 completa non sono nel pacchetto.

## Norme e riferimenti

- EN 1993-1-9:2005, Eurocodice 3, Parte 1-9: Fatica. §3 (γ_Mf, Tabella 3.1), §7.1 (curva S-N, eq. 7.1, Fig. 7.1), §7.2.1 (effetto scala), Allegato A.6 (Palmgren-Miner).
- EN 1993-1-10:2005, Parte 1-10: Resilienza del materiale e proprietà attraverso lo spessore. §2.2, Tabella 2.1, Allegato B.
- ASTM E1049-85 (2017), Standard Practices for Cycle Counting in Fatigue Analysis, §5.4.4.
- Hobbacher, A. (2008), Recommendations for Fatigue Design of Welded Joints and Components, IIW XIII-2151-07 / XV-1254-07.
- AISC 360-22, Appendix 3; AS 4100 §11; ASME BPVC VIII Div. 2.
- Budynas, R. e Nisbett, J. K., Shigley's Mechanical Engineering Design, cap. 6.
- Paris, P. ed Erdogan, F. (1963); Barsom, J. M. e Rolfe, S. T., Fracture and Fatigue Control in Structures.
- Smith, K. N., Watson, P. e Topper, T. H. (1970).
- Engelhardt, M. D. (2007), FEMA 350; AISC 341-16 §K2.4b (protocollo di carico).
- Thornton, W. A. e Muir, L. S., AISC Manual Part 13 (Metodo della Forza Uniforme).
- Schede del Master in Ingegneria Strutturale e delle Costruzioni (UPC) citate per WorkID nelle docstring di `tests/`.

## Licenza

MIT. Vedi [LICENSE](LICENSE).

---

Parte di **Loadpath**, la raccolta di librerie strutturali open source di [Jesús Murgas](https://github.com/jmurgass99).
