"""Builds the README's "what is proven" table from test results, so no claim outruns the evidence.

    python3 tools/proof/proof_table.py claims.json
claims.json: [{"claim": "...", "tests": ["test name substring", ...]}]. Test results come from
proof/pytest.xml (pytest --junitxml) and proof/playwright.json (playwright --reporter=json).
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path(os.environ.get("PROOF_DIR", "proof"))


def results() -> dict[str, bool]:
    passed: dict[str, bool] = {}
    if (OUT / "pytest.xml").exists():
        for case in ET.parse(OUT / "pytest.xml").iter("testcase"):
            passed[case.get("name", "")] = not any(child.tag in ("failure", "error", "skipped") for child in case)
    if (OUT / "playwright.json").exists():
        def walk(suite):
            for spec in suite.get("specs", []):
                passed[spec["title"]] = all(t["status"] == "expected" for t in spec.get("tests", []))
            for child in suite.get("suites", []):
                walk(child)
        for suite in json.loads((OUT / "playwright.json").read_text()).get("suites", []):
            walk(suite)
    return passed


def table(claims: list[dict], passed: dict[str, bool]) -> str:
    rows = ["| Claim | Verdict | Evidence |", "| --- | --- | --- |"]
    for c in claims:
        hits = {name: ok for name, ok in passed.items() if any(t in name for t in c["tests"])}
        verdict = "Proven" if hits and all(hits.values()) else ("Failing" if hits else "Not yet tested")
        evidence = ", ".join(f"`{n}`" for n in hits) or "no test"
        rows.append(f"| {c['claim']} | {verdict} | {evidence} |")
    return "\n".join(rows)


if __name__ == "__main__":
    print(table(json.loads(Path(sys.argv[1]).read_text()), results()))
