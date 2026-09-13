"""各層 citation_ids 必須能在 evidence/citations.yaml 對上。"""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CITE_PATH = ROOT / "evidence" / "citations.yaml"
LAYER_FILES = [
    ROOT / "core" / "identities.yaml",
    ROOT / "guardrails" / "principles.yaml",
    ROOT / "config" / "parameters.yaml",
    ROOT / "config" / "assistance.yaml",
    ROOT / "adapters" / "registry.yaml",
    ROOT / "evidence" / "rejected.yaml",
]


def _collect_cite_ids(node, out):
    if isinstance(node, dict):
        if "citation_ids" in node:
            ids = node["citation_ids"]
            if isinstance(ids, str):
                out.append(ids)
            else:
                out.extend(ids)
        for v in node.values():
            _collect_cite_ids(v, out)
    elif isinstance(node, list):
        for item in node:
            _collect_cite_ids(item, out)


def test_every_citation_id_is_registered():
    registered = {c["id"] for c in yaml.safe_load(CITE_PATH.read_text(encoding="utf-8"))["citations"]}
    used = []
    for path in LAYER_FILES:
        _collect_cite_ids(yaml.safe_load(path.read_text(encoding="utf-8")), used)
    unknown = sorted(set(used) - registered)
    assert not unknown, f"未登記的 citation_ids: {unknown}"


def test_literature_frontmatter_citations_are_registered():
    registered = {c["id"] for c in yaml.safe_load(CITE_PATH.read_text(encoding="utf-8"))["citations"]}
    used = []
    for path in (ROOT / "literature").rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        fm = text.split("---", 2)[1]
        _collect_cite_ids(yaml.safe_load(fm) or {}, used)
    unknown = sorted(set(used) - registered)
    assert not unknown, f"文獻未登記的 citation_ids: {unknown}"


def test_acwr_adapter_stays_disabled():
    from adapters._disabled.acwr import DISABLED
    assert DISABLED is True
