# Integral Secant Distributions and Improved Bounds for Complete (k,n)-Arcs

This directory contains the manuscript source and its verification materials.
The paper studies complete `(k,n)`-arcs through the
numbers of \(n\)-secants through each point.  Its principal
application is the lower bound

\[
t_{2q/3+1}(2,q)\ge q^2/3+4q/3-o(q)
\]

over the tower \(q=3^h\).

Referees can start with [`REVIEWER_GUIDE.md`](REVIEWER_GUIDE.md), which maps
the load-bearing proof steps, imported results, formal coverage, computational
evidence, and hypothesis checks to their owning files.

From this directory, build the manuscript with:

```text
make manuscript
```

Run the complete paper gate with:

```text
make check
```

From the monorepo root, prefix either target with
`make -C papers/integral_secant_arcs`.

The `lean/` directory contains a pinned Mathlib-only partial formal companion.
Its reviewer interface checks the integer balancing and interval-overlap core,
the rational coefficient identities, and the final discrete affine
minimizations. The Lean README and claim map state the exact coverage and
limitations.

The bibliography and `verification/imported-sources.json` identify the public
sources used by the manuscript.  The monorepo retains a private literature
audit; the standalone release intentionally omits that internal research
record.
