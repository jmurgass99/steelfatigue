"""
sn_curves.py - S-N Curves and Cumulative Damage Evaluation based on EN 1993-1-9.
"""
from .exceptions import DetailCategoryError, SpectrumError
from .rainflow_fatpack import rainflow_count_arrays, _HAS_FATPACK


class FatigueEvaluator:
    """
    Evaluates fatigue life of structural steel details.
    """
    def __init__(self, detail_category: float, gamma_mf: float = 1.35):
        """
        :param detail_category: Detail category (Delta Sigma C in MPa), e.g., 71, 80, 90, 112.
        :param gamma_mf: Partial safety factor for fatigue strength.
        :raises DetailCategoryError: if ``detail_category`` or ``gamma_mf`` <= 0.

        A non-positive detail category is ZERO fatigue resistance. Left
        unvalidated it made ``calculate_endurance`` return N <= 0, which the
        ``if n_capacity > 0`` guard in :meth:`calculate_damage` silently skipped
        -> D = 0.0 -> ``"status": "PASS"`` and ``"Fatigue life is adequate"``.
        The same validation already lived in
        :mod:`steelfatigue.services.fatigue_service`; it belongs here too, because
        this class is public and usable directly.
        """
        if detail_category <= 0:
            raise DetailCategoryError(
                f"detail_category debe ser > 0 (recibido {detail_category}): "
                "una categoria de detalle nula o negativa es resistencia a "
                "fatiga NULA y no puede producir un veredicto PASS."
            )
        if gamma_mf <= 0:
            raise DetailCategoryError(
                f"gamma_mf debe ser > 0 (recibido {gamma_mf})"
            )
        self.detail_category = detail_category
        self.gamma_mf = gamma_mf
        
    def calculate_endurance(self, stress_range: float) -> float:
        """
        Calculates the maximum number of cycles (N) for a given stress range (Delta Sigma).
        Based on standard bilinear S-N curves (m=3 for N < 5e6).
        """
        # Detail category corresponds to N = 2e6 cycles
        N_c = 2e6
        m = 3.0
        
        # Design fatigue strength
        delta_sigma_c_d = self.detail_category / self.gamma_mf
        
        if stress_range <= 0:
            return float('inf')
            
        # N = N_c * (Delta Sigma C / Delta Sigma)^m
        N = N_c * ((delta_sigma_c_d / stress_range) ** m)
        return N

    def calculate_damage(self, stress_spectrum: list[dict]) -> float:
        """
        Calculates Palmgren-Miner cumulative damage.
        :param stress_spectrum: List of dicts [{'stress_range': 80, 'cycles': 100000}, ...]
        :return: Damage factor D. If D > 1.0, failure occurs.
        :raises SpectrumError: if a block omits 'stress_range' or 'cycles'.

        Both keys are REQUIRED. They used to be read with ``.get(key, 0)``, so a
        block missing either one contributed zero damage and vanished from the
        sum without a trace: a missing stress range became "0 MPa" (N = inf) and
        a missing cycle count became "0 cycles". An absent datum is not a zero.
        An explicit 0.0 supplied by the caller IS a datum and is still accepted.
        """
        total_damage = 0.0
        for i, block in enumerate(stress_spectrum):
            for key in ('stress_range', 'cycles'):
                if key not in block:
                    raise SpectrumError(
                        f"bloque {i} del espectro sin la clave '{key}': "
                        f"{block!r}. Un dato ausente no es un cero; declara el "
                        "valor explicitamente si de verdad vale 0."
                    )
            sigma = block['stress_range']
            n_applied = block['cycles']

            n_capacity = self.calculate_endurance(sigma)
            if n_capacity <= 0:
                # Inalcanzable tras validar detail_category > 0 en __init__.
                # Se deja ruidoso a proposito: una capacidad nula es dano
                # INFINITO, nunca dano cero.
                raise SpectrumError(
                    f"bloque {i}: capacidad nula o negativa (N={n_capacity}) "
                    f"para stress_range={sigma}; el dano seria infinito."
                )
            total_damage += n_applied / n_capacity

        return total_damage

    def count_rainflow_fatpack(self, stress_history):
        """Usa fatpack (ASTM E1049-85) para el conteo rainflow.

        Devuelve (means, ranges, counts) como np.array.
        Recomendado para validacion contra ASTM E1049.

        Coexiste con el resto de la API; no sustituye a calculate_damage,
        sino que ofrece una via alternativa para construir el espectro
        a partir de una historia temporal de tensiones.
        """
        if not _HAS_FATPACK:
            raise ImportError("instalar fatpack>=0.7")
        return rainflow_count_arrays(stress_history)

    def evaluation_report(self, stress_spectrum: list[dict]) -> dict:
        """
        Complete evaluation report.
        """
        d = self.calculate_damage(stress_spectrum)
        return {
            "detail_category": self.detail_category,
            "total_damage": round(d, 4),
            "status": "PASS" if d <= 1.0 else "FAIL",
            "message": "Fatigue life exhausted" if d > 1.0 else "Fatigue life is adequate"
        }
