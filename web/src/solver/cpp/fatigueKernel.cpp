// C++ / WebAssembly kernel para ciclos S-N pendiente 3 EN 1993-1-9 y paso de crecimiento de grieta Paris
extern "C" {
  double snCyclesSlope3(double delta_sigma_c, double delta_sigma) {
    double ratio = delta_sigma_c / delta_sigma;
    return 2000000.0 * ratio * ratio * ratio;
  }

  double parisCrackStep(double C_val, double delta_K_cubed, double dN) {
    return C_val * delta_K_cubed * dN;
  }
}
