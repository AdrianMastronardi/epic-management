#!/usr/bin/env python3
"""Validate an EPIC knowledge bundle against Open Knowledge Format v0.2.

Errors are conformance failures or skill requirements. Warnings are the
tolerances OKF grants consumers, such as broken cross-links; pass --strict to
treat them as failures.

OKF makes log.md optional and this skill relies on git for history instead, so
no log is required. One found in the bundle is still checked against the
structure OKF defines for the reserved filename.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path, PurePosixPath

from okf import (
    DATE_RE,
    LINK_RE,
    OKF_VERSION,
    FrontmatterError,
    as_text,
    check_sources,
    check_stale_after,
    check_trust,
    has_frontmatter,
    iter_concepts,
    read_document,
    STATUS_VALUES,
)


EPIC_DIRECTORY_RE = re.compile(r"^EPIC-\d{3}-[a-z0-9]+(?:-[a-z0-9]+)*$")
LOG_DATE_RE = re.compile(r"^## (\S+)\s*$")


def relative(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def first_path_part(target: str) -> str:
    head = target.split("#", 1)[0]
    return next(
        (part for part in PurePosixPath(head).parts if part not in {".", "/"}),
        "",
    )


def validate_root_index(root: Path, errors: list[str], warnings: list[str]) -> set[str]:
    path = root / "index.md"
    if not path.is_file():
        errors.append(
            "index.md: the bundle root requires an index listing published EPICs"
        )
        return set()
    try:
        document = read_document(path)
    except (FrontmatterError, OSError) as error:
        errors.append(str(error))
        return set()
    if not document.data:
        errors.append("index.md: the bundle root index must declare okf_version")
    else:
        unexpected = sorted(set(document.data) - {"okf_version"})
        if unexpected:
            errors.append(
                f"index.md: okf_version is the only frontmatter key allowed, found {', '.join(unexpected)}"
            )
        declared = as_text(document.get("okf_version"))
        if declared != OKF_VERSION:
            errors.append(
                f"index.md: okf_version must be \"{OKF_VERSION}\", found '{declared}'"
            )
    if not any(line.startswith("# ") for line in document.body):
        errors.append("index.md: an index requires a heading")
    return {
        first_path_part(target)
        for target in LINK_RE.findall(document.body_text)
        if not target.startswith(("http://", "https://", "mailto:", "#"))
        and first_path_part(target)
    }


def validate_log(path: Path, root: Path, errors: list[str]) -> None:
    label = relative(root, path)
    if has_frontmatter(path):
        errors.append(f"{label}: a log file carries no frontmatter")
    lines = path.read_text(encoding="utf-8").splitlines()
    if not any(line.startswith("# ") for line in lines):
        errors.append(f"{label}: a log requires a heading")
    dates: list[str] = []
    for index, line in enumerate(lines, start=1):
        match = LOG_DATE_RE.match(line)
        if not match:
            continue
        if not DATE_RE.match(match.group(1)):
            errors.append(
                f"{label} line {index}: log headings must use ISO 8601 YYYY-MM-DD"
            )
            continue
        dates.append(match.group(1))
    if not dates:
        errors.append(f"{label}: a log requires at least one dated entry group")
    if dates != sorted(dates, reverse=True):
        errors.append(f"{label}: log entry groups must be ordered newest first")


def validate_index(path: Path, root: Path, errors: list[str]) -> None:
    label = relative(root, path)
    if has_frontmatter(path):
        errors.append(f"{label}: only the bundle root index may carry frontmatter")
    if not any(
        line.startswith("# ") for line in path.read_text(encoding="utf-8").splitlines()
    ):
        errors.append(f"{label}: an index requires a heading")


def validate_concept(path: Path, root: Path, errors: list[str]) -> None:
    label = relative(root, path)
    try:
        document = read_document(path)
    except (FrontmatterError, OSError) as error:
        errors.append(str(error))
        return
    if not document.data:
        errors.append(f"{label}: every concept requires a YAML frontmatter block")
        return
    if not as_text(document.get("type")):
        errors.append(f"{label}: every concept requires a non-empty type")
    if document.has("status"):
        status = as_text(document.get("status"))
        if status not in STATUS_VALUES:
            errors.append(f"{label}: status must be one of {', '.join(STATUS_VALUES)}")
    if document.has("generated") or document.has("verified"):
        check_trust(document, label, errors, require_human=False)
    check_stale_after(document, label, errors)
    if document.has("sources"):
        check_sources(document, label, errors, required=False)


def validate_links(path: Path, root: Path, warnings: list[str]) -> None:
    label = relative(root, path)
    text = path.read_text(encoding="utf-8")
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        head = target.split("#", 1)[0]
        if not head:
            continue
        base = root if head.startswith("/") else path.parent
        candidate = (base / head.lstrip("/")).resolve()
        if not candidate.is_relative_to(root.resolve()):
            warnings.append(f"{label}: link target '{target}' escapes the bundle")
            continue
        if not candidate.exists():
            warnings.append(
                f"{label}: link target '{target}' does not resolve inside the bundle"
            )


def validate(root: Path, strict: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not root.is_dir():
        return [f"{root} is not a directory"], []

    linked = validate_root_index(root, errors, warnings)

    for path in sorted(root.rglob("*.md")):
        if path.name == "index.md" and path != root / "index.md":
            validate_index(path, root, errors)
        elif path.name == "log.md":
            validate_log(path, root, errors)
        validate_links(path, root, warnings)

    for path in iter_concepts(root):
        validate_concept(path, root, errors)

    for directory in sorted(root.iterdir()):
        if not directory.is_dir() or not EPIC_DIRECTORY_RE.match(directory.name):
            continue
        if directory.name not in linked:
            errors.append(f"index.md: {directory.name} is published but not listed")
        if not (directory / "epic.md").is_file():
            errors.append(f"{directory.name}: missing epic.md")
        if not (directory / "index.md").is_file():
            errors.append(f"{directory.name}: missing index.md")

    if strict:
        errors.extend(warnings)
        warnings = []
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an OKF EPIC knowledge bundle."
    )
    parser.add_argument(
        "bundle_root", type=Path, help="bundle root, normally docs/epics"
    )
    parser.add_argument(
        "--strict", action="store_true", help="treat warnings as failures"
    )
    args = parser.parse_args()

    errors, warnings = validate(args.bundle_root, args.strict)
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"epic-management: {args.bundle_root} conforms to OKF v{OKF_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
