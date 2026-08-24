import Mathlib.Tactic

/-!
# Integer bounds for selected-block degree sequences

For an integer degree `z`, `twicePairCount z = z * (z - 1)` is twice the
number of unordered pairs incident with that point.  This module proves the
unit-transfer identity behind balancing, a lower bound for every integer
degree sequence with prescribed sum, and the interval-overlap consequence of
an exact partition of the total pair count.

The results are purely arithmetic.  They do not construct a block design or
prove the geometric double-counting identity that supplies the total pair
count in an incidence structure.
-/

namespace TavisRuddFiniteGeom.Papers.IntegralSecantArcs

open scoped BigOperators

/-- Twice the binomial pair count associated with an integer degree. -/
def twicePairCount (z : ℤ) : ℤ := z * (z - 1)

/-- Moving one unit from degrees `x` to `y`, where `y + 2 ≤ x`, decreases
twice the pair count by `2 * (x - y - 1)`. -/
theorem twicePairCount_unit_transfer (x y : ℤ) :
    twicePairCount x + twicePairCount y =
      twicePairCount (x - 1) + twicePairCount (y + 1) + 2 * (x - y - 1) := by
  simp [twicePairCount]
  ring

/-- The product of two consecutive integers in descending order is
nonnegative. -/
theorem consecutiveIntegerProduct_nonnegative (x : ℤ) : 0 ≤ x * (x - 1) := by
  by_cases hx : x ≤ 0
  · exact mul_nonneg_of_nonpos_of_nonpos hx (by omega)
  · exact mul_nonneg (by omega) (by omega)

/-- Exact decomposition of twice the pair count around an integer level
`a`.  The remainder is a sum of nonnegative consecutive-integer products. -/
theorem twicePairCount_balancing_decomposition {ι : Type*} [Fintype ι]
    (z : ι → ℤ) (a w : ℤ)
    (hsum : ∑ i, z i = (Fintype.card ι : ℤ) * a + w) :
    ∑ i, twicePairCount (z i) =
      (Fintype.card ι : ℤ) * a * (a - 1) + 2 * a * w +
        ∑ i, (z i - a) * (z i - a - 1) := by
  simp only [twicePairCount]
  calc
    ∑ i, z i * (z i - 1) =
        ∑ i, (a * (a - 1) + 2 * a * (z i - a) +
          (z i - a) * (z i - a - 1)) := by
            apply Finset.sum_congr rfl
            intro i _
            ring
    _ = (Fintype.card ι : ℤ) * a * (a - 1) + 2 * a * w +
        ∑ i, (z i - a) * (z i - a - 1) := by
          simp only [Finset.sum_add_distrib, Finset.sum_const, nsmul_eq_mul]
          rw [← Finset.mul_sum]
          simp only [Finset.sum_sub_distrib, Finset.sum_const, nsmul_eq_mul,
            Finset.card_univ, hsum]
          ring

/-- If an integer degree sequence has sum `N*a + w`, then its twice-pair
count is at least `N*a*(a-1) + 2*a*w`.  For `0 ≤ w < N`, dividing by two is
the balanced formula with `N-w` entries `a` and `w` entries `a+1`. -/
theorem balanced_twicePairCount_lower {ι : Type*} [Fintype ι]
    (z : ι → ℤ) (a w : ℤ)
    (hsum : ∑ i, z i = (Fintype.card ι : ℤ) * a + w) :
    (Fintype.card ι : ℤ) * a * (a - 1) + 2 * a * w ≤
      ∑ i, twicePairCount (z i) := by
  rw [twicePairCount_balancing_decomposition z a w hsum]
  have hnonnegative : 0 ≤ ∑ i, (z i - a) * (z i - a - 1) :=
    Finset.sum_nonneg fun i _ ↦ consecutiveIntegerProduct_nonnegative (z i - a)
  omega

/-- Exact interval overlap forced by a partition `internal + external = total`
of a pair count.  The witness is the actual external pair count. -/
theorem integerPairIntervals_overlap
    (internal external total internalMin internalMax externalMin externalMax : ℤ)
    (hpartition : internal + external = total)
    (hinternalMin : internalMin ≤ internal)
    (hinternalMax : internal ≤ internalMax)
    (hexternalMin : externalMin ≤ external)
    (hexternalMax : external ≤ externalMax) :
    ∃ value : ℤ,
      externalMin ≤ value ∧ value ≤ externalMax ∧
      total - internalMax ≤ value ∧ value ≤ total - internalMin := by
  refine ⟨external, hexternalMin, hexternalMax, ?_, ?_⟩ <;> omega

end TavisRuddFiniteGeom.Papers.IntegralSecantArcs
