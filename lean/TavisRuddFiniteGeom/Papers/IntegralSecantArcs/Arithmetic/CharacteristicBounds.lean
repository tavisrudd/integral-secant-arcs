import Mathlib.Tactic

/-!
# Discrete coefficient bounds in characteristics three and two

The projective-geometric arguments reduce their final coefficient estimates to
minimizing maxima of two affine functions over an integer offset.  This module
proves those discrete minimizations from the residue or parity condition on
the repair support.

It does not formalize the modular stability theorems, the construction of the
dual secant set, or the geometric lower bound on repair support.
-/

namespace TavisRuddFiniteGeom.Papers.IntegralSecantArcs

/-- If a nonzero characteristic-three correction has support at least two in
the residue class `h = 1 mod 3` and support at least one otherwise, the two
affine lower bounds force coefficient at least four. -/
theorem characteristicThree_affine_bounds
    (h r : ℤ) (hr : 1 ≤ r) (hresidue : h % 3 = 1 → 2 ≤ r) :
    (4 : ℚ) ≤ max ((18 + (h : ℚ)) / 5) (3 - (h : ℚ) + (r : ℚ)) := by
  by_cases hhigh : 2 ≤ h
  · apply le_max_of_le_left
    have hhighQ : (2 : ℚ) ≤ h := by exact_mod_cast hhigh
    linarith
  by_cases hlow : h ≤ 0
  · apply le_max_of_le_right
    have hlowQ : (h : ℚ) ≤ 0 := by exact_mod_cast hlow
    have hrQ : (1 : ℚ) ≤ r := by exact_mod_cast hr
    linarith
  · have hh : h = 1 := by omega
    have hr2 : 2 ≤ r := hresidue (by omega)
    apply le_max_of_le_right
    have hr2Q : (2 : ℚ) ≤ r := by exact_mod_cast hr2
    norm_num [hh]
    linarith

/-- On odd offsets, the characteristic-two pair-count and repair bounds force
coefficient at least `73/6`. -/
theorem characteristicTwo_odd_affine_bounds
    (h : ℤ) (hodd : h % 2 = 1) :
    (73 / 6 : ℚ) ≤ max ((76 + (h : ℚ)) / 6) (9 - (h : ℚ)) := by
  by_cases hhigh : -3 ≤ h
  · apply le_max_of_le_left
    have hhighQ : (-3 : ℚ) ≤ h := by exact_mod_cast hhigh
    linarith
  · have hlow : h ≤ -5 := by omega
    apply le_max_of_le_right
    have hlowQ : (h : ℚ) ≤ -5 := by exact_mod_cast hlow
    linarith

/-- On even offsets, the characteristic-two pair-count and repair bounds force
coefficient at least `37/3`. -/
theorem characteristicTwo_even_affine_bounds
    (h : ℤ) (heven : h % 2 = 0) :
    (37 / 3 : ℚ) ≤ max ((76 + (h : ℚ)) / 6) (10 - (h : ℚ)) := by
  by_cases hhigh : -2 ≤ h
  · apply le_max_of_le_left
    have hhighQ : (-2 : ℚ) ≤ h := by exact_mod_cast hhigh
    linarith
  · have hlow : h ≤ -4 := by omega
    apply le_max_of_le_right
    have hlowQ : (h : ℚ) ≤ -4 := by exact_mod_cast hlow
    linarith

end TavisRuddFiniteGeom.Papers.IntegralSecantArcs
