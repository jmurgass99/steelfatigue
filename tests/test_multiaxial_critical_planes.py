"""Findley y Brown-Miller se maximizan en su propio plano, no en el plano crítico de SWT."""
import numpy as np
import pytest

from steelfatigue.multiaxial import brown_miller_parameter, critical_plane_search, findley_parameter


def _history():
    t = np.linspace(0.0, 2.0 * np.pi, 73)
    return {"sxx": list(50 + 50 * np.sin(t)), "syy": [0.0] * 73, "sxy": list(80 * np.cos(t))}


def _brute(h, n=180, E=200_000.0, nu=0.30):
    sx, sy, sxy = (np.asarray(h[k]) for k in ("sxx", "syy", "sxy"))
    G = E / (2 * (1 + nu))
    pf, pbm = [], []
    for th in np.linspace(0, np.pi, n, endpoint=False):
        c, s = np.cos(th), np.sin(th)
        sn = sx * c * c + sy * s * s + 2 * sxy * c * s
        tn = -(sx - sy) * s * c + sxy * (c * c - s * s)
        pf.append(findley_parameter((tn.max() - tn.min()) / 2, sn.max()))
        pbm.append(brown_miller_parameter((tn.max() - tn.min()) / G, (sn.max() - sn.min()) / E))
    return max(pf), max(pbm)


def test_findley_and_brown_miller_are_maxima_over_all_planes():
    h = _history()
    r = critical_plane_search(h, n_angles=180, include_shear=True)
    pf, pbm = _brute(h)
    assert r["findley_MPa"] == pytest.approx(pf)
    assert r["brown_miller"] == pytest.approx(pbm)
    # en este caso el plano de Findley no es el de SWT (antes se devolvía 65,4 en vez de 110)
    assert r["findley_theta_rad"] != pytest.approx(r["theta_rad"])
    assert r["findley_MPa"] == pytest.approx(110.0, rel=1e-6)
