#!/usr/bin/env python3
"""Record the current statement and terminal digests in the claim map.

The correspondence check pins each claim-map row to the manuscript statement it
describes and to the statements of the terminals it registers, by digest.  When
either changes, the check fails, and the row must be re-examined: does its
recorded objects, hypotheses, conclusion, and limitations still describe what
Lean now proves about what the manuscript now states?

Run this only after that re-examination, and only for rows it applies to:

    python3 lean/verification/refresh_claim_digests.py LABEL [LABEL ...]
    python3 lean/verification/refresh_claim_digests.py --machinery DECLARATION ...
    python3 lean/verification/refresh_claim_digests.py --all

The last form records every current digest at once and is for establishing the
baseline, not for clearing a failure.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "verification" / "check_formal_artifact.py"
CLAIMS = ROOT / "verification" / "claims.json"


def load_checker() -> dict:
    namespace: dict = {"__file__": str(CHECKER), "__name__": "check_formal_artifact"}
    exec(compile(CHECKER.read_text(encoding="utf-8"), str(CHECKER), "exec"), namespace)
    return namespace


def main() -> None:
    arguments = sys.argv[1:]
    if not arguments:
        print(__doc__)
        raise SystemExit(2)
    checker = load_checker()
    manifest = json.loads(CLAIMS.read_text(encoding="utf-8"))
    namespace = manifest["terminal_namespace"]
    environments = checker["manuscript_environments"]()
    interface_sources = checker["reviewer_sources"](manifest)
    signatures = checker["terminal_signatures"](interface_sources)

    everything = arguments == ["--all"]
    machinery_mode = arguments[:1] == ["--machinery"]
    selected = set(arguments[1:] if machinery_mode else arguments)

    for claim in manifest["claims"]:
        label = claim["manuscript_label"]
        if not (everything or (not machinery_mode and label in selected)):
            continue
        claim["statement_digest"] = checker["statement_digest"](environments[label])
        if claim["declarations"]:
            claim["terminal_digest"] = checker["terminal_digest"](
                claim["declarations"], signatures, namespace
            )
        else:
            claim.pop("terminal_digest", None)
        print("recorded", label)

    for entry in manifest["machinery"]:
        declaration = entry["declaration"]
        if not (everything or (machinery_mode and declaration in selected)):
            continue
        entry["terminal_digest"] = checker["terminal_digest"](
            [declaration], signatures, namespace
        )
        print("recorded", declaration)

    CLAIMS.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
