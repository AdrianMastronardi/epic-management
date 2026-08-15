#!/usr/bin/env python3
"""Validate an EPIC document's structure and GitHub distribution map."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


TITLE_RE = re.compile(r"^# EPIC-(\d{3}):\s+\S")
SPEC_RE = re.compile(r"^### (SPEC-(\d{3})-(\d{3})):\s+\S")
STORY_RE = re.compile(r"^### (STORY-(\d{3})-(\d{3})):\s+\S")
TEMP_REF_RE = re.compile(r"(?<![A-Za-z0-9_.-])tmp/")
PLACEHOLDER_RE = re.compile(r"\{\{[^{}]+\}\}")
REQUIRED_H2 = (
    "## Description",
    "## Functional and technical specification",
    "## Affected components",
    "## Dependencies",
    "## Execution order",
    "## Acceptance criteria",
    "## GitHub distribution",
    "## Stories",
)
REQUIRED_STORY_H4 = (
    "#### Description",
    "#### Tasks",
    "#### Acceptance criteria",
    "#### Quality checklist",
)


@dataclass(frozen=True)
class Distribution:
    block_id: str
    block_class: str
    destinations: frozenset[str]
    line: int


def section_bounds(lines: list[str], heading: str) -> tuple[int, int]:
    start = lines.index(heading)
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return start, end


def parse_table(lines: list[str], start: int, end: int, errors: list[str]) -> list[Distribution]:
    rows: list[Distribution] = []
    for index in range(start + 1, end):
        line = lines[index].strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells == ["Block", "Class", "Destination"]:
            continue
        if len(cells) == 3 and all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        if len(cells) != 3:
            errors.append(f"line {index + 1}: distribution row must have three columns")
            continue
        block_id, block_class, destination_text = cells
        destinations = frozenset(
            destination.strip().upper()
            for destination in destination_text.split(",")
            if destination.strip()
        )
        rows.append(Distribution(block_id, block_class.lower(), destinations, index + 1))
    if not rows:
        errors.append("distribution table has no data rows")
    return rows


def parse_id_list(value: str) -> frozenset[str]:
    return frozenset(item.strip() for item in value.split(",") if item.strip())


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        return [f"cannot read {path}: {error}"]

    lines = text.splitlines()
    if not lines:
        return ["document is empty"]

    title_match = TITLE_RE.match(lines[0])
    if not title_match:
        return ["line 1: expected '# EPIC-NNN: name'"]
    epic_number = title_match.group(1)

    if TEMP_REF_RE.search(text):
        errors.append("document contains a forbidden tmp/ reference")
    if PLACEHOLDER_RE.search(text):
        errors.append("document contains unresolved {{PLACEHOLDER}} values")
    if re.search(r"\bdrafts?\b", text, flags=re.IGNORECASE):
        errors.append("versioned EPIC documents must not be labelled as drafts")

    positions: list[int] = []
    for heading in REQUIRED_H2:
        count = lines.count(heading)
        if count != 1:
            errors.append(f"expected exactly one '{heading}', found {count}")
            continue
        positions.append(lines.index(heading))
    if len(positions) == len(REQUIRED_H2) and positions != sorted(positions):
        errors.append("required level-2 sections are out of order")

    if errors and any(heading not in lines for heading in REQUIRED_H2):
        return errors

    spec_start, spec_end = section_bounds(lines, "## Functional and technical specification")
    spec_matches: list[tuple[str, int, int]] = []
    for index in range(spec_start + 1, spec_end):
        if not lines[index].startswith("### "):
            continue
        match = SPEC_RE.match(lines[index])
        if not match:
            errors.append(f"line {index + 1}: specification heading must use SPEC-NNN-SSS")
            continue
        block_id, block_epic, serial = match.groups()
        spec_matches.append((block_id, int(serial), index + 1))
        if block_epic != epic_number:
            errors.append(f"line {index + 1}: {block_id} belongs to another EPIC")

    spec_ids = [block_id for block_id, _, _ in spec_matches]
    spec_serials = [serial for _, serial, _ in spec_matches]
    if not spec_ids:
        errors.append("specification has no SPEC blocks")
    if len(spec_ids) != len(set(spec_ids)):
        errors.append("SPEC block identifiers are duplicated")
    if spec_serials and spec_serials != list(range(1, len(spec_serials) + 1)):
        errors.append("SPEC blocks must be numbered consecutively from 001")

    stories_start, stories_end = section_bounds(lines, "## Stories")
    story_matches: list[tuple[str, int, int]] = []
    for index in range(stories_start + 1, stories_end):
        match = STORY_RE.match(lines[index])
        if not match:
            continue
        story_id, story_epic, serial = match.groups()
        story_matches.append((story_id, int(serial), index))
        if story_epic != epic_number:
            errors.append(f"line {index + 1}: {story_id} belongs to another EPIC")

    story_ids = [story_id for story_id, _, _ in story_matches]
    story_serials = [serial for _, serial, _ in story_matches]
    if not story_ids:
        errors.append("document has no stories")
    if len(story_ids) != len(set(story_ids)):
        errors.append("story identifiers are duplicated")
    if story_serials and story_serials != list(range(1, len(story_serials) + 1)):
        errors.append("stories must be numbered consecutively from 001")

    distribution_start, distribution_end = section_bounds(lines, "## GitHub distribution")
    rows = parse_table(lines, distribution_start, distribution_end, errors)
    rows_by_block: dict[str, Distribution] = {}
    valid_destinations = {"DOCUMENT", "EPIC", *story_ids}
    for row in rows:
        if row.block_id in rows_by_block:
            errors.append(f"line {row.line}: duplicate distribution for {row.block_id}")
        rows_by_block[row.block_id] = row
        if row.block_class not in {"context", "operational"}:
            errors.append(f"line {row.line}: class must be context or operational")
        unknown = row.destinations - valid_destinations
        if unknown:
            errors.append(
                f"line {row.line}: unknown destinations {', '.join(sorted(unknown))}"
            )
        if row.block_class == "operational" and not (
            row.destinations & ({"EPIC"} | set(story_ids))
        ):
            errors.append(
                f"line {row.line}: operational block must reach EPIC or a story"
            )
        if not row.destinations:
            errors.append(f"line {row.line}: destination list is empty")

    missing_rows = set(spec_ids) - set(rows_by_block)
    extra_rows = set(rows_by_block) - set(spec_ids)
    if missing_rows:
        errors.append(f"SPEC blocks missing from distribution: {', '.join(sorted(missing_rows))}")
    if extra_rows:
        errors.append(f"distribution references unknown blocks: {', '.join(sorted(extra_rows))}")

    for story_index, (story_id, _, start) in enumerate(story_matches):
        end = (
            story_matches[story_index + 1][2]
            if story_index + 1 < len(story_matches)
            else stories_end
        )
        story_lines = lines[start:end]
        if not any(line.startswith("**Components**:") for line in story_lines):
            errors.append(f"{story_id}: missing Components line")
        applicable_lines = [
            line for line in story_lines if line.startswith("**Applicable blocks**:")
        ]
        if len(applicable_lines) != 1:
            errors.append(f"{story_id}: expected exactly one Applicable blocks line")
            applicable = frozenset()
        else:
            applicable = parse_id_list(applicable_lines[0].split(":", 1)[1])
        mapped = frozenset(
            row.block_id for row in rows if story_id in row.destinations
        )
        if applicable != mapped:
            errors.append(
                f"{story_id}: applicable blocks differ from distribution "
                f"(line={sorted(applicable)}, table={sorted(mapped)})"
            )
        unknown_applicable = applicable - set(spec_ids)
        if unknown_applicable:
            errors.append(
                f"{story_id}: unknown applicable blocks {', '.join(sorted(unknown_applicable))}"
            )
        for heading in REQUIRED_STORY_H4:
            if story_lines.count(heading) != 1:
                errors.append(f"{story_id}: expected exactly one '{heading}'")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate one self-contained EPIC document."
    )
    parser.add_argument("epic_document", type=Path)
    args = parser.parse_args()

    errors = validate(args.epic_document)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"epic-management: {args.epic_document} is structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
