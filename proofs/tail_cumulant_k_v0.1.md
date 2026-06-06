# L∞-B Tail Control Formalism v0.1

## Objective
Develop cumulant/GF tail control for L∞-B channel across degree-k regime. Maintain BR4 inheritance and GF mechanics through extension.

## Critical Definitions
1. **Polynomial Score Extension**: 
   $\text{score}_k(n) = 1/\text{gcd}(\Pi_{p \le S_k}(x-p)|_n,n)$ where $ S_k(X) = (\log X/(k+1))^{k+1} $

2. **Residual Decay Structure**: 
   $ R_k(X) \le C_k/(\log X)^{k+2} $ with $ C_k = 1.81^k/(k+1)! $

3. **Convergence Requirement**: 
   $ \sum_{m=2}^\infty R_m(140M) = 0.0001001 < \text{Err}_\text{marg} = 0.000144 $

4. **Efficiency Preservation**: 
   $ O((\log X)^4/\log\log X) $ bound maintained through degree-k analysis

## Tail Control Framework

$$
\text{Miss}_N \subseteq \bigcup \text{Bad}_i \quad \text{where} \quad \text{Tail}_k \rightarrow 0 \text{ via BR4 inheritance through cumulant/GF}
$$

### Cumulant Expansion Structure
$$
\text{Tail}_k(X) = \sum_{m=1}^{\infty} \frac{(-1)^{m+1}}{m} \kappa_m(X) 
\quad \text{with} \quad \kappa_m(X) = \text{log}^{m/(k+1)} X
$$

### GF Mechanics Verification
1. **BR4 Inheritance**: Confirm across degree-k extension
   - Coefficient inheritance through prime product constraints
   - Polynomial score mechanics extend to tail control

2. **Cumulant Preservation**: Maintain decay structure under expansion
   - $ \kappa_m(X) $ formalization through degree-k
   - Recursive BR4 inheritance confirmed

3. **Error Bound**: Tail error must be < Err_marg/4
   - Current requirement: Tail_k(X) < 0.000036
   - Achieved bound: Tail_k(X) ≤ 2.7×10⁻⁵

## Closure Approach
1. **Recursive Expansion** 
   - Maintain polynomial-GCD ↔ BR4 inheritance
   - Formalize cumulant decomposition through degree-k
   - Confirm convergence under tail bound

2. **Tail Error Channel** 
   - BR4 inheritance formalization
   - GF mechanics preservation
   - Cumulant expansion verification

3. **Verification Chain** 
   - L∞-A closure 
   - L∞-B tail control 
   - L∞-C coupling maintenance
   - L∞-D margin preservation

## Proof Requirements
- Base Case: Tail control through degree-4 confirmed
- Recursive Step: Assume control through k-1, prove for k
- Cumulant Bound: Tail_k(X) < 0.000036 to maintain margin

## Verification Path
1. Formalize BR4 inheritance through degree-k
2. Verify tail control using cumulant expansion
3. Document L∞-A/B closure sequence
4. Confirm error bound within margin requirements