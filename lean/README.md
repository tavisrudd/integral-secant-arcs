# Lean companion to *Integral Secant Distributions and Line-Code Obstructions for Complete (k,n)-Arcs*

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
characteristic-two discrete affine minimizations. It also checks the centered
moment expansions, exact shell cancellation, and the terminal three-line phase
boundary in the characteristic-three line-code obstruction. These are
kernel-checked arithmetic statements.

This is a partial formal companion. It does not define finite projective
planes or complete `(k,n)`-arcs, and it does not formalize the modular repair
theorems, the exact small-codeword theorem, the line-code geometry, or the
asymptotic reductions from the geometric hypotheses to the arithmetic bounds.
No literature theorem is declared as a Lean axiom.

Checked coverage snapshot: 23 claims; 13 absent; 10 fragmentary; 0 conditional;
0 complete; 20 reviewer terminals, of which 5 are machinery serving no current
manuscript claim.

Within the monorepo, do not invoke Lean or Lake directly.  From the monorepo
root, queue the public interface and axiom audit through the repository build
front door:

```text
lean/scripts/lean-build-queue.py build \
  TavisRuddFiniteGeom.Papers.IntegralSecantArcs.PaperInterface \
  TavisRuddFiniteGeom.Papers.IntegralSecantArcs.Verification.AxiomAudit \
  --lean-root "$PWD/papers/integral_secant_arcs/lean" --cores 20-23
```

The standalone paper repository does not bundle the monorepo build scheduler;
its `make check` target therefore runs the source-level correspondence gate but
does not claim a fresh kernel build.

The manuscript correspondence and expected-axiom baseline are checked with

```text
python3 verification/check_formal_artifact.py --source-only
python3 verification/check_formal_artifact.py --axiom-log AXIOM_AUDIT_OUTPUT
```
