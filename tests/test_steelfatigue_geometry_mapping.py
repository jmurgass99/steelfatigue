"""Tests para HotspotMeshMapping en SteelFatigue."""
from steelfatigue.geometry_mapping import SemanticWeldToe, build_hotspot_crack_mesh


def test_hotspot_mesh_mapping_refinement():
    weld = SemanticWeldToe("WELD-1", plate_thickness_mm=20.0, detail_category_MPa=80.0, nominal_stress_range_MPa=100.0)
    nodes_4, map_4, sum_4 = build_hotspot_crack_mesh(weld=weld, points_per_zone=4)
    nodes_12, map_12, sum_12 = build_hotspot_crack_mesh(weld=weld, points_per_zone=12)

    assert len(nodes_4) == 4
    assert len(nodes_12) == 12
    assert len(map_12.weld_toe_to_points["WELD-1"]) == 12
    assert sum_4["hotspot_stress_MPa"] > 100.0
    assert abs(sum_4["hotspot_stress_MPa"] - sum_12["hotspot_stress_MPa"]) < 1e-6
    assert sum_12["final_crack_size_mm"] > 1.0
