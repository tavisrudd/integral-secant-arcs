import Mathlib.Tactic

/-!
# Arithmetic of rational equality parameters

This module checks the rational parameter family indexed by positive factors
`u` and `v`.  It verifies the two continuous equality equations and the exact
factorization comparing the two displayed first-order coefficients.

Only the rational identities and positivity statement are formalized here.
The converse classification of every rational solution and the passage from
these identities to finite projective arcs are outside this module.
-/

namespace TavisRuddFiniteGeom.Papers.IntegralSecantArcs

/-- The four rational parameters attached to positive factors `u` and `v`. -/
def rationalEqualityParameters (u v : ℚ) : ℚ × ℚ × ℚ × ℚ :=
  ((u + 1) / (u + v + 1), u / (u + v + 1), u * v, (u + 1) * (v + 1))

/-- The factor-indexed parameters satisfy both continuous equality equations
for the incidence relaxation. -/
theorem rationalEqualityParameters_satisfy_equations
    (u v : ℚ) (hu : 0 < u) (hv : 0 < v) :
    let α := (u + 1) / (u + v + 1)
    let β := u / (u + v + 1)
    let lam := u * v
    let a := (u + 1) * (v + 1)
    a = lam * α * (1 - β) / ((1 - α) * β) ∧
      lam * (α - β) ^ 2 = β * (1 - α) := by
  dsimp
  have hu0 : u ≠ 0 := ne_of_gt hu
  have hv0 : v ≠ 0 := ne_of_gt hv
  have hd0 : u + v + 1 ≠ 0 := by nlinarith
  constructor <;> field_simp [hu0, hv0, hd0] <;> ring

/-- The difference between the balanced integer coefficient and the real
incidence coefficient has the displayed positive factorization. -/
theorem coefficient_difference_factorization
    (u v : ℚ) (hu : 0 < u) (hv : 0 < v) :
    let balanced :=
      u * (u * v ^ 2 + 4 * u * v + 2 * u + 2 * v ^ 2 + 4 * v + 1) /
        (2 * u * v + u + v)
    let incidence := u * (u * v + 3 * u + 2 * v + 3) / (2 * u + 1)
    let difference :=
      u * (v + 1) * (u ^ 2 + u + 1) /
        ((2 * u + 1) * (2 * u * v + u + v))
    balanced - incidence = difference ∧ 0 < difference := by
  dsimp
  have hden₁ : 2 * u + 1 ≠ 0 := by nlinarith
  have hden₂ : 2 * u * v + u + v ≠ 0 := by nlinarith [mul_pos hu hv]
  constructor
  · field_simp
    ring
  · positivity

end TavisRuddFiniteGeom.Papers.IntegralSecantArcs
