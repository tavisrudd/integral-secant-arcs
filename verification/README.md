# Verification

Every theorem in the manuscript has a mathematical proof.  The deterministic
bundle `check_integral_secant_distributions.py`, `integral-secant-checks.json`,
and `integral-secant-checks.sha256` independently checks the finite algebra and
bounded parameter grids used while developing those proofs.

From this directory (or from the root of the standalone repository), run

```text
nix shell nixpkgs#python3 --command \
  python3 verification/check_integral_secant_distributions.py check
```

The check uses only Python's standard library and exact integer/rational
arithmetic.  It covers 5,386 direct convex-minimum instances, 1,368 bounded
degree instances, 600 congruence-restricted instances, 25,494 polynomial
identities, 246 raw first-order expansions, 144 characteristic-three
zero-repair cases and 1,580 sharp line-code shell, cancellation, and phase
boundary instances, the seven exact endpoint candidate rows, three endpoint
field instances, and the centered moment rows at
\(q=81,243,729\).  The JSON
records every declared search domain and count.  These finite checks do not
prove existence or unrestricted nonexistence of a projective arc.

`imported-sources.json` records the exact source loci and convention matches
for every external theorem used in the manuscript.  `evidence.json` records
the role and replay command of the computational bundle.

The adjacent `lean/` directory is a pinned Mathlib-only partial companion.
Its static correspondence gate checks every theorem-like manuscript statement,
the formal coverage annotations, reviewer declarations, expected axiom lists,
and the dependency graph. Checked coverage snapshot: 24 claims; 14 absent; 10
fragmentary; 0 conditional; 0 complete; 20 reviewer terminals, of which 5 are
machinery serving no current manuscript claim.
