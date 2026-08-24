#!/usr/bin/env python3
"""Emit the annotated dependency graph of the manuscript in Graphviz form.

Nodes are the theorem-like statements of the manuscript, coloured by the
strength at which they are formalized, together with the external results they
import and the computational evidence bundles they rest on.  Edges run from a
dependency to the statement that uses it: dashed for a dependency recorded in a
statement body, which is conceptual, solid for one recorded in a proof, which is
logical, and dotted for an imported source or an evidence bundle.

The emitted file is deterministic: identifiers are sorted, and no timestamp or
path is written.  Regenerate it with

    python3 verification/dependency_graph.py verification/dependency-graph.dot

and check it against the manuscript with

    python3 lean/verification/check_formal_artifact.py --source-only
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION_DIRS = (ROOT / "sections",)
ENVIRONMENTS = ("theorem", "proposition", "lemma", "corollary", "definition")
FILL = {
    "absent": "#ffffff",
    "fragment": "#fde8c8",
    "conditional_deduction": "#d6e8f7",
    "complete": "#cdeccd",
}


def identifiers(body: str, macro: str) -> list[str]:
    found = re.findall(r"\\" + macro + r"\{(.*?)\}", body, re.DOTALL)
    if not found:
        return []
    cleaned = re.sub(r"%.*", "", found[0])
    return [part.strip() for part in cleaned.split(",") if part.strip()]


def collect() -> tuple[dict[str, str], list[tuple[str, str, str]]]:
    coverage: dict[str, str] = {}
    edges: list[tuple[str, str, str]] = []
    environment = re.compile(
        r"\\begin\{(" + "|".join(ENVIRONMENTS) + r")\}(?:\[[^\]]*\])?(.*?)\\end\{\1\}",
        re.DOTALL,
    )
    for section in (
        section
        for directory in SECTION_DIRS
        for section in sorted(directory.glob("*.tex"))
    ):
        text = section.read_text(encoding="utf-8")
        for match in environment.finditer(text):
            body = match.group(2)
            label = re.findall(r"\\label\{((?:thm|prop|lem|cor|def):[^}]+)\}", body)[0]
            coverage[label] = identifiers(body, "coverage")[0]
            for kind, macro in (("conceptual", "uses"), ("import", "imports"),
                                ("import", "evidence")):
                for source in identifiers(body, macro):
                    edges.append((source, label, kind))
        position = 0
        for match in re.finditer(r"\\begin\{proof\}(.*?)\\end\{proof\}", text, re.DOTALL):
            body = match.group(1)
            named = identifiers(body, "proves")
            if named:
                label = named[0]
            else:
                preceding = re.findall(
                    r"\\label\{((?:thm|prop|lem|cor|def):[^}]+)\}", text[position:match.start()]
                )
                if not preceding:
                    continue
                label = preceding[-1]
            position = match.end()
            for kind, macro in (("logical", "uses"), ("import", "imports"),
                                ("import", "evidence")):
                for source in identifiers(body, macro):
                    edges.append((source, label, kind))
    return coverage, edges


def emit(coverage: dict[str, str], edges: list[tuple[str, str, str]]) -> str:
    style = {"conceptual": "dashed", "logical": "solid", "import": "dotted"}
    lines = ["digraph manuscript {", '  rankdir=BT;',
             '  node [shape=box, style=filled, fontname="Helvetica", fontsize=10];',
             '  edge [fontname="Helvetica", fontsize=8];']
    for label in sorted(coverage):
        lines.append(
            '  "%s" [fillcolor="%s", tooltip="%s"];'
            % (label, FILL[coverage[label]], coverage[label])
        )
    external = sorted({source for source, _, kind in edges if kind == "import"})
    for source in external:
        lines.append('  "%s" [shape=note, fillcolor="#eeeeee"];' % source)
    for source, target, kind in sorted(set(edges)):
        lines.append('  "%s" -> "%s" [style=%s];' % (source, target, style[kind]))
    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> None:
    coverage, edges = collect()
    rendered = emit(coverage, edges)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


if __name__ == "__main__":
    main()
