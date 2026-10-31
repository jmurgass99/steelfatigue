"""Elegir la categoría de detalle desde el catálogo FAT del paquete y ver qué vida da cada una.

El catálogo `wohler_db` contiene 12 categorías de EN 1993-1-9 con una descripción
y un uso típico. Se busca por palabra clave («atiesador», «tope», «perno»), se
consulta una categoría por código y se compara la vida N para un mismo rango de
tensión de 100 MPa. Las descripciones son resúmenes: la asignación definitiva se
hace con las Tablas 8.1 a 8.10 de la norma.

Ejecutar:  python examples/select_detail_category_from_catalogue.py
"""
from steelfatigue.ec3_sn import ec3_cycles_to_failure
from steelfatigue.wohler_db import list_fat_categories, lookup_fat, recommend_for_detail

DELTA_SIGMA = 100.0


def main() -> None:
    print("Catálogo FAT (EN 1993-1-9):")
    for fat in list_fat_categories():
        n = ec3_cycles_to_failure(DELTA_SIGMA, fat)
        n_txt = "∞" if n == float("inf") else f"{n:.2e}"
        print(f"  {fat.code:>8}  {fat.description:<48} N(Δσ={DELTA_SIGMA:.0f}) = {n_txt}")

    for needle in ("atiesador", "tope", "perno"):
        hits = recommend_for_detail(needle)
        print(f"\nBúsqueda «{needle}»: {', '.join(f.code for f in hits) or 'sin resultados'}")

    fat = lookup_fat("fat 71")
    print(f"\nlookup_fat('fat 71') → {fat.code}: {fat.description} / {fat.typical_use}")
    print(f"lookup_fat('FAT 999') → {lookup_fat('FAT 999')}")


if __name__ == "__main__":
    main()
