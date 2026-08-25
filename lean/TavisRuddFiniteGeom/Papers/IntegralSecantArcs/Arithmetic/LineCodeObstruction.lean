import Mathlib.Tactic

/-!
# Arithmetic checks for the characteristic-three line-code obstruction

This module checks the centered moment expansions, the exact shell
cancellation, and the terminal three-line phase boundary.  It does not define
the projective-plane line code, import the Szőnyi--Weiner theorem, or formalize
the geometric support and positive-line counts.
-/

namespace TavisRuddFiniteGeom.Papers.IntegralSecantArcs

/-- Expansion of the total centered multiplicity. -/
theorem centeredMoment_sum (r δ j : ℤ) :
    (9 * r ^ 2 + 3 * r + 1) + 3 * (3 * r ^ 2 + 4 * r + δ) -
        (3 * r + 1) * (6 * r + j) =
      (9 - 3 * j) * r + 3 * δ - j + 1 := by
  ring

/-- Expansion of the squared centered multiplicity. -/
theorem centeredMoment_norm (r δ j : ℤ) :
    (9 * r ^ 2 + 3 * r + 1) + 15 * (3 * r ^ 2 + 4 * r + δ) +
        (6 * r + j) ^ 2 - (15 * r + 8) * (6 * r + j) =
      (15 - 3 * j) * r + 15 * δ + j ^ 2 - 8 * j + 1 := by
  ring

/-- Expansion of the centered multiplicity over the arc. -/
theorem centeredMoment_internalSum (r δ j : ℤ) :
    4 * (3 * r ^ 2 + 4 * r + δ) - (2 * r + 1) * (6 * r + j) =
      (10 - 2 * j) * r + 4 * δ - j := by
  ring

/-- Exact arithmetic form of the centered shell defect. -/
theorem shellDefect_identity (r δ j : ℤ) :
    ((15 - 3 * j) * r + 15 * δ + j ^ 2 - 8 * j + 1) +
          ((9 - 3 * j) * r + 3 * δ - j + 1) -
        2 * ((10 - 2 * j) * r + 4 * δ - j) =
      (4 - 2 * j) * r + 2 + 10 * δ + j * (j - 7) := by
  ring

/-- The shell lower-bound expression collapses to a quantity independent of
the size displacement.  This is twice the manuscript identity. -/
theorem threeLine_shellCollapse (r δ j : ℤ) :
    4 * ((10 - 2 * j) * r + 4 * δ - j) -
      ((4 - 2 * j) * r + 2 + 10 * δ + j * (j - 7)) -
      2 * ((9 - 3 * j) * r + 3 * δ - j + 1) =
      18 * r - (j - 1) * (j - 4) := by
  ring

/-- Three necessary generator lines and the signed capacity bound force the
normalized displacement to be at least `1/3`. -/
theorem threeLine_phaseBoundary (t : ℤ) (α : ℚ)
    (hlower : 3 ≤ t) (hupper : (t : ℚ) ≤ 1 + 6 * α) :
    (1 / 3 : ℚ) ≤ α := by
  have hlowerQ : (3 : ℚ) ≤ t := by exact_mod_cast hlower
  linarith

/-- Once the asymptotic upper bound is strictly below four, the integral line
count forced above by three is exactly three. -/
theorem threeLine_rigidityBoundary (t : ℤ) (hlower : 3 ≤ t) (hupper : t < 4) :
    t = 3 := by
  omega

/-- The old modular coefficient plus the line-code displacement is `5/3`. -/
theorem characteristicThree_finalCoefficient :
    (4 / 3 : ℚ) + 1 / 3 = 5 / 3 := by
  norm_num

end TavisRuddFiniteGeom.Papers.IntegralSecantArcs
