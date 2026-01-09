# Common Mistakes in Math Problems

This document lists frequent errors students make when solving JEE-style problems. The solver and verifier agents reference this to catch issues early and explain why certain approaches fail.

## Algebra

### Quadratic Equations Mistakes
- **Sign error in quadratic formula**: Using x = (-b ± √(b² - 4ac)) / a instead of 2a. Remember the denominator is always 2a, not just a.
- **Forgetting both roots**: After solving (x - 2)(x - 3) = 0, students sometimes write only x = 2 and forget x = 3. Always list all solutions.
- **Incorrect factorization**: Writing x² - 5x + 6 = (x - 2)(x - 2) is wrong. Check by expanding: we need (x - 2)(x - 3).
- **Dividing by the variable**: Never divide both sides by x or any variable that could be zero. This loses solutions.

### Polynomial Operations
- **Expanding brackets incorrectly**: (x + 2)² is NOT x² + 4. It's x² + 4x + 4. Use the formula (a + b)² = a² + 2ab + b².
- **Sign mistakes with negatives**: -(x + 2) = -x - 2, not -x + 2. The negative distributes to both terms.
- **Canceling incorrectly**: You can only cancel common factors in multiplication/division, not in addition. (x² + 2x) / (x + 1) cannot be simplified by canceling x from numerator with x in denominator.

### Logarithm Mistakes
- **log(a + b) ≠ log(a) + log(b)**: Logarithms only split products and quotients, not sums. log(ab) = log(a) + log(b), but log(a + b) stays as is.
- **Forgetting the domain**: log(x) is only defined for x > 0. If you get a negative value under the log, the solution is invalid.
- **Base confusion**: log₁₀(100) = 2 means 10² = 100. Always check what base you're using.
- **Changing bases incorrectly**: logₐ(x) = log(x) / log(a), not log(x) - log(a).

## Probability

### Counting Mistakes
- **Confusing permutation and combination**: Use permutation P(n,r) when order matters (arranging people in a line). Use combination C(n,r) when order doesn't matter (choosing a team). Always think: "Does the order matter?"
- **Overcounting**: When choosing 2 people from 5, it's C(5,2) = 10, not 5 × 4 = 20. We divide by 2! because choosing person A then B is the same as B then A.
- **Wrong total count**: If rolling two dice, there are 6 × 6 = 36 total outcomes, not 12. Multiply the possibilities, don't add.

### Probability Calculation Errors
- **P(A or B) mistake**: P(A ∪ B) = P(A) + P(B) - P(A ∩ B), not just P(A) + P(B). You must subtract the overlap or you double-count.
- **Forgetting conditional probability**: "Given that X happened" means use P(A|B) = P(A ∩ B) / P(B), not just P(A).
- **Independence assumption**: Two events are independent only if explicitly stated. Don't assume independent unless told.
- **Probability outside [0,1]**: If you calculate a probability > 1 or < 0, something is wrong. Check your work.

### Bayes' Theorem Mistakes
- **Wrong formula**: Don't use P(A|B) = P(A) × P(B|A). The correct formula is P(A|B) = P(B|A) × P(A) / P(B).
- **Forgetting the denominator**: P(B) is NOT always P(B|A). You must calculate P(B) = Σ P(B|Aᵢ) × P(Aᵢ) over all cases.

## Calculus

### Derivative Mistakes
- **Power rule confusion**: d/dx(x³) = 3x², not 3x³. The exponent comes down and decreases by 1.
- **Chain rule forgotten**: d/dx(sin(2x)) ≠ cos(2x). You must use the chain rule: d/dx(sin(2x)) = cos(2x) × 2 = 2cos(2x).
- **Product rule error**: d/dx(x × sin(x)) = 1 × sin(x) + x × cos(x), not sin(x) + cos(x). Use u'v + uv' properly.
- **Quotient rule signs**: d/dx(u/v) = (u'v - uv') / v², not (uv' - u'v) / v². The numerator order matters.

### Integration Mistakes
- **Forgetting the constant**: ∫ x dx = x²/2 + C, not x²/2. Always add the constant of integration.
- **Wrong power rule**: ∫ x³ dx = x⁴/4 + C, not x⁴/3 + C. Increase the exponent by 1, then divide by the new exponent.
- **Limits in definite integrals**: ∫₀¹ x dx = [x²/2]₀¹ = 1/2 - 0 = 1/2. Evaluate at the upper limit first, then subtract the lower limit value.

### Optimization Mistakes
- **Skipping second derivative test**: Finding f'(x) = 0 gives critical points, but you must check f''(x) to confirm it's max or min (or use endpoints/context).
- **Forgetting domain restrictions**: If the problem says x > 0, don't include x = 0 or negative solutions even if they satisfy the equation.
- **Local vs global maximum**: A local maximum found by calculus might not be the global maximum. Always check endpoints and compare all critical points.

## Linear Algebra

### Matrix Operation Mistakes
- **Order matters in multiplication**: A × B ≠ B × A. Matrix multiplication is not commutative.
- **Determinant of product**: det(A × B) = det(A) × det(B), but det(A + B) ≠ det(A) + det(B).
- **Inverse formula error**: For [a b; c d], the inverse is NOT [1/a 1/b; 1/c 1/d]. The correct formula is 1/(ad-bc) × [d -b; -c a].
- **Assuming invertible**: A matrix is invertible only if det(A) ≠ 0. Don't assume you can find A⁻¹.

### System of Equations
- **Wrong number of solutions**: If rank(A) < n variables, there are infinite solutions, not unique. Don't forget this case.
- **Inconsistent systems**: If rank(A) ≠ rank(augmented), the system has no solution. Check consistency first.

## General Problem-Solving

- **Not checking the answer**: Always substitute your solution back into the original equation to verify.
- **Domain ignored**: Keep track of restrictions like x ≠ 0, x > 0, 0 < p < 1. Reject solutions outside the domain.
- **Incomplete solutions**: Write all steps clearly. Show how you got each intermediate result.
- **Calculator errors**: Verify numerical calculations. Round appropriately at the end, not intermediate steps.
- **Misreading the question**: Read carefully what the problem asks for (solve for x? find the sum? maximize?). Answering the wrong question loses marks.