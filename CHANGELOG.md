# Changelog

## 1.1.0 — 2026-10-31

Correcciones encontradas al ejecutar los casos de uso del README.

- `rainflow_fatpack.rainflow_count`: el residuo (inversiones sin cerrar) se cuenta ahora como semiciclos consecutivos, como pide ASTM E1049-85 §5.4.4. Antes se recorría de dos en dos y se perdía uno de cada dos tramos, incluido el de mayor rango de la señal. En el ejemplo del estándar el recuento pasa de 2,5 a 4,0 ciclos y reproduce su tabla. El daño calculado desde historias de tensión sube en consecuencia.
- `paris_law.integrate_paris`: ΔK se evalúa en MPa·√m y da/dN en m/ciclo, coherentes con la C por defecto (Barsom & Rolfe, 6,9·10⁻¹²). Antes ΔK iba en MPa·√mm con la misma C y la vida salía dividida por √1000 = 31,6. Nuevo test contra la forma cerrada.
- `lowcycle.CoffinMansonRBS.evaluate`: sin aviso de división por cero cuando la historia contiene rotaciones plásticas nulas.
- 29 casos de uso ejecutados en `examples/` con su salida en `examples/output/`; README reescrito; metadatos del paquete alineados.

## 1.0.0

Publicación inicial como repositorio independiente (origen: FatigueJm del monorepo Structural JM).
