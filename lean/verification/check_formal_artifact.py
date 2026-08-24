#!/usr/bin/env python3
"""Check the static trust boundary of the paper-bundled Lean companion."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "TavisRuddFiniteGeom"
CLAIMS = ROOT / "verification" / "claims.json"
EXPECTED_AXIOMS = ROOT / "verification" / "expected_axioms.txt"
MANUSCRIPT_ROOT = ROOT.parent
SECTION_DIRS = (MANUSCRIPT_ROOT / "sections",)
AXIOM_AUDIT = (
    SOURCE_ROOT
    / "Papers"
    / "IntegralSecantArcs"
    / "Verification"
    / "AxiomAudit.lean"
)
IMPORTED_SOURCES = ROOT.parent / "verification" / "imported-sources.json"
EVIDENCE = ROOT.parent / "verification" / "evidence.json"
MANUSCRIPTS = (MANUSCRIPT_ROOT / "integral_secant_arcs.tex",)
GRAPH_GENERATOR = ROOT.parent / "verification" / "dependency_graph.py"
GRAPH = ROOT.parent / "verification" / "dependency-graph.dot"
LEAN_README = ROOT / "README.md"
VERIFICATION_README = ROOT.parent / "verification" / "README.md"

FORBIDDEN = {
    "sorry": re.compile(r"\bsorry\b"),
    "admit": re.compile(r"\badmit\b"),
    "project axiom": re.compile(r"(?m)^\s*axiom\s+"),
    "unsafe": re.compile(r"\bunsafe\b"),
    "native_decide": re.compile(r"\bnative_decide\b"),
    "implemented_by": re.compile(r"\bimplemented_by\b"),
    "opaque declaration": re.compile(r"(?m)^\s*opaque\s+"),
    "kernel skipping": re.compile(r"\bdebug\.skipKernelTC\b"),
    "task identifier": re.compile(r"\bC[0-9]{2,}\b"),
}

THEOREM_ENVIRONMENTS = ("theorem", "proposition", "lemma", "corollary", "definition")
ALLOWED_COVERAGE = {"absent", "fragment", "conditional_deduction", "complete"}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def manuscript_sections() -> tuple[Path, ...]:
    """All section sources covered by the repository-wide formal artifact."""
    return tuple(
        section
        for directory in SECTION_DIRS
        for section in sorted(directory.glob("*.tex"))
    )


def manuscript_environments() -> dict[str, str]:
    """Map each theorem-like manuscript environment's semantic label to its body."""
    environments: dict[str, str] = {}
    environment_pattern = re.compile(
        r"\\begin\{(" + "|".join(THEOREM_ENVIRONMENTS) + r")\}"
        r"(?:\[[^\]]*\])?(.*?)\\end\{\1\}",
        re.DOTALL,
    )
    for section in manuscript_sections():
        text = section.read_text(encoding="utf-8")
        for match in environment_pattern.finditer(text):
            found = re.findall(
                r"\\label\{((?:thm|prop|lem|cor|def):[^}]+)\}", match.group(2)
            )
            if len(found) != 1:
                fail(
                    f"{section.relative_to(ROOT.parent)} has a {match.group(1)} "
                    f"environment with {len(found)} semantic labels"
                )
            label = found[0]
            if label in environments:
                fail(f"duplicate manuscript label {label}")
            environments[label] = match.group(2)
    return environments


def manuscript_proofs(labels: set[str]) -> dict[str, str]:
    """Map each proof block to the statement it establishes.

    A proof is paired with the statement it follows, unless it carries a
    \\proves annotation naming the statement it establishes, which is how a proof
    separated from its statement is paired with it.
    """
    proofs: dict[str, str] = {}
    for section in manuscript_sections():
        text = section.read_text(encoding="utf-8")
        position = 0
        for match in re.finditer(r"\\begin\{proof\}(.*?)\\end\{proof\}", text, re.DOTALL):
            body = match.group(1)
            named = re.findall(r"\\proves\{([^}]*)\}", body)
            if len(named) > 1:
                fail(f"{section.name} has a proof with {len(named)} \\proves annotations")
            if named:
                owner = named[0].strip()
                if owner not in labels:
                    fail(f"{section.name} has a proof of unknown statement {owner!r}")
            else:
                preceding = re.findall(
                    r"\\label\{((?:thm|prop|lem|cor|def):[^}]+)\}", text[position:match.start()]
                )
                if not preceding:
                    continue
                owner = preceding[-1]
            if owner in proofs:
                fail(f"statement {owner} has more than one proof")
            proofs[owner] = body
            position = match.end()
    return proofs


ANNOTATIONS = ("coverage", "lean", "uses", "imports", "evidence", "proves")


def statement_digest(body: str) -> str:
    """Digest of a manuscript statement, ignoring its annotations and layout.

    The annotations are removed before hashing, because the annotation gate
    already compares them with the claim map; what this digest fixes is the
    mathematical text of the statement, so that rewriting it forces the row
    describing its formal coverage to be re-examined.
    """
    stripped = body
    for macro in ANNOTATIONS:
        stripped = re.sub(r"\\" + macro + r"\{.*?\}", "", stripped, flags=re.DOTALL)
    stripped = re.sub(r"(?m)%.*$", "", stripped)
    return hashlib.sha256(" ".join(stripped.split()).encode("utf-8")).hexdigest()


def terminal_signatures(interface_sources: tuple[Path, ...]) -> dict[str, str]:
    """The elaborated statement text of each reviewer terminal, by name.

    A terminal's signature runs from its declaration keyword to the assignment
    that opens its proof; the docstring above it is deliberately excluded, so a
    prose improvement does not read as a change of statement.
    """
    signatures: dict[str, str] = {}
    for source in interface_sources:
        current: str | None = None
        collected: list[str] = []
        for line in source.read_text(encoding="utf-8").splitlines():
            opening = re.match(
                r"^(?:noncomputable\s+)?(?:theorem|def)\s+([A-Za-z0-9_']+)", line
            )
            if opening:
                current = opening.group(1)
                collected = [line]
                if ":=" in line:
                    signatures[current] = " ".join(" ".join(collected).split())
                    current = None
                continue
            if current is not None:
                collected.append(line)
                if ":=" in line:
                    signatures[current] = " ".join(" ".join(collected).split())
                    current = None
    return signatures


def reviewer_sources(manifest: dict[str, object]) -> tuple[Path, ...]:
    """Resolve the declared section-level reviewer modules inside this package."""
    modules = manifest.get("reviewer_modules")
    if not isinstance(modules, list) or not modules or not all(isinstance(x, str) for x in modules):
        fail("claim map declares no reviewer module list")
    if len(modules) != len(set(modules)):
        fail("claim map repeats a reviewer module")
    result = tuple(ROOT / (module.replace(".", "/") + ".lean") for module in modules)
    for source in result:
        if not source.is_relative_to(SOURCE_ROOT) or not source.is_file():
            fail(f"reviewer module does not resolve inside the package: {source}")
    aggregator = manifest.get("reviewer_module")
    if not isinstance(aggregator, str) or not aggregator:
        fail("claim map declares no reviewer aggregator")
    aggregator_source = ROOT / (aggregator.replace(".", "/") + ".lean")
    if not aggregator_source.is_file():
        fail("reviewer aggregator does not resolve inside the package")
    aggregator_text = aggregator_source.read_text(encoding="utf-8")
    for module in modules:
        if f"import {module}" not in aggregator_text:
            fail(f"reviewer aggregator does not import {module}")
    return result


def terminal_digest(declarations: list[str], signatures: dict[str, str], namespace: str) -> str:
    """Digest of the statements of one row's terminals, in the recorded order."""
    payload = []
    for declaration in declarations:
        name = declaration[len(namespace) + 1:]
        if name not in signatures:
            fail(f"no signature found for terminal {declaration}")
        payload.append(signatures[name])
    return hashlib.sha256("\n".join(payload).encode("utf-8")).hexdigest()


def annotation(label: str, body: str, macro: str, arity_optional: bool = False) -> str | None:
    """Read the single argument of one formal-annotation macro from an environment."""
    matches = re.findall(r"\\" + macro + r"\{(.*?)\}", body, re.DOTALL)
    if not matches:
        if arity_optional:
            return None
        fail(f"{label} carries no \\{macro} annotation")
    if len(matches) > 1:
        fail(f"{label} carries {len(matches)} \\{macro} annotations")
    return matches[0]


def registry(path: Path, key: str, schema: str) -> dict[str, dict]:
    """Read one identifier-keyed provenance registry."""
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema") != schema:
        fail(f"{path.name} has an unexpected schema")
    entries = manifest.get(key)
    if not isinstance(entries, dict):
        fail(f"{path.name} has no {key} map")
    return entries


def check_imported_sources(entries: dict[str, dict]) -> None:
    """Every imported source names a bibliography key, a pinpoint, and its conventions."""
    bibliography = {
        key
        for manuscript in MANUSCRIPTS
        for key in re.findall(
            r"\\bibitem\{([^}]+)\}", manuscript.read_text(encoding="utf-8")
        )
    }
    for identifier, entry in entries.items():
        for field in ("citation", "pinpoint", "used"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                fail(f"imported source {identifier} has no nonempty {field}")
        if entry["citation"] not in bibliography:
            fail(f"imported source {identifier} cites unknown bibliography key {entry['citation']}")
        conventions = entry.get("conventions")
        if not isinstance(conventions, list) or not conventions:
            fail(f"imported source {identifier} records no conventions")
        for convention in conventions:
            for field in ("aspect", "requirement", "matched"):
                if not isinstance(convention.get(field), str) or not convention[field].strip():
                    fail(f"imported source {identifier} has a convention with no {field}")


def check_evidence(entries: dict[str, dict]) -> None:
    """Every evidence bundle names its role, its checksum manifest, and its replay commands."""
    for identifier, entry in entries.items():
        for field in ("role", "checksum_manifest"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                fail(f"evidence bundle {identifier} has no nonempty {field}")
        manifest_path = ROOT.parent / entry["checksum_manifest"]
        if not manifest_path.is_file():
            fail(f"evidence bundle {identifier} names a missing checksum manifest")
        commands = entry.get("commands")
        if not isinstance(commands, list) or not commands:
            fail(f"evidence bundle {identifier} records no replay command")


def annotated_identifiers(body: str, macro: str) -> list[str]:
    """The identifiers listed by one annotation macro, in source order."""
    payload = re.findall(r"\\" + macro + r"\{(.*?)\}", body, re.DOTALL)
    if not payload:
        return []
    cleaned = re.sub(r"%.*", "", payload[0])
    return [part.strip() for part in cleaned.split(",") if part.strip()]


def annotated_references(label: str, body: str, macro: str, known: set[str], kind: str) -> None:
    """Every identifier annotated by one macro resolves in its registry."""
    payload = annotation(label, body, macro, arity_optional=True)
    if payload is None:
        return
    cleaned = re.sub(r"%.*", "", payload)
    identifiers = [part.strip() for part in cleaned.split(",") if part.strip()]
    if not identifiers:
        fail(f"{label} annotates an empty {kind} list")
    for identifier in identifiers:
        if identifier not in known:
            fail(f"{label} annotates unknown {kind} {identifier!r}")
    if len(set(identifiers)) != len(identifiers):
        fail(f"{label} annotates a repeated {kind}")


def annotated_claim(label: str, body: str, namespace: str) -> tuple[str, list[str]]:
    """Read the coverage and terminal annotations of one manuscript environment."""
    coverage = annotation(label, body, "coverage")
    if coverage not in ALLOWED_COVERAGE:
        fail(f"{label} annotates invalid coverage {coverage!r}")
    payload = annotation(label, body, "lean", arity_optional=True)
    if payload is None:
        declarations: list[str] = []
    else:
        cleaned = re.sub(r"%.*", "", payload)
        names = [part.strip() for part in cleaned.split(",") if part.strip()]
        if not names:
            fail(f"{label} annotates an empty terminal list")
        for name in names:
            if not re.fullmatch(r"[A-Za-z0-9_'.]+", name):
                fail(f"{label} annotates malformed terminal name {name!r}")
        declarations = [f"{namespace}.{name}" for name in names]
        if len(set(declarations)) != len(declarations):
            fail(f"{label} annotates a repeated terminal")
    if coverage == "absent" and declarations:
        fail(f"absent claim {label} annotates terminals")
    if coverage != "absent" and not declarations:
        fail(f"covered claim {label} annotates no terminals")
    return coverage, declarations


def check_public_docstrings(source: Path, text: str) -> None:
    lines = text.splitlines()
    declaration = re.compile(
        r"^(?:noncomputable\s+)?(?:theorem|lemma|def|structure|inductive|class)\s+"
        r"([A-Za-z0-9_'.]+)"
    )
    comment_depth = 0
    for index, line in enumerate(lines):
        if comment_depth:
            comment_depth += line.count("/-") - line.count("-/")
            continue
        if line.lstrip().startswith("--"):
            continue
        opening_comments = line.count("/-")
        closing_comments = line.count("-/")
        if opening_comments > closing_comments:
            comment_depth += opening_comments - closing_comments
            continue
        match = declaration.match(line)
        if match is None:
            continue
        previous = index - 1
        while previous >= 0 and (
            not lines[previous].strip()
            or lines[previous].lstrip().startswith("@[")
        ):
            previous -= 1
        if previous < 0 or not lines[previous].rstrip().endswith("-/"):
            fail(
                f"{source.relative_to(ROOT)}:{index + 1} public declaration "
                f"{match.group(1)} has no immediately preceding docstring"
            )
        opening = previous
        while opening >= 0 and "/--" not in lines[opening]:
            opening -= 1
        if opening < 0:
            fail(
                f"{source.relative_to(ROOT)}:{index + 1} public declaration "
                f"{match.group(1)} has a non-doc comment"
            )


def expected_axioms() -> dict[str, tuple[str, ...]]:
    result: dict[str, tuple[str, ...]] = {}
    for line_number, raw in enumerate(EXPECTED_AXIOMS.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            fail(f"expected_axioms.txt:{line_number} has no colon")
        declaration, payload = (part.strip() for part in line.split(":", 1))
        if declaration in result:
            fail(f"duplicate expected-axiom row for {declaration}")
        result[declaration] = () if payload == "none" else tuple(
            part.strip() for part in payload.split(",") if part.strip()
        )
    return result


def observed_axioms(path: Path) -> dict[str, tuple[str, ...]]:
    text = path.read_text(encoding="utf-8")
    result: dict[str, tuple[str, ...]] = {}
    pattern = re.compile(
        r"'([^']+)' (does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])",
        re.DOTALL,
    )
    for match in pattern.finditer(text):
        declaration = match.group(1)
        payload = match.group(3)
        axioms = () if payload is None else tuple(
            part.strip() for part in payload.replace("\n", " ").split(",") if part.strip()
        )
        if declaration in result:
            fail(f"axiom log repeats {declaration}")
        result[declaration] = axioms
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--source-only", action="store_true")
    mode.add_argument("--axiom-log", type=Path)
    args = parser.parse_args()

    manifest = json.loads(CLAIMS.read_text(encoding="utf-8"))
    if manifest.get("schema") != "integral-secant-arcs-lean-claims-v1":
        fail("unexpected claims schema")
    interface_sources = reviewer_sources(manifest)

    sources = sorted(SOURCE_ROOT.rglob("*.lean"))
    if not sources:
        fail("no Lean sources found")
    namespace = "TavisRuddFiniteGeom.Papers.IntegralSecantArcs"
    for source in sources:
        text = source.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN.items():
            if pattern.search(text):
                fail(f"{source.relative_to(ROOT)} contains forbidden {label}")
        check_public_docstrings(source, text)

    interface_text = "\n".join(
        source.read_text(encoding="utf-8") for source in interface_sources
    )
    terminals = {
        f"{namespace}.{match.group(1)}"
        for match in re.finditer(
            r"(?m)^(?:noncomputable\s+)?(?:theorem|def)\s+([A-Za-z0-9_']+)",
            interface_text,
        )
    }
    audited = set(
        re.findall(r"(?m)^#print axioms\s+(\S+)\s*$", AXIOM_AUDIT.read_text(encoding="utf-8"))
    )
    if audited != terminals:
        fail(
            "axiom audit terminal mismatch: "
            f"missing={sorted(terminals - audited)} extra={sorted(audited - terminals)}"
        )

    terminal_namespace = manifest.get("terminal_namespace")
    if not isinstance(terminal_namespace, str) or not terminal_namespace:
        fail("claim map declares no terminal namespace")
    claims = manifest.get("claims", [])
    labels = [claim.get("manuscript_label") for claim in claims]
    if len(labels) != len(set(labels)):
        fail("duplicate manuscript labels in claim map")
    environments = manuscript_environments()
    expected_labels = set(environments)
    if set(labels) != expected_labels:
        fail(
            "manuscript claim-map mismatch: "
            f"missing={sorted(expected_labels - set(labels))} "
            f"extra={sorted(set(labels) - expected_labels)}"
        )
    imported_sources = registry(
        IMPORTED_SOURCES, "sources", "integral-secant-arcs-imported-sources-v1"
    )
    check_imported_sources(imported_sources)
    evidence_bundles = registry(
        EVIDENCE, "evidence", "integral-secant-arcs-evidence-v1"
    )
    check_evidence(evidence_bundles)
    generator: dict[str, object] = {"__file__": str(GRAPH_GENERATOR), "__name__": "dependency_graph"}
    exec(compile(GRAPH_GENERATOR.read_text(encoding="utf-8"), str(GRAPH_GENERATOR), "exec"),
         generator)
    regenerated = generator["emit"](*generator["collect"]())
    if regenerated != GRAPH.read_text(encoding="utf-8"):
        fail(
            "verification/dependency-graph.dot does not match the manuscript annotations; "
            "regenerate it with verification/dependency_graph.py"
        )

    proofs = manuscript_proofs(expected_labels)
    for label, body in environments.items():
        annotated_references(label, body, "imports", set(imported_sources), "imported source")
        annotated_references(label, body, "evidence", set(evidence_bundles), "evidence bundle")
        annotated_references(label, body, "uses", expected_labels, "manuscript label")
    for label, body in proofs.items():
        annotated_references(label, body, "imports", set(imported_sources), "imported source")
        annotated_references(label, body, "evidence", set(evidence_bundles), "evidence bundle")
        annotated_references(label, body, "uses", expected_labels, "manuscript label")
        if label in annotated_identifiers(body, "uses"):
            fail(f"the proof of {label} lists {label} among its dependencies")

    registered: set[str] = set()
    for claim in claims:
        label = claim.get("manuscript_label")
        coverage = claim.get("coverage")
        annotated_coverage, annotated_declarations = annotated_claim(
            label, environments[label], terminal_namespace
        )
        if annotated_coverage != coverage:
            fail(
                f"{label} annotates coverage {annotated_coverage} but the claim map "
                f"records {coverage}"
            )
        recorded_statement = claim.get("statement_digest")
        current_statement = statement_digest(environments[label])
        if recorded_statement != current_statement:
            fail(
                f"the statement of {label} has changed since its claim-map row was "
                f"reviewed: recorded {recorded_statement}, current {current_statement}"
            )
        if annotated_declarations != claim.get("declarations"):
            fail(
                f"{label} annotates a terminal list differing from the claim map: "
                f"annotated={annotated_declarations} recorded={claim.get('declarations')}"
            )
        if coverage not in ALLOWED_COVERAGE:
            fail(f"invalid coverage for {label}")
        for field in ("objects", "hypotheses", "conclusion", "cautions"):
            if not isinstance(claim.get(field), str) or not claim[field].strip():
                fail(f"{label} has no nonempty {field}")
        declarations = claim.get("declarations")
        if not isinstance(declarations, list):
            fail(f"{label} has no declaration list")
        if coverage == "absent" and declarations:
            fail(f"absent claim {label} registers declarations")
        if coverage != "absent" and not declarations:
            fail(f"covered claim {label} registers no declarations")
        for declaration in declarations:
            if declaration not in terminals:
                fail(f"unresolved declaration {declaration}")
            if declaration in registered:
                fail(f"terminal registered more than once: {declaration}")
            registered.add(declaration)
    signatures = terminal_signatures(interface_sources)
    for claim in claims:
        if not claim["declarations"]:
            if claim.get("terminal_digest") is not None:
                fail(f"absent claim {claim['manuscript_label']} records a terminal digest")
            continue
        recorded = claim.get("terminal_digest")
        current = terminal_digest(claim["declarations"], signatures, terminal_namespace)
        if recorded != current:
            fail(
                f"the terminals of {claim['manuscript_label']} have changed since its "
                f"claim-map row was reviewed: recorded {recorded}, current {current}"
            )

    machinery = manifest.get("machinery")
    if not isinstance(machinery, list):
        fail("claim map has no machinery list")
    for entry in machinery:
        declaration = entry.get("declaration")
        if declaration not in terminals:
            fail(f"unresolved machinery declaration {declaration}")
        if declaration in registered:
            fail(f"terminal registered more than once: {declaration}")
        if not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
            fail(f"machinery declaration {declaration} has no nonempty reason")
        recorded = entry.get("terminal_digest")
        current = terminal_digest([declaration], signatures, terminal_namespace)
        if recorded != current:
            fail(
                f"the statement of machinery terminal {declaration} has changed since its "
                f"row was reviewed: recorded {recorded}, current {current}"
            )
        registered.add(declaration)
    if registered != terminals:
        fail(
            "claim-map terminal mismatch: "
            f"missing={sorted(terminals - registered)} extra={sorted(registered - terminals)}"
        )
    expected = expected_axioms()
    if set(expected) != terminals:
        fail(
            "expected-axiom terminal mismatch: "
            f"missing={sorted(terminals - set(expected))} extra={sorted(set(expected) - terminals)}"
        )
    if args.axiom_log is not None:
        observed = observed_axioms(args.axiom_log)
        if observed != expected:
            fail(
                "axiom output mismatch: "
                f"expected={expected} observed={observed}"
            )
    mode_name = "axiom-log" if args.axiom_log is not None else "source-only"
    coverage_counts = {
        coverage: sum(claim["coverage"] == coverage for claim in claims)
        for coverage in sorted(ALLOWED_COVERAGE)
    }
    coverage_snapshot = (
        f"Checked coverage snapshot: {len(claims)} claims; "
        f"{coverage_counts['absent']} absent; "
        f"{coverage_counts['fragment']} fragmentary; "
        f"{coverage_counts['conditional_deduction']} conditional; "
        f"{coverage_counts['complete']} complete; {len(terminals)} reviewer terminals, "
        f"of which {len(machinery)} are machinery serving no current manuscript claim."
    )
    for readme in (LEAN_README, VERIFICATION_README):
        normalized = " ".join(readme.read_text(encoding="utf-8").split())
        if coverage_snapshot not in normalized:
            fail(
                f"{readme.relative_to(ROOT.parent)} has a stale or missing "
                "checked coverage snapshot"
            )
    print(
        f"PASS mode={mode_name} sources={len(sources)} terminals={len(terminals)} "
        f"manuscript_claims={len(claims)} machinery={len(machinery)} "
        f"imported_sources={len(imported_sources)} evidence={len(evidence_bundles)} "
        f"coverage={coverage_counts}"
    )


if __name__ == "__main__":
    main()
