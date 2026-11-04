# Limitaciones conocidas de steelfatigue

Lo que el paquete no hace o hace de forma simplificada.

- `rainflow_count` usa por defecto `fatpack`, que cuantiza las inversiones en 64 niveles entre el mínimo y el máximo de la señal: los rangos salen con un error de hasta un 1,6 % del rango máximo (el número de ciclos no se ve afectado). Con `use_float64_exact=True` cuenta con la regla de 4 puntos de ASTM E1049 sin cuantizar.
- `services.hotspot_service` estima por defecto la vida con una recta de pendiente única m = 3; con `use_trilinear_ec3=True` usa la curva trilineal de EN 1993-1-9.
- Los K_t de `notch_stress` son ajustes propios del paquete por tipo de cordón, no las tablas de IIW; las categorías de entalla asignadas a AISC, AS y NSR son equivalencias del paquete.
- Los factores ambientales de `corrosion` son orientativos. Para proyecto, usar las curvas en agua de mar de la norma aplicable.
- `paris_law`: Y constante y sin efecto de la relación de tensiones R; el umbral `delta_K_th_MPa_sqrt_m` vale 0 por defecto (sin umbral); la C por defecto es la cota superior de Barsom-Rolfe para aceros ferrítico-perlíticos.
- `lowcycle.CoffinMansonRBS` convierte rotación plástica en deformación con un factor geométrico constante (0,5 por defecto); los parámetros por defecto son los de A992.
- `multiaxial.critical_plane_search` toma ε = σ/E en el plano normal (elástico) para SWT; con `include_shear=True` añade Findley (k = 0,30 por defecto) y Brown-Miller con Δγ = Δτ/G, también elásticos. Cada criterio se maximiza en su propio plano: hasta la 1.1.0 Findley y Brown-Miller se evaluaban en el plano de SWT (110 MPa → 65,4 MPa en el test de regresión).
- `sn_curves.FatigueEvaluator` es la implementación heredada de pendiente única sin codo ni cut-off; para EN 1993-1-9 usa `ec3_sn`.
- `gusset_rbs` duplica UFM y Coffin-Manson con fórmulas simplificadas por compatibilidad; las versiones de referencia están en `lowcycle`. Desde la 1.1.2 `FatigueRBS` cuenta ciclos como `lowcycle` (hasta la 1.1.1 tomaba inversiones por ciclos y daba la mitad del daño). Con σ′_f > 0 suma Basquin a la capacidad, pero compara con la deformación plástica: es una aproximación del lado inseguro.
- EN 1993-1-10: T_Ed se simplifica al término dominante T₀ − ΔT_r; los demás términos del Anexo A y la Tabla 2.1 completa no están en el paquete.
