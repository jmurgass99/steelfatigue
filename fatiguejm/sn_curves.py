"""
sn_curves.py - S-N Curves and Cumulative Damage Evaluation based on EN 1993-1-9.
"""
from .rainflow_fatpack import rainflow_count_arrays, _HAS_FATPACK


class FatigueEvaluator:
    """
    Evaluates fatigue life of structural steel details.
    """
    def __init__(self, detail_category: float, gamma_mf: float = 1.35):
        """
        :param detail_category: Detail category (Delta Sigma C in MPa), e.g., 71, 80, 90, 112.
        :param gamma_mf: Partial safety factor for fatigue strength.
        """
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
        """
        total_damage = 0.0
        for block in stress_spectrum:
            sigma = block.get('stress_range', 0)
            n_applied = block.get('cycles', 0)
            
            n_capacity = self.calculate_endurance(sigma)
            if n_capacity > 0:
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
