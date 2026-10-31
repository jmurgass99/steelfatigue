"""
Base de datos de curvas Wöhler (S-N) — FAT categories EN 1993-1-9.

Detail Categories Δσ_C (MPa) a N_C = 2·10⁶ ciclos.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FATDetail:
    code: str             # 'FAT 90', 'FAT 71' etc.
    delta_sigma_C: float  # MPa
    description: str
    typical_use: str


FAT_DATABASE: dict[str, FATDetail] = {
    "FAT 160": FATDetail("FAT 160", 160,
                          "Acero base, sin soldadura",
                          "Vigas laminadas, sección bruta"),
    "FAT 140": FATDetail("FAT 140", 140,
                          "Soldadura a tope longitudinal continuo",
                          "Cordón longitudinal pleno"),
    "FAT 125": FATDetail("FAT 125", 125,
                          "Soldadura a tope transversal calidad B",
                          "Empalmes vigas calidad alta"),
    "FAT 112": FATDetail("FAT 112", 112,
                          "Cordón a tope con plancha respaldo",
                          "Conexiones intermedias"),
    "FAT 100": FATDetail("FAT 100", 100,
                          "Soldadura cruciforme con full penetration",
                          "Refuerzos cruzados"),
    "FAT 90":  FATDetail("FAT 90",  90,
                          "Soldadura de filete + transverse stiffener",
                          "Atiesadores transversales"),
    "FAT 80":  FATDetail("FAT 80",  80,
                          "Soldadura filete longitudinal",
                          "Atiesadores longitudinales"),
    "FAT 71":  FATDetail("FAT 71",  71,
                          "Soldadura a tope transversal con offset",
                          "Empalmes simples"),
    "FAT 63":  FATDetail("FAT 63",  63,
                          "Pernos pretensados ASTM A325/A490",
                          "Conexiones a fricción"),
    "FAT 50":  FATDetail("FAT 50",  50,
                          "Soldadura a corte filete con carga",
                          "Conexiones cargadas en corte"),
    "FAT 45":  FATDetail("FAT 45",  45,
                          "Pernos no pretensados a corte",
                          "Conexiones snug-tight"),
    "FAT 36":  FATDetail("FAT 36",  36,
                          "Detalles severos / áreas de concentración",
                          "Categoría más conservadora"),
}


def lookup_fat(code: str) -> FATDetail | None:
    return FAT_DATABASE.get(code.upper())


def list_fat_categories() -> list[FATDetail]:
    return list(FAT_DATABASE.values())


def recommend_for_detail(use_case: str) -> list[FATDetail]:
    """Búsqueda fuzzy en descripción y typical_use."""
    needle = use_case.lower()
    matches = []
    for fat in FAT_DATABASE.values():
        if (needle in fat.description.lower()
                or needle in fat.typical_use.lower()):
            matches.append(fat)
    return matches


__all__ = ["FATDetail", "FAT_DATABASE", "lookup_fat",
           "list_fat_categories", "recommend_for_detail"]
