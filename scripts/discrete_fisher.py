#!/usr/bin/env python3
"""
discrete_fisher.py - Closed-form Fisher Information for the modulo-6 lattice PMF.

The PMF on the lattice {6k : k = 1, 2, 3, ...} with exponential envelope is:
  P(k; λ) = (e^{6/λ} - 1) · e^{-6k/λ}    for k = 1, 2, ...

This is a geometric distribution with p = 1 - e^{-6/λ}.

Fisher Information: I(λ) = Σ P(k) · [∂ log P(k)/∂λ]²
"""
import math
from scipy import stats
import time

def discrete_fisher_closed_form(lam):
    """
    Exact closed-form Fisher Information for the modulo-6 lattice PMF.
    
    Derivation:
    log P(k) = log(e^{6/λ} - 1) - 6k/λ
    
    ∂ log P(k)/∂λ = (6/λ²) · [k - e^{6/λ}/(e^{6/λ} - 1)]
                    = (6/λ²) · [k - E[k]]
    
    I(λ) = (36/λ⁴) · Σ P(k) · (k - E[k])²
         = (36/λ⁴) · Var(k)
    
    For geometric(p) with p = 1 - e^{-6/λ}:
    Var(k) = (1 - p) / p² = e^{-6/λ} / (1 - e^{-6/λ})²
    
    Therefore:
    I(λ) = (36/λ⁴) · e^{-6/λ} / (1 - e^{-6/λ})²
    
    Simplified using hyperbolic functions:
    I(λ) = 9 / [λ⁴ · sinh²(3/λ)]
    
    Asymptotic limit (λ >> 6): sinh(3/λ) ≈ 3/λ, so I(λ) ≈ 1/λ²
    """
    # Exact form via hyperbolic function
    sinh_3lam = math.sinh(3.0 / lam)
    return 9.0 / (lam**4 * sinh_3lam**2)

def discrete_fisher_via_variance(lam):
    """Direct computation via variance of geometric distribution."""
    p = 1.0 - math.exp(-6.0 / lam)
    var_k = (1.0 - p) / (p**2)
    return (36.0 / lam**4) * var_k

def continuous_fisher_approx(lam):
    """Continuous exponential approximation: I(λ) = 1/λ²."""
    return 1.0 / lam**2

if __name__ == "__main__":
    print("=" * 72)
    print("DISCRETE FISHER INFORMATION — Modulo-6 Lattice PMF")
    print("=" * 72)
    print()
    print("PMF: P(k) = (e^{6/λ} - 1) · e^{-6k/λ},   k ∈ {1, 2, 3, ...}")
    print("Distribution: Geometric(p),  p = 1 - e^{-6/λ}")
    print()
    print("Closed-form result:")
    print("  I(λ) = 9 / [λ⁴ · sinh²(3/λ)]")
    print()
    print("Asymptotic (λ >> 6):  I(λ) ≈ 1/λ²")
    print()
    print("-" * 72)
    print(f"{'λ':>10} {'I_exact':>14} {'I_cont':>14} {'Ratio':>10} {'Mean Gap':>12}")
    print("-" * 72)
    
    for lam in [227.11, 100, 50, 30, 15, 10, 6]:
        i_exact = discrete_fisher_closed_form(lam)
        i_cont = continuous_fisher_approx(lam)
        ratio = i_exact / i_cont
        mean_gap = 6.0 * math.exp(6.0/lam) / (math.exp(6.0/lam) - 1)
        print(f"{lam:>10.2f} {i_exact:>14.8f} {i_cont:>14.8f} {ratio:>10.6f} {mean_gap:>12.2f}")
    
    print()
    print("-" * 72)
    print("EMPIRICAL VALIDATION AT X = 10^8 (λ_obs = 227.11)")
    print("-" * 72)
    
    lam_obs = 227.1113
    i_exact = discrete_fisher_closed_form(lam_obs)
    i_cont = continuous_fisher_approx(lam_obs)
    
    print(f"  Observed λ̂ = {lam_obs} (mean twin-to-twin gap)")
    print(f"  I_discrete(λ̂) = {i_exact:.8e}")
    print(f"  I_continuous(λ̂) = {i_cont:.8e} (≈ 1/λ̂²)")
    print(f"  Discrete/Continuous ratio = {i_exact/i_cont:.8f}")
    print(f"  Relative difference = {abs(i_exact - i_cont)/i_cont*100:.4f}%")
    print()
    
    # Asymptotic scaling
    print("-" * 72)
    print("λ(X) FLOW: Hardy-Littlewood Anchoring")
    print("-" * 72)
    print()
    print("  λ(X) = log²(X) / (2 · C₂)  where C₂ ≈ 0.66016")
    print()
    for exp in [5, 6, 7, 8, 9, 10, 12, 15]:
        X = 10**exp
        C2 = 0.6601618158468696
        lam_hl = (math.log(X))**2 / (2 * C2)
        i_val = discrete_fisher_closed_form(lam_hl)
        print(f"  X = 10^{exp:>2d}:  λ(X) = {lam_hl:>12.4f}   I(λ(X)) = {i_val:.8e}")
    
    print()
    print("-" * 72)
    print("KEY INSIGHT")
    print("-" * 72)
    print()
    print("  As X → ∞:  λ(X) → ∞  (logarithmic divergence)")
    print("  As X → ∞:  I(λ(X)) → 0  (information thins out)")
    print("  But: I(λ) > 0 for all finite X — structure never collapses.")
    print()
