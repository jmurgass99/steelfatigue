# steelfatigue — fadiga e fratura frágil do aço estrutural (EN 1993-1-9 e EN 1993-1-10)

[Español](README.md) · [English](README.en.md) · **Português** · [Italiano](README.it.md)

Verificação à fadiga de detalhes de aço estrutural por categoria de detalhe com a curva S-N trilinear da EN 1993-1-9 e o dano de Palmgren-Miner com γ_Mf; espessura máxima admissível contra fratura frágil segundo a EN 1993-1-10; e o caminho completo a partir de um histórico de tensões medido ou simulado: contagem rainflow (ASTM E1049), correção pela tensão média, tensão de ponto quente e de entalhe (IIW), propagação de trinca (Paris) e fadiga de baixo ciclo (Coffin-Manson). Python puro, sem estado global, com as funções ancoradas em exemplos resolvidos à mão.

[![CI](https://github.com/jmurgass99/steelfatigue/actions/workflows/ci.yml/badge.svg)](https://github.com/jmurgass99/steelfatigue/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Que problema resolve

Tem um espectro de variações de tensão (ou um histórico σ(t)) num detalhe soldado ou parafusado e precisa saber quantos ciclos ele resiste, que dano acumula na vida de projeto e que categoria de detalhe ou que espessura é necessária. O pacote faz essa parte: a curva de resistência, a contagem de ciclos e a acumulação de dano. As tensões são suas, do seu modelo ou das suas medições.

**Use quando**

- verificar um detalhe da EN 1993-1-9 com um espectro em blocos {Δσ, n} e um γ_Mf da Tabela 3.1;
- partir de um histórico de tensões (sensor, análise dinâmica, passagem de cargas) e quiser chegar ao dano com rainflow e, se necessário, correção pela tensão média;
- tiver leituras de um modelo de casca a t/2 e 3t/2 de um cordão e precisar da tensão de ponto quente do IIW;
- quiser a espessura máxima admissível à fratura frágil de um elemento S355 a baixa temperatura com os pontos da Tabela 2.1 da EN 1993-1-10 introduzidos à mão;
- fizer uma triagem da vida residual de uma trinca detectada (Paris) ou do dano de baixo ciclo de uma ligação RBS sob um protocolo sísmico.

**Não use para**

- obter tensões a partir de geometria e cargas: não há modelo de barras nem de secções;
- o método dos fatores de dano equivalente λ da EN 1993-2 ou da EN 1993-6 (pontes, vigas de rolamento): não está implementado;
- consultar as Tabelas 8.1 a 8.10 da EN 1993-1-9: o catálogo do pacote tem 12 categorias com uma descrição curta e a atribuição final é sua;
- a Tabela 2.1 completa da EN 1993-1-10: a função recebe os pontos (razão, t_max) da subclasse e da temperatura que se aplicam ao seu caso e não extrapola fora deles;
- reduzir a 60 % a parte de compressão da variação em detalhes não soldados (EN 1993-1-9 §7.2.1(1)): não está implementado;
- mecânica da fratura com K_IC e tamanho de defeito para o veredito de fratura frágil: apenas o método da espessura da EN 1993-1-10.

## Instalação

```bash
pip install git+https://github.com/jmurgass99/steelfatigue.git
pip install "steelfatigue[api,memos] @ git+https://github.com/jmurgass99/steelfatigue.git"   # API REST e memórias handcalcs
```

Dependências: `numpy` e `fatpack`. Para desenvolvimento: `git clone`, `pip install -e ".[test,api,memos]"`, `pytest -q` (23 ficheiros de testes). No Windows, se a consola não for UTF-8, execute os exemplos com `python -X utf8 examples/<nome>.py`.

## Capacidades

| Capacidade | Módulos | Norma ou referência | Casos de uso |
|---|---|---|---|
| Fadiga por categoria de detalhe: curva S-N trilinear (m = 3/5, joelho em 5·10⁶, cut-off em 10⁸), Palmgren-Miner com γ_Mf, catálogo FAT | `ec3_sn`, `wohler_db`, `sn_curves` | EN 1993-1-9 §7.1, §3 Tabela 3.1, §A.6 | [6 casos](#1-fadiga-por-categoria-de-detalhe-en-1993-1-9) |
| Fratura frágil: T_Ed, f_y(t) reduzida pela espessura, t_max interpolado na tabela da subclasse | `ec3_brittle_fracture` | EN 1993-1-10 §2.2, Anexo B eq. B.1, Tabela 2.1 | [5 casos](#2-fratura-frágil-por-espessura-en-1993-1-10) |
| Do histórico de tensões ao dano: rainflow, tensão média (Goodman, Gerber, Soderberg, ASME, Langer), amplitude variável, variação equivalente | `rainflow_fatpack`, `variable_amplitude`, `mean_stress` | ASTM E1049-85 §5.4.4, Shigley §6-12, AISC 360-22 Ap. 3 | [5 casos](#3-do-histórico-de-tensões-ao-dano) |
| Tensões locais em soldas: ponto quente IIW (linear e quadrático), entalhe efetivo FAT 225, fator de espessura, fatores ambientais, curvas AISC/AS/ASME | `hotspot`, `services.hotspot_service`, `notch_stress`, `corrosion`, `sn_curves_multi` | IIW XIII-2151-07 (Hobbacher 2008) §2.2.3 e §2.2.4, EN 1993-1-9 §7.2.1, AISC 360-22 Ap. 3, AS 4100 §11, ASME VIII-2 | [5 casos](#4-tensões-locais-em-soldas-e-curvas-s-n-de-outras-normas) |
| Fadiga de componentes e de baixo ciclo: fatores de Marin, Smith-Watson-Topper com plano crítico, lei de Paris, Coffin-Manson em RBS, forças UFM em chapas de ligação | `endurance_factors`, `multiaxial`, `paris_law`, `lowcycle`, `gusset_rbs` | Shigley §6-9 a §6-18, SWT 1970, Paris-Erdogan 1963 com C de Barsom-Rolfe, Engelhardt 2007 / FEMA 350, AISC Manual Part 13 | [5 casos](#5-fadiga-de-componentes-propagação-de-trinca-e-fadiga-de-baixo-ciclo) |
| Memórias de cálculo (Markdown e LaTeX) e API REST | `memos`, `api` | — | [3 casos](#6-memórias-de-cálculo-e-api-rest) |

Os 29 scripts de `examples/` foram executados num ambiente limpo antes de serem publicados; a saída está em `examples/output/` e é a que se reproduz aqui.

## Casos de uso

As saídas reproduzem-se exatamente como os scripts as imprimem, em espanhol.

### 1. Fadiga por categoria de detalhe (EN 1993-1-9)

#### Viga de rolamento de ponte rolante: dano por categoria de detalhe e γ_Mf

Um espectro de serviço de 50 anos avaliado para seis categorias FAT e os três γ_Mf da Tabela 3.1. Serve para decidir que detalhe construtivo é admissível antes de desenhar a solda.

<details><summary>Saída real de <code>python examples/crane_runway_girder_miner_by_detail_category_en1993_1_9.py</code></summary>

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

#### Viga IPE 500 com balanço sob duas cargas repetidas: fadiga em duas secções

Problema do exame da UPC de 2020-03-30 (fichas W01468/W01469 da extração do mestrado). A mesma categoria 80 verifica no meio do vão e falha no encastramento do balanço: a secção crítica à fadiga é decidida pela variação de tensão por ciclo, não pelo momento estático. Resultados da ficha: N_B = 13 811, D_B = 0,40, D_C = 1,07.

<details><summary>Saída real de <code>python examples/ipe500_cantilever_beam_two_sections_exam_w01468.py</code></summary>

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

#### Carga admissível para uma vida exigida (curva S-N invertida)

Exercise 7b do mestrado (ficha W01508): que carga esgota exatamente 500 000 ciclos num detalhe de categoria 80 e noutro de categoria 36. Resolve-se por bissecção sobre a curva trilinear e contrasta-se com a forma fechada do troço m = 3. Resultado da ficha: 376,3 kN e 102,4 kN.

<details><summary>Saída real de <code>python examples/admissible_load_for_required_life_exam_w01508.py</code></summary>

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

#### Longarina de ponte ferroviária: vida em anos a partir do espectro diário de comboios

Dano por dia com a curva trilinear, vida como 1/(D·365) e repartição do dano por bloco. Compara uma emenda de topo transversal (71) com um cordão longitudinal contínuo (112): o detalhe de melhor categoria multiplica a vida por dez.

<details><summary>Saída real de <code>python examples/railway_bridge_stringer_life_from_daily_train_spectrum.py</code></summary>

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

#### Joelho, cut-off e troço m = 5 de cada categoria contra uma reta única m = 3

Tabela de Δσ_D e Δσ_L do catálogo (coincide com os apontamentos da UPC, ficha W01419) e quanto erra uma reta de inclinação única no troço m = 5 e abaixo do cut-off. Explica quando usar `ec3_sn` e quando basta `FatigueEvaluator`.

<details><summary>Saída real de <code>python examples/sn_curve_knee_cutoff_table_vs_single_slope.py</code></summary>

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

#### Escolher a categoria de detalhe a partir do catálogo

Pesquisa por palavra-chave, consulta por código e vida de cada categoria para a mesma variação. As descrições são resumos; a atribuição final faz-se com as Tabelas 8.1 a 8.10 da norma.

<details><summary>Saída real de <code>python examples/select_detail_category_from_catalogue.py</code></summary>

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

### 2. Fratura frágil por espessura (EN 1993-1-10)

#### Banzo IPE 500 S355JR a −35 °C: espessura máxima admissível

Parte de fratura frágil do mesmo exame (fichas W01468/W01469): T_Ed = T₀ − ΔT_r = −40 °C, f_y(t) = f_y − 0,25·t, interpolação linear entre os dois pontos da Tabela 2.1 transcritos pelas fichas para S355JR a −40 °C. Resultado da ficha: t_max ≈ 21,4 mm > 16 mm.

<details><summary>Saída real de <code>python examples/brittle_fracture_ipe500_s355jr_minus35c_exam_w01468.py</code></summary>

```text
σ_Ed = 207.46 N/mm² (M = 400 kN·m, W_el,y = 1928.1 cm³)
T_Ed = -40 °C (T₀ = -35 °C, ΔT_r = 5 °C)
f_y(t) = 351.0 N/mm² (f_y − 0,25·t, Anexo B)

σ_Ed / f_y(t) = 0.591
t_max admisible (interpolado en la tabla S355JR, T_Ed = -40 °C) = 21.4 mm
t_f = 16.0 mm  →  VERIFICA
```

</details>

#### Viga de alma cheia: escolher a espessura do banzo para serviço a −35 °C

Varrimento de espessuras candidatas com a tensão estimada pelo binário dos banzos. Quando a utilização sai dos pontos de tabela disponíveis o pacote avisa e não extrapola: é preciso fornecer mais pontos da Tabela 2.1.

<details><summary>Saída real de <code>python examples/brittle_fracture_plate_girder_flange_thickness_choice.py</code></summary>

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

#### Sensibilidade da espessura admissível ao nível de tensão

Para um banzo de 20 mm, a partir de que σ_Ed deixa de verificar. Inclui a razão limite obtida da reta de interpolação.

<details><summary>Saída real de <code>python examples/brittle_fracture_stress_level_sensitivity.py</code></summary>

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

#### Chapas grossas: efeito da redução de f_y(t) do Anexo B

De 10 a 100 mm a redução de 0,25 N/mm² por milímetro aumenta a utilização e baixa t_max, enquanto a espessura real aumenta: em chapas grossas os dois efeitos somam-se.

<details><summary>Saída real de <code>python examples/brittle_fracture_thick_plate_reduced_yield.py</code></summary>

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

#### Verificação em lote dos elementos de um pavilhão em zona fria

Lista de elementos com a sua espessura e tensão, veredito por linha e contagem. As linhas fora do intervalo da tabela ficam assinaladas em vez de receberem um número inventado.

<details><summary>Saída real de <code>python examples/brittle_fracture_batch_check_members.py</code></summary>

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

### 3. Do histórico de tensões ao dano

#### Sinal do exemplo da ASTM E1049-85 §5.4.4

A contagem reproduz a tabela da norma (variação 3: 0,5; 4: 1,5; 6: 0,5; 8: 1,0; 9: 0,5). Até esta versão o resíduo era percorrido de dois em dois e perdiam-se três dos seis meios ciclos, entre eles o de maior variação; está corrigido e fixado por teste.

<details><summary>Saída real de <code>python examples/rainflow_astm_e1049_example_signal.py</code></summary>

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
```

</details>

#### Passadiço pedonal: do histórico medido de um dia ao dano em 50 anos

Histórico σ(t) → rainflow → espectro de variações → Miner com a curva trilinear → extrapolação à vida de projeto e lista das variações mais danosas.

<details><summary>Saída real de <code>python examples/footbridge_measured_history_rainflow_to_damage.py</code></summary>

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

#### Viga de rolamento: correção pela tensão média num histórico com peso próprio

O mesmo histórico avaliado com Goodman, com Gerber e centrado em zero, sobre a categoria C da AISC 360-22. Quantifica o que a tensão média de tração acrescenta ao dano.

<details><summary>Saída real de <code>python examples/crane_girder_history_mean_stress_correction_aisc_category.py</code></summary>

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

#### Consola de apoio de maquinaria: fatores de segurança no diagrama de Haigh

Goodman modificado, Gerber, Soderberg, ASME elíptico e Langer para o mesmo par (σ_a, σ_m), e a tensão totalmente alternada equivalente para entrar numa curva S-N com R = −1.

<details><summary>Saída real de <code>python examples/haigh_diagram_safety_factors_machine_support_bracket.py</code></summary>

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

#### Torre eólica: variação equivalente de dano (DEL) a partir do rainflow

Extrapola a contagem de 10 minutos a 20 anos, calcula o DEL para m = 3 e N_ref = 10⁷ e verifica que um único bloco reproduz o dano do espectro completo numa reta de inclinação única. Com a curva trilinear da EN 1993-1-9 a maior parte dos ciclos pequenos fica abaixo do cut-off.

<details><summary>Saída real de <code>python examples/wind_turbine_tower_damage_equivalent_range_from_rainflow.py</code></summary>

```text
Ventana de 10 min: 2382 ciclos rainflow, Δσ máx = 44.7 MPa, Σn = 2376.5
Extrapolación a 20 años: 1051200 ventanas, Σn = 2.498e+09 ciclos

Δσ_eq (m = 3, N_ref = 1e+07, 20 años) = 61.24 MPa
Daño del espectro completo (recta m = 3, sin cut-off) = 3.2077
Daño del bloque equivalente                          = 3.2077  (diferencia relativa 6.7e-16)

Mismo espectro con la curva trilineal EN 1993-1-9 (FAT 71, γ_Mf = 1): D = 0.3599; 2373 de 2382 niveles quedan bajo el cut-off y no dañan.
```

</details>

### 4. Tensões locais em soldas e curvas S-N de outras normas

#### Ponto quente IIW a partir de leituras de um modelo de casca

Extrapolação linear (tipo a) e quadrática (tipo b) ao pé do cordão de uma chapa de 20 mm e vida estimada pelo serviço com FAT 100 e FAT 90.

<details><summary>Saída real de <code>python examples/hot_spot_stress_iiw_from_fem_readings_tubular_joint.py</code></summary>

```text
Lecturas FEM: σ(t/2) = 142.0, σ(3t/2) = 118.0, σ(5t/2) = 104.0 MPa
σ_hs lineal (tipo a)    = 158.1 MPa
σ_hs cuadrática (tipo b) = 168.4 MPa  (+6.5% frente a la lineal)

FAT 100 (cordón no portante), linear   : σ_hs =  158.1 MPa, N ≈ 3.33e+05 ciclos (γ_Mf = 1,15, recta m = 3)
FAT 100 (cordón no portante), quadratic: σ_hs =  168.4 MPa, N ≈ 2.75e+05 ciclos (γ_Mf = 1,15, recta m = 3)
FAT 90 (cordón portante), linear   : σ_hs =  158.1 MPa, N ≈ 2.43e+05 ciclos (γ_Mf = 1,15, recta m = 3)
FAT 90 (cordón portante), quadratic: σ_hs =  168.4 MPa, N ≈ 2.01e+05 ciclos (γ_Mf = 1,15, recta m = 3)
```

</details>

#### Ponto quente quando a malha não tem nós a t/2 e 3t/2

Interpolação entre os nós disponíveis para obter σ(t/2) e σ(3t/2) e comparação com a extrapolação direta a partir dos nós mais próximos do cordão, que apanha o pico do entalhe.

<details><summary>Saída real de <code>python examples/hot_spot_from_arbitrary_fem_node_distances.py</code></summary>

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

#### Tensão de entalhe efetiva (raio fictício de 1 mm) para três tipos de cordão

K_t estimado por tipo de cordão e relação t/r, comparação com FAT 225 e veredito para 2·10⁶ e 10⁷ ciclos.

<details><summary>Saída real de <code>python examples/effective_notch_stress_iiw_fat225_weld_types.py</code></summary>

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

#### Solda de travamento de jacket: ambiente marinho e efeito da espessura

Fatores ambientais orientativos do pacote compostos com k_s = (25/t)^0,2 da EN 1993-1-9 §7.2.1 sobre uma curva de inclinação única.

<details><summary>Saída real de <code>python examples/offshore_brace_weld_corrosion_and_thickness_effect.py</code></summary>

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

#### Curvas S-N da EN 1993-1-9, AS 4100, AISC 360-22 e ASME para a mesma variação

Comparação entre normas, efeito de escala e categorias equivalentes a um Δσ_C dado.

<details><summary>Saída real de <code>python examples/multicode_sn_curves_en_aisc_as_asme.py</code></summary>

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

### 5. Fadiga de componentes, propagação de trinca e fadiga de baixo ciclo

#### Veio laminado a quente: limite de fadiga corrigido pelos fatores de Marin

S_e' = 0,5·S_u e os fatores k_a a k_e de Shigley para diferentes acabamentos, tipos de carga, temperatura e fiabilidade.

<details><summary>Saída real de <code>python examples/marin_factors_endurance_limit_hot_rolled_shaft_shigley.py</code></summary>

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

#### Fadiga multiaxial SWT: plano crítico a partir de um histórico de tensões não proporcional

Pesquisa do plano que maximiza σ_max·ε_a e resolução de N_f na curva de Basquin–Coffin-Manson. Os parâmetros por defeito são genéricos e devem ser substituídos pelos do aço ensaiado.

<details><summary>Saída real de <code>python examples/swt_multiaxial_critical_plane_from_fem_stress_history.py</code></summary>

```text
Plano crítico: θ = 0.0°
  σ_max = 120.0 MPa, ε_a = 6.000e-04, P_SWT = 0.0720 MPa
  N_f (SWT, parámetros por defecto) = 8.176e+08 ciclos

Mismo plano con amplitudes de deformación crecientes (daño plástico):
  ε_a = 0.0008 → N_f = 1.965e+08
  ε_a = 0.0015 → N_f = 9.274e+06
  ε_a = 0.0030 → N_f = 4.310e+05
  ε_a = 0.0060 → N_f = 3.797e+04
```

</details>

#### Trinca detetada no banzo de uma viga de ponte: vida residual pela lei de Paris

Tamanho crítico a partir de K_IC, integração de da/dN = C·ΔK^m com a C de Barsom-Rolfe (m/ciclo com ΔK em MPa·√m) e intervalo de inspeção. Até esta versão ΔK era avaliado em MPa·√mm com essa mesma C, o que dividia a vida por √1000 = 31,6; está corrigido e fixado por um teste contra a forma fechada.

<details><summary>Saída real de <code>python examples/paris_law_remaining_life_bridge_girder_flange_crack.py</code></summary>

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
```

</details>

#### Ligação RBS sob o protocolo de carga da AISC 341: dano de baixo ciclo

Rotação plástica por ciclo do protocolo, N_f por Coffin-Manson com parâmetros tipo A992, dano de Miner e número de sequências completas até à rotura.

<details><summary>Saída real de <code>python examples/rbs_connection_low_cycle_fatigue_aisc341_loading_protocol.py</code></summary>

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

#### Chapa de ligação de contraventamento: forças nas interfaces pelo Método da Força Uniforme

Forças nas interfaces chapa-viga e chapa-pilar com θ implícito pela geometria, verificação do equilíbrio com um ângulo imposto e caso de compressão.

<details><summary>Saída real de <code>python examples/gusset_plate_uniform_force_method_brace_connection.py</code></summary>

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

### 6. Memórias de cálculo e API REST

#### Memória de Palmgren-Miner em Markdown e LaTeX

O mesmo exemplo resolvido do mestrado que ancora a curva (ficha W01510, Exercise 9): D = 0,63. Requer o extra `memos`.

<details><summary>Saída real de <code>python examples/calculation_memo_miner_handcalcs_markdown.py</code></summary>

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

#### Memória combinada: alto ciclo em serviço mais baixo ciclo em sismo

Soma D_HCF (Miner) e D_LCF (Basquin + Coffin-Manson) e emite uma única memória.

<details><summary>Saída real de <code>python examples/calculation_memo_combined_hcf_lcf_seismic_connection.py</code></summary>

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

#### API REST sem servidor, com o TestClient do FastAPI

`/api/fatigue/evaluate`, `/api/fatigue/hotspot` e `/api/fatigue/paris`; uma entrada incompleta devolve 422, não 500. A mesma aplicação serve-se com `uvicorn steelfatigue.api.app:app`.

<details><summary>Saída real de <code>python examples/rest_api_fatigue_evaluate_with_testclient.py</code></summary>

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

## Verificação

- Os testes golden de `ec3_sn` e `ec3_brittle_fracture` ancoram os resultados nos exemplos resolvidos à mão do mestrado da UPC (fichas W01419, W01510, W01468/W01469, W01508, W01407, W01445) e na curva completa da categoria 90 derivada do texto da EN 1993-1-9 §7.1. Nenhum valor esperado se obtém voltando a executar a função em teste.
- A contagem rainflow reproduz a tabela do exemplo da ASTM E1049-85 §5.4.4 (`tests/test_rainflow_residue_astm_golden.py`).
- A integração de Paris coincide com a forma fechada para Y constante dentro do erro de discretização (`tests/test_paris_closed_form_golden.py`).
- Duas erratas das fichas de origem ficaram documentadas nos testes e não foram ancoradas: a W01419 escreve Δσ_L = 0,549·Δσ_C (o correto é 0,549·Δσ_D) e a W01407 escolhe o troço m = 5 pelo número de ciclos aplicados em vez de por Δσ face a Δσ_D.
- Correções desta revisão (1.1.0): o resíduo do rainflow conta-se como meios ciclos consecutivos (antes perdia-se um de cada dois troços, incluindo o de maior variação); a lei de Paris avalia ΔK em MPa·√m, coerente com a C por defeito (antes a vida saía dividida por 31,6); eliminado um aviso de divisão por zero em Coffin-Manson com rotações nulas.

## Limitações

- `fatpack` quantifica as inversões em 64 níveis entre o mínimo e o máximo do sinal: as variações saem com um erro de até 1,6 % da variação máxima. O número de ciclos não é afetado.
- `services.hotspot_service` estima a vida com uma reta de inclinação única m = 3, não com a curva trilinear.
- Os K_t de `notch_stress` são ajustes próprios do pacote por tipo de cordão, não as tabelas do IIW; as categorias de entalhe atribuídas a AISC, AS e NSR são equivalências do pacote.
- Os fatores ambientais de `corrosion` são orientativos. Para projeto, use as curvas em água do mar da norma aplicável.
- `paris_law`: Y constante, sem limiar ΔK_th nem efeito da razão de tensões R; a C por defeito é o limite superior de Barsom-Rolfe para aços ferrítico-perlíticos.
- `lowcycle.CoffinMansonRBS` converte rotação plástica em deformação com um fator geométrico constante (0,5 por defeito); os parâmetros por defeito são os do A992.
- `multiaxial.critical_plane_search` toma ε = σ/E no plano normal (elástico), sem componente de corte.
- `sn_curves.FatigueEvaluator` é a implementação herdada de inclinação única sem joelho nem cut-off; para a EN 1993-1-9 use `ec3_sn`.
- `gusset_rbs` duplica UFM e Coffin-Manson com fórmulas simplificadas por compatibilidade; as versões de referência estão em `lowcycle`.
- EN 1993-1-10: T_Ed simplifica-se ao termo dominante T₀ − ΔT_r; os restantes termos do Anexo A e a Tabela 2.1 completa não estão no pacote.

## Normas e referências

- EN 1993-1-9:2005, Eurocódigo 3, Parte 1-9: Fadiga. §3 (γ_Mf, Tabela 3.1), §7.1 (curva S-N, eq. 7.1, Fig. 7.1), §7.2.1 (efeito de escala), Anexo A.6 (Palmgren-Miner).
- EN 1993-1-10:2005, Parte 1-10: Tenacidade e propriedades segundo a espessura. §2.2, Tabela 2.1, Anexo B.
- ASTM E1049-85 (2017), Standard Practices for Cycle Counting in Fatigue Analysis, §5.4.4.
- Hobbacher, A. (2008), Recommendations for Fatigue Design of Welded Joints and Components, IIW XIII-2151-07 / XV-1254-07.
- AISC 360-22, Appendix 3; AS 4100 §11; ASME BPVC VIII Div. 2.
- Budynas, R. e Nisbett, J. K., Shigley's Mechanical Engineering Design, cap. 6.
- Paris, P. e Erdogan, F. (1963); Barsom, J. M. e Rolfe, S. T., Fracture and Fatigue Control in Structures.
- Smith, K. N., Watson, P. e Topper, T. H. (1970).
- Engelhardt, M. D. (2007), FEMA 350; AISC 341-16 §K2.4b (protocolo de carga).
- Thornton, W. A. e Muir, L. S., AISC Manual Part 13 (Método da Força Uniforme).
- Fichas do Mestrado em Engenharia Estrutural e da Construção (UPC) citadas por WorkID nas docstrings de `tests/`.

## Licença

MIT. Consulte [LICENSE](LICENSE).

---

Parte do **Loadpath**, a coleção de bibliotecas estruturais de código aberto de [Jesús Murgas](https://github.com/jmurgass99).
