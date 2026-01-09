# Solution Pattern: Conditional Probability and Bayes' Theorem

This document outlines the standard approaches for solving conditional probability problems, which frequently appear in JEE exams. Understanding these patterns helps recognize problem types and apply the correct method.

## Pattern 1: Basic Conditional Probability

**When to use**: When you need to find the probability of event A given that event B has already occurred.

**Definition**: Conditional probability P(A|B) means "the probability of A happening given that B has happened."

**Formula**: P(A|B) = P(A ∩ B) / P(B), where P(B) ≠ 0

**Understanding the formula**: 
- P(A ∩ B) is the probability that both A and B occur
- P(B) is the total probability of B occurring
- We're restricting our sample space to only the cases where B happened, then finding what fraction of those also have A

**Steps to solve**:
1. Identify events A and B clearly
2. Find the probability of both occurring: P(A ∩ B)
3. Find the probability of B occurring: P(B)
4. Divide: P(A|B) = P(A ∩ B) / P(B)
5. Simplify and interpret

**Example**: A card is drawn from a standard deck. Given that it's a red card, what's the probability it's an ace?
- Event A: Card is an ace
- Event B: Card is red
- There are 52 cards total, 26 are red, 2 are red aces
- P(A ∩ B) = 2/52 (red aces)
- P(B) = 26/52 (red cards)
- P(A|B) = (2/52) / (26/52) = 2/26 = 1/13
- Check: Of the 26 red cards, 2 are aces, so 2/26 = 1/13 ✓

---

## Pattern 2: Using Independence to Simplify

**When to use**: When events A and B are independent (one doesn't affect the other).

**Key property**: If A and B are independent, then P(A|B) = P(A)

**Why?** Because if B happening doesn't change the probability of A, then knowing B occurred doesn't help predict A.

**Example of independent events**:
- Rolling two dice: the result of the first die doesn't affect the second
- Drawing cards with replacement: putting the card back makes each draw independent
- Weather tomorrow vs. stock market today: typically unrelated

**Example**: A coin is flipped and a die is rolled. Given that the die showed 4, what's the probability the coin showed heads?
- Events are independent (coin flip doesn't affect die roll)
- P(Heads | Die = 4) = P(Heads) = 1/2
- The die result tells us nothing about the coin

**When NOT to use this pattern**: If replacing the first item matters or if there's any connection between events, they're likely dependent.

---

## Pattern 3: Two-Stage Problems (Tree Diagrams)

**When to use**: When events happen in sequence and the probability of the second event depends on what happened in the first.

**Method**: Create a probability tree showing all branches and their probabilities.

**Steps**:
1. Draw the first stage with all possible outcomes and their probabilities
2. From each first-stage outcome, draw branches for the second stage
3. The probability on each second-stage branch is the conditional probability
4. To find final probability, multiply along the path
5. To find total probability of an event, sum all paths leading to it

**Example**: An urn contains 3 red balls and 2 blue balls. Two balls are drawn without replacement. Find P(both red).

```
First draw: P(Red) = 3/5
  Second draw (if first was red): P(Red|first red) = 2/4 = 1/2
  
First draw: P(Blue) = 2/5
  Second draw (if first was blue): P(Red|first blue) = 3/4
```

To find P(both red):
- Follow the "Red then Red" path: (3/5) × (2/4) = 6/20 = 3/10

**Complete solution with all possibilities**:
- P(both red) = (3/5) × (2/4) = 3/10
- P(red then blue) = (3/5) × (2/4) = 3/10
- P(blue then red) = (2/5) × (3/4) = 6/20 = 3/10
- P(both blue) = (2/5) × (1/4) = 2/20 = 1/10
- Total: 3/10 + 3/10 + 3/10 + 1/10 = 10/10 = 1 ✓

---

## Pattern 4: Bayes' Theorem (Reversing Conditional Probability)

**When to use**: When you know P(B|A) but need to find P(A|B). This is about "updating beliefs with new information."

**Formula**: P(A|B) = P(B|A) × P(A) / P(B)

**Extended form (with multiple causes)**: 
If A₁, A₂, ..., Aₙ are mutually exclusive and exhaustive events:

P(Aᵢ|B) = P(B|Aᵢ) × P(Aᵢ) / Σⱼ[P(B|Aⱼ) × P(Aⱼ)]

**Interpretation**:
- P(A): Prior probability (what we believed before new information)
- P(B|A): Likelihood (how likely the new information is if A is true)
- P(B): Total probability of the new information
- P(A|B): Posterior probability (updated belief after seeing new information)

**Example - Disease Testing**: 
A medical test correctly identifies a disease 99% of the time. The disease affects 1% of the population. If someone tests positive, what's the probability they actually have the disease?

Define events:
- D: Person has disease
- T: Person tests positive

Given information:
- P(D) = 0.01 (disease prevalence)
- P(T|D) = 0.99 (test accuracy when disease present)
- P(T|¬D) = 0.01 (false positive rate)

Find: P(D|T) = probability of disease given positive test

Step 1: Calculate P(T) using law of total probability
- P(T) = P(T|D) × P(D) + P(T|¬D) × P(¬D)
- P(T) = 0.99 × 0.01 + 0.01 × 0.99
- P(T) = 0.0099 + 0.0099 = 0.0198

Step 2: Apply Bayes' theorem
- P(D|T) = P(T|D) × P(D) / P(T)
- P(D|T) = 0.99 × 0.01 / 0.0198
- P(D|T) = 0.0099 / 0.0198
- P(D|T) ≈ 0.50 or 50%

**Key insight**: Even though the test is 99% accurate, a positive result only gives 50% chance of having the disease because the disease is rare. This is why rare diseases need confirmatory tests!

---

## Pattern 5: Total Probability Rule

**When to use**: When you need to find the probability of an event B that can occur through multiple disjoint paths (mutually exclusive causes).

**Formula**: P(B) = Σᵢ P(B|Aᵢ) × P(Aᵢ)

Where A₁, A₂, ..., Aₙ partition the sample space (they cover all cases without overlap).

**Steps**:
1. Identify all mutually exclusive paths that lead to event B
2. For each path, calculate P(B|Aᵢ) × P(Aᵢ)
3. Sum all these products

**Example**: A factory has three machines producing items. Machine 1 produces 50% and has 2% defect rate. Machine 2 produces 30% and has 3% defect rate. Machine 3 produces 20% and has 5% defect rate. Find the probability a random item is defective.

- P(Defect) = P(Defect|M1)×P(M1) + P(Defect|M2)×P(M2) + P(Defect|M3)×P(M3)
- P(Defect) = 0.02×0.50 + 0.03×0.30 + 0.05×0.20
- P(Defect) = 0.01 + 0.009 + 0.01
- P(Defect) = 0.029 or 2.9%

---

## Pattern 6: Multi-Stage Conditional Probability

**When to use**: When multiple events happen in sequence, each affected by previous outcomes.

**Approach**: Extend the tree diagram to three or more stages, multiplying probabilities along paths.

**Example**: Three cards are drawn from a deck without replacement. Find P(all three are aces).

- P(1st ace) = 4/52
- P(2nd ace | 1st ace) = 3/51
- P(3rd ace | first two aces) = 2/50
- P(all three aces) = (4/52) × (3/51) × (2/50) = 24/132600 = 1/5525

**Verification**: This should be quite small (only 4 aces in 52 cards), and it is.

---

## Common Pitfalls in Conditional Probability

**Confusion 1**: P(A|B) ≠ P(B|A). These are not the same! Use Bayes' theorem to convert.

**Confusion 2**: Not accounting for sample space reduction. When you condition on B, your sample space shrinks to only outcomes where B occurs.

**Confusion 3**: Assuming independence when events are dependent. Always check if one event affects the probability of another.

**Confusion 4**: Forgetting to divide by P(B) in conditional probability formula. This is required to properly scale the probability.