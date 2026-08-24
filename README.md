# Integral Secant Distributions and Improved Bounds for Complete (k,n)-Arcs

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.22087679-blue.svg)](https://doi.org/10.5281/zenodo.22087679)

## Read the paper

[**Open the paper (PDF) →**](integral_secant_arcs.pdf)

**Title:** *Integral Secant Distributions and Improved Bounds for Complete
(k,n)-Arcs*

A `(k,n)`-arc is a set of `k` points in a finite projective plane with at most
`n` points on any line. It is complete when every external point lies on an
`n`-secant. The paper studies the full family of `n`-secants through its two
integer degree distributions: the numbers incident with points of the arc and
with points of its complement.

The principal application is

```text
t_{2q/3+1}(2,q) ≥ q²/3 + 4q/3 − o(q)       (q = 3^h → ∞).
```

Equivalently, for every `epsilon > 0`, all sufficiently large powers
`q = 3^h` satisfy

```text
k ≥ q²/3 + (4/3 − epsilon)q
```

for every complete `(k,2q/3+1)`-arc in `PG(2,q)`. The classical real
incidence bound gives only `q²/3 + q + O(1)` in this regime.

## Why the integer distribution matters

The standard incidence estimate replaces the secant degrees by quadratic
averages. Here the exact block-pair count is split between the arc and its
complement, and each side is bounded by the sharp integer convex envelope for
its degree sum. The real relaxation recovers the classical design incidence
bound. Retaining the integer remainders gives a positive linear correction on
the rational equality families with integral limiting degrees.

For an ordered factorization `lambda = uv`, put

```text
q = (u+v+1)m,          n = (u+1)m + 1.
```

If every external point lies on at least `lambda` `n`-secants, the paper gives
an explicit divisor-indexed bound

```text
k ≥ u(u+v+1)m² + c_Z(u,v)m − O_{u,v}(1),
```

whose linear coefficient is strictly larger than that of the real incidence
bound. On characteristic-compatible branches, the Szőnyi--Weiner stability
theorems reduce near equality to a bounded modular repair. Completeness then
forces a linear secant excess for every point in the repair support.

## Main consequences

- The integer incidence condition holds for every selected block family in a
  symmetric design; the classical real inequality is its relaxation.
- Ordered positive factorizations `lambda = uv` classify the rational equality
  families whose limiting internal degree is an integer greater than
  `lambda`.
- Over `q = 3^h`, ordinary completeness gives
  `t_{2q/3+1}(2,q) ≥ q²/3 + 4q/3 − o(q)`.
- Over `q = 2^h`, if every external point of a `(k,3q/4+1)`-arc lies on at
  least two maximal secants, then
  `k ≥ q²/2 + (73/48 − epsilon)q` for all sufficiently large `h`.
- Complementation gives bounds for minimal multiple blocking sets. The same
  incidence theorem bounds robust nonextendibility of projective codes by the
  number of minimum-weight hyperplanes through a candidate extension column.
- A classical two-character duality corollary reconstructs an exact complete
  arc and its full maximal-secant family from the high-character lines. It
  does not solve inverse realization after a bounded modular repair.

[`REVIEWER_GUIDE.md`](REVIEWER_GUIDE.md) gives a short route through the proof
and an explicit checklist for the balancing-branch crossing, secant-number
localization, exceptional-line estimate, imported stability hypotheses,
repair-support argument, and evidence boundary.

## Proof and evidence boundary

The manuscript contains human proofs of the complete theorem chain. The
paper-local Lean 4 package in [`lean/`](lean/) checks arithmetic fragments:
integer balancing and interval overlap, rational substitutions and coefficient
identities, and the terminal characteristic-three and characteristic-two
affine minima.

The formal claim map reports 18 manuscript claims: 12 absent and 6
fragmentary, with none classified as complete. Lean does not formalize finite
projective planes, complete `(k,n)`-arcs, the exceptional-line estimate, the
Szőnyi--Weiner stability theorems, repair support, or the asymptotic geometric
reductions. No imported literature theorem is introduced as a Lean axiom. See
[`lean/README.md`](lean/README.md) and
[`lean/verification/claims.json`](lean/verification/claims.json).

The exact Python evidence bundle independently checks the finite algebra and
declared bounded grids used while developing the proofs. It is not a premise
of a theorem, does not search for projective arcs, and does not verify the
imported modular-stability theorems. The exact outside inputs and convention
matches are recorded in
[`verification/imported-sources.json`](verification/imported-sources.json).

## Verification

From this directory, run

```text
make check
```

This lints the manuscript, replays the exact-arithmetic evidence, validates
the source-level formal correspondence and claim map, rebuilds the PDF with a
fixed source date, and rejects TeX warnings. It does not claim a fresh Lean
kernel build; the pinned formal package has separate guarded build and axiom
audit instructions in [`lean/README.md`](lean/README.md).

## Files

- `integral_secant_arcs.pdf` is the compiled paper.
- `integral_secant_arcs.tex` is the manuscript driver.
- `sections/` contains the incidence theorem, arc applications, modular
  arguments, translations, and conclusion.
- `formal-annotations.tex` defines the nonprinting claim-coverage macros.
- `REVIEWER_GUIDE.md` maps the load-bearing proof and trust checks.
- `lean/` is the pinned Mathlib-only partial formal companion.
- `verification/` contains exact evidence and source-level trust checks.
- `.zenodo.json` contains deposit metadata.

## Citation

The concept DOI for all versions is
[`10.5281/zenodo.22087679`](https://doi.org/10.5281/zenodo.22087679). The
first release, `v0.1.0`, has version DOI
[`10.5281/zenodo.22087680`](https://doi.org/10.5281/zenodo.22087680).

## License

The contents of this repository are licensed under the Creative Commons
Attribution 4.0 International License; see [`LICENSE`](LICENSE).
