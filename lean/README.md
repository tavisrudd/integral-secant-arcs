# Lean companion to *Integral Secant Distributions and Improved Bounds for Complete (k,n)-Arcs*

This Mathlib-only package is the paper-owned formal companion. Its
reviewer-facing entry point is

```text
TavisRuddFiniteGeom.Papers.IntegralSecantArcs.PaperInterface
```

and its axiom audit is

```text
TavisRuddFiniteGeom.Papers.IntegralSecantArcs.Verification.AxiomAudit
```

The package proves the integer unit-transfer and balancing identities, the
abstract pair-interval overlap, the rational parameter substitutions and
coefficient factorization, and the characteristic-three and
characteristic-two discrete affine minimizations. These are kernel-checked
arithmetic statements.

This is a partial formal companion. It does not define finite projective
planes or complete `(k,n)`-arcs, and it does not formalize the modular
stability theorems or the asymptotic reductions from the geometric hypotheses
to the arithmetic bounds. No literature theorem is declared as a Lean axiom.

Checked coverage snapshot: 17 claims; 11 absent; 6 fragmentary; 0 conditional;
0 complete; 12 reviewer terminals, of which 5 are machinery serving no current
manuscript claim.

From this directory, build the public interface and axiom audit with

```text
nix develop --command lake build \
  TavisRuddFiniteGeom.Papers.IntegralSecantArcs.PaperInterface \
  TavisRuddFiniteGeom.Papers.IntegralSecantArcs.Verification.AxiomAudit
```

The manuscript correspondence and expected-axiom baseline are checked with

```text
python3 verification/check_formal_artifact.py --source-only
python3 verification/check_formal_artifact.py --axiom-log AXIOM_AUDIT_OUTPUT
```
