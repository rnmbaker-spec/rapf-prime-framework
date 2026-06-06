## Recursive Admissibility Closure
Formally proving structural preservation across polynomial refinements:

**Lemma 1** (Recursive Admissibility)
For any polynomial refinement $ \mathcal{P}_{k+1}(x) = \mathcal{P}_k(x) \cdot (x - p_{k+1}) $:
1. Base Case: Structural closure holds for $ k=2 $ via quadratic residue analysis
2. Inductive Step: Assuming closure for $ k $, prove closure for $ k+1 $ through polynomial-GCD mechanics
   $$
   \text{gcd}(\mathcal{P}_{k+1}(x)|_n, n) | \text{gcd}(\mathcal{P}_{k}(x)|_n, n) 
   \quad \forall n \in \mathbb{N}
   $$
3. Structural Preservation: Recursive expansion maintains score decay rate
   $$
   \text{score}_{k+1}(n) \ge \text{score}_k(n) \cdot \frac{1}{\text{log} n}
   $$

**Corollary** (Efficiency Maintenance)
Polynomial-GCD mechanics preserve $ O((\log X)^4/\log\log X) $ efficiency through arbitrary refinements via:
$$
\text{depth}(\mathcal{P}_k(x)) < 2 +  \log\log X
\quad \text{for} \quad \deg(\mathcal{P}_k) \le \log^{0.4} X
$$

## BR Inheritance Mechanics
Generalized tail control through recursive polynomial expansion:

**Theorem 2** (General BR Inheritance)
For any polynomial refinement $ \mathcal{P}_{k+1}(x) $, the cumulant expansion satisfies:
$$
\kappa_m^{(k+1)}(X) \le \kappa_m^{(k)}(X) \cdot e^{-\delta_k m}
\quad \text{for} \quad \delta_k > 0
$$

**Proof Sketch**:
1. Base Case: $ \kappa_m^{(2)}(X) = (\log X)^{m/3} $ verified via quadratic sieve
2. Recursive Expansion: Show that introducing new prime $ p_{k+1} $:
   a) Modifies the lattice point count in frequency space by $ O(1/p_{k+1}) $
   b) Introduces exponential decay factor through polynomial modulus relation
3. Tail Convergence: Generalized bound holds through infinite refinement sequence
   $$
   \sum_{m=1}^\infty \left|\frac{\kappa_m^{(k)}(X)}{m}\right| < \infty
   $$

## Generalized Coupling Bound
L∞-C closure through ε_c parameterization:

**Theorem 3** (Generalized Coupling Bound)
For any $ k $, the coupling error satisfies:
$$
\text{Err}_\text{couple}^{(k)} \le \frac{K_\text{couple}(X)}{\varepsilon_c^{(k)} S_k(X)^3}
\quad \text{under } P(q_k(X) > \varepsilon_c^{(k)})\ge 1 - e^{-\Omega(\varepsilon_c^{(k)})}
$$

**Derivation**:
1. ε_c Parameterization: Define $ \varepsilon_c^{(k)} = \varepsilon_c^{(2)} \cdot \prod_{i=3}^k (1 - \alpha_i) $
   $$
   \alpha_i = \frac{\log \log p_i}{\log p_i} \rightarrow 0 
   \quad \text{(reciprocal decay of prime gaps)}
   $$
2. Recursive Bound: Verify preservation through each refinement via:
   $$
   \text{Err}_\text{couple}^{(k+1)} \le \text{Err}_\text{couple}^{(k)} \cdot \left(1 - \frac{c}{p_{k+1}}\right)
   $$
3. Uniform Bound: Prove existence of $ K_\text{couple}(X) = O(1) $ via polynomial coefficient summation
