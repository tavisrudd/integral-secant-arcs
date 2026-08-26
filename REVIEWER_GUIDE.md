# A referee's route through the proof

The manuscript proves an exact integer necessary condition for a selected
block family in a symmetric design and applies it to the family of
`n`-secants of a complete `(k,n)`-arc.  The characteristic-three and
characteristic-two bounds add modular stability to that necessary condition.

## A first pass

Read the three theorem statements in
[`sections/01-introduction.tex`](sections/01-introduction.tex), then the pair
identity and integer feasibility condition in
[`sections/03-maximal-secants.tex`](sections/03-maximal-secants.tex).  The
rational parameter calculation is in
[`sections/04-rational-parameters.tex`](sections/04-rational-parameters.tex).
The load-bearing modular-repair step is in Section 5, the ternary line-code
obstruction is in Section 6, and the characteristic-two argument follows it.

## Nine checks

1. **What integer information survives the real incidence bound?**
   The interval-overlap condition uses the actual pair count as a witness in
   two intervals determined by exact integer extrema.  It does not claim that
   every integer between those extrema is attainable.  The closed
   balancing-remainder formula identifies the nonnegative residue term
   discarded by the real relaxation.
2. **Where do the rational equality parameters come from?**
   Lemma 4.1 classifies triples with integral limiting average internal degree
   `a > lambda`.  Under that hypothesis, factoring the integral discriminant
   gives an ordered factorization `lambda = uv` in positive integers.  The
   manuscript makes no classification claim for rational nonintegral `a`.
3. **Why is the number of `n`-secants localized?**
   Lemma 4.2 fixes explicit bounds `C,K` for the first-order coefficient and
   constant remainder.  It bounds `F(T_0)` by `Am`, uses the exact floor-sum
   forward difference through `T_0+vm`, and then proves that the real lower
   bound for the forward difference is positive for every later `T`.  Thus it
   proves `T = ud(v+1)m + O_{u,v,C,K}(1)` uniformly over the bounded family.
   Before applying the lemma in Theorem 1.2, the classical incidence bound
   supplies `c_m >= c_mix - O_{u,v}(m^-1)`; the automatic case supplies the
   upper bound.  Hence the lemma's two-sided boundedness hypothesis holds
   with `e_m=0`.
   In the subsequent coefficient calculation, the balanced internal degrees
   can cross from `(a-1,a)` to `(a,a+1)`.  The display labelled
   `eq:pair-linear` uses equality on the first branch and the convex
   supporting-line lower bound on the second; it does not identify the two
   branches.
4. **Why are there only `O(q)` exceptional dual lines?**
   Proposition `prop:rational-family-stability` packages the general
   characteristic-compatible argument.  The pair identity writes `-F(T)` as
   the sum of two nonnegative balancing losses.  The exact balancing-loss
   identity charges every degree outside the adjacent balanced pair; the proof
   displays the pointwise inequality that also controls their total absolute
   deviation.  The signed internal deviation and external excess then count
   the wrong member of each adjacent pair.  This is the step to check before
   applying either
   modular stability theorem.
5. **Do the imported repair theorems apply?**
   Section 5 records the Szőnyi--Weiner hypotheses `q=p^e>27`, `e>1`, their
   exceptional-line threshold, and the exact support size
   `ceil(delta/(q+1))`.  Section 6 records the even-type threshold and support
   size.  Since `delta=O(q)`, both thresholds hold eventually and the support
   size is bounded; the proofs pass to a subsequence on which it is fixed.
6. **Where does completeness enter after repair?**
   Lemma `lem:repair-support` dualizes every repair-support point to a primal
   line.  Away from
   intersections of those lines, the dual line contains exactly one support
   point, whose correction coefficient is nonzero modulo `p`; hence its
   original residue is wrong.  The external lower degree then forces positive
   secant excess.  This produces the additional linear term.  For `d=p^j`
   and `q=p^e=dm`, one has `m=p^(e-j)`, so the leading term of `T` vanishes
   modulo `p` once `e>j`; the display `eq:support-one-obstruction` then rules
   out support one in one residue class.
7. **Are the final constants correct?**
   The characteristic-three proof minimizes two affine bounds over the three
   residue classes.  The characteristic-two proof separates odd and even
   repair support.  The exact Python evidence bundle and the Lean fragments
   independently check these terminal arithmetic calculations, but neither
   substitutes for the preceding geometric proof.
8. **What creates the new `5/3` coefficient?**
   Section `sec:line-code-obstruction` centers the full maximal-secant degree
   vector at the former `4/3` bound.  The exact moments give its norm and a
   nonnegative shell defect.  Szőnyi--Weiner Theorem 4.3 represents the
   residue word on a bounded number `t` of distinct lines.  The first
   pointwise shell inequality forces `t>=3`; the signed norm correction and
   the arc cap give `t<=1+6 alpha+o(1)`.  Hence the displacement is at least
   `q/3-o(q)`, and combining this with the Section 5 lower side gives
   `4/3+1/3=5/3`.  The paper does not claim that `5/3` is optimal.
9. **What happens at the exact `5/3` endpoint?**
   Proposition `prop:exact-five-thirds-endpoint` reduces equality to six
   signed three-line rows.  Exact norm and arc-cap inequalities exclude
   concurrence; the connector-pencil equations leave two triangular rows,
   and their degree spectra violate the arc cap.  This excludes zero repair,
   not positive sublinear repair.
10. **What inverse realization is actually proved?**
   Proposition `prop:two-character-inverse` treats an exact two-character
   point set in the dual plane.
   Summing its line characters through one dual point reconstructs the primal
   arc and proves that the dual point set is exactly its full maximal-secant
   family.  The proposition does not assert that a bounded repair of a modular
   core is realizable; that perturbed inverse problem remains open.

## Outside inputs

The proof imports the Bishnoi--Mattheus--Schillewaert real incidence bound only
for comparison and imports two Szőnyi--Weiner modular repair theorems and the
exact small-codeword theorem in the headline applications.
[`verification/imported-sources.json`](verification/imported-sources.json)
records the source location, hypotheses, and convention match for each import.
The manuscript states the integer necessary condition before deriving the
classical real inequality as a corollary.

## Formal and computational boundary

The adjacent Lean package is a partial formal companion.  Its public interface
is
[`PaperInterface.lean`](lean/TavisRuddFiniteGeom/Papers/IntegralSecantArcs/PaperInterface.lean),
and [`claims.json`](lean/verification/claims.json) gives the exact
manuscript-to-declaration map.  It classifies 24 manuscript claims as 14 absent
and 10 fragmentary; none is complete.  Lean checks integer balancing and
interval overlap, forward rational substitutions and coefficient algebra, and
the terminal affine minima.  It also checks the centered-moment expansions,
exact shell cancellation, phase boundary, and terminal rigidity integrality.  It
does not formalize projective planes, `(k,n)`-arcs, the exceptional-line
estimate, any imported repair or small-codeword theorem, the line-code
geometry, repair support, or the asymptotic reductions.

[`expected_axioms.txt`](lean/verification/expected_axioms.txt) is the baseline
for a captured kernel audit, not evidence of a fresh run by itself.  The
paper-local static gate checks statement digests, coverage annotations,
declarations, and the dependency graph.  The repository-wide trust registry
adopts the manuscript labels and claim manifest but does not advertise the
paper-local Lean declarations as portfolio terminals until that registry has
an extraction unit for adjacent packages.

The exact Python bundle checks finite integer/rational identities and bounded
test domains recorded in JSON.  It neither proves the asymptotic theorems nor
searches for projective arcs.  See
[`verification/README.md`](verification/README.md).

## Replay

From the paper or standalone repository root, run:

```text
make check
```

This replays the exact evidence checker, the source-level formal
correspondence gate, the pinned manuscript build, and the TeX-warning gate.  A
fresh Lean kernel build and axiom transcript use the guarded repository Lean
workflow described in [`lean/README.md`](lean/README.md); `make check` does not
claim to perform that build.

## Hypothesis-smuggling checklist

- Keep `a in Z`, `a > lambda`, and `u,v in Z_{>0}` in the rational
  classification.
- Keep `A,B` nonempty and `T>0` when dividing in the real relaxation.
- Check that the coefficient of `T` is positive before substituting the
  coverage lower bound for `T` in the classical relaxation.
- Treat pair-count intervals as necessary enclosing intervals, not as sets of
  all attainable values.
- Normalize modular correction support by deleting zero coefficients modulo
  `p` before applying the repair-support lemma.
- Keep signed deficiencies signed; the characteristic-two even restriction
  costs `|D|/2` internally.
- In the even-type lemma, `D ≥ 0` gives the balanced pair `{5,6}`; `D < 0`
  gives `{6,7}`, where the displayed affine slack is an upper bound.  The
  characteristic-two theorem's contradiction range proves `D > 0` before
  using `{5,6}`.
- Pass to a subsequence before calling the bounded repair-support size fixed.
- In the line-code section, use the full family of maximal secants, verify that
  the centered residue belongs to the ternary line code, and apply the exact
  small-codeword theorem only after checking its exponent and weight threshold.
- Keep the line representation on distinct lines and absorb discrepancies
  between its integral sum and the balanced residue only at their bounded set
  of pairwise intersections.
- Treat the line-code result as a two-sided forbidden band; obtain the final
  one-sided lower bound only by combining it with the modular-repair lower
  side.  Do not infer optimality of `5/3`.
- In the endpoint proposition, keep the six signed rows exact, distinguish
  concurrent from triangular generators, and apply the connector-pencil
  equations before either final arc-cap contradiction.
- Fix uniform bounds for both the first-order coefficient and constant
  remainder before invoking the secant-number localization lemma.
- Require a spanning point set for the stated rank-three projective-code
  translation.
- Do not use the Lean fragments or finite computational checks as premises for
  the geometric or asymptotic steps.
