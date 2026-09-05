#!/usr/bin/env python3
"""Validate one EPIC as an OKF concept directory.

Accepts the EPIC directory, or the epic.md inside it, in either its working
location under tmp/ or its published location inside the docs/epics/ bundle.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from okf import (
    Document,
    EPIC_STATUS_VALUES,
    FrontmatterError,
    LINK_RE,
    as_list,
    as_text,
    body_links,
    check_date,
    check_footnotes,
    check_hygiene,
    check_sources,
    check_stale_after,
    check_status,
    check_trust,
    has_frontmatter,
    infer_stage,
    read_document,
    section_bounds,
)


DIRECTORY_RE = re.compile(r"^EPIC-(\d{3})-[a-z0-9]+(?:-[a-z0-9]+)*$")
TITLE_RE = re.compile(r"^EPIC-(\d{3}) — \S")
STORY_TITLE_RE = re.compile(r"^STORY-(\d{3})-(\d{3}) — \S")
STORY_FILE_RE = re.compile(r"^(STORY-(\d{3})-(\d{3}))-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
SPEC_RE = re.compile(r"^### (SPEC-(\d{3})-(\d{3})):\s+\S")
STORY_ID_RE = re.compile(r"^STORY-(\d{3})-(\d{3})$")
SPEC_FRAGMENT_RE = re.compile(r"^(spec-\d{3}-\d{3})(?:-|$)", re.IGNORECASE)

REQUIRED_EPIC_SECTIONS = (
    "## Description",
    "## Functional and technical specification",
    "## Affected components",
    "## Dependencies",
    "## Execution order",
    "## Acceptance criteria",
    "## GitHub distribution",
)
COMPLETION_SECTIONS = ("## Final verification", "## Findings", "## Exit state")
REQUIRED_STORY_SECTIONS = (
    "## Description",
    "## Applicable specification",
    "## Tasks",
    "## Acceptance criteria",
    "## Quality checklist",
)


class Distribution:
    __slots__ = ("block_id", "block_class", "destinations", "line")

    def __init__(
        self, block_id: str, block_class: str, destinations: frozenset[str], line: int
    ):
        self.block_id = block_id
        self.block_class = block_class
        self.destinations = destinations
        self.line = line


def parse_distribution(document: Document, errors: list[str]) -> list[Distribution]:
    start, end = section_bounds(document.body, "## GitHub distribution")
    rows: list[Distribution] = []
    for index in range(start + 1, end):
        line = document.body[index].strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells == ["Block", "Class", "Destination"]:
            continue
        if len(cells) == 3 and all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        if len(cells) != 3:
            errors.append(
                f"epic.md line {document.body_offset + index}: distribution row must have three columns"
            )
            continue
        block_id, block_class, destination_text = cells
        destinations = frozenset(
            destination.strip().upper()
            for destination in destination_text.split(",")
            if destination.strip()
        )
        rows.append(
            Distribution(
                block_id,
                block_class.lower(),
                destinations,
                document.body_offset + index,
            )
        )
    if not rows:
        errors.append("epic.md: distribution table has no data rows")
    return rows


def check_sections(
    document: Document, label: str, required: tuple[str, ...], errors: list[str]
) -> bool:
    positions: list[int] = []
    complete = True
    for heading in required:
        count = document.body.count(heading)
        if count != 1:
            errors.append(f"{label}: expected exactly one '{heading}', found {count}")
            complete = False
            continue
        positions.append(document.body.index(heading))
    if complete and positions != sorted(positions):
        errors.append(f"{label}: required sections are out of order")
    return complete


def validate_local_links(document: Document, label: str, errors: list[str]) -> None:
    for target in body_links(document):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        head = target.split("#", 1)[0]
        if not head:
            continue
        candidate = (document.path.parent / head).resolve()
        if not candidate.exists():
            errors.append(f"{label}: link target '{target}' does not exist")


def validate_epic_concept(
    document: Document, number: str, stage: str, errors: list[str]
) -> tuple[list[str], list[Distribution]]:
    label = "epic.md"
    if as_text(document.get("type")) != "EPIC":
        errors.append(f"{label}: type must be EPIC")
    title = as_text(document.get("title"))
    title_match = TITLE_RE.match(title)
    if not title_match:
        errors.append(f"{label}: title must read 'EPIC-NNN — name'")
    elif title_match.group(1) != number:
        errors.append(
            f"{label}: title number does not match the directory number {number}"
        )
    if not as_text(document.get("description")):
        errors.append(f"{label}: description is required")
    if as_text(document.get("epic_number")) != number:
        errors.append(f'{label}: epic_number must be the quoted string "{number}"')
    epic_status = as_text(document.get("epic_status"))
    if epic_status not in EPIC_STATUS_VALUES:
        errors.append(
            f"{label}: epic_status must be one of {', '.join(EPIC_STATUS_VALUES)}"
        )
    check_status(document, label, errors, stage)
    check_trust(document, label, errors, require_human=stage == "published")
    check_stale_after(document, label, errors)
    identifiers = check_sources(document, label, errors, required=True)
    check_footnotes(document, label, errors, identifiers)
    check_hygiene(document, label, errors)
    check_date(document.get("started_on"), f"{label}: started_on", errors)
    if epic_status == "Completed":
        check_date(document.get("completed_on"), f"{label}: completed_on", errors)
        for heading in COMPLETION_SECTIONS:
            if document.body.count(heading) != 1:
                errors.append(
                    f"{label}: a completed EPIC requires exactly one '{heading}'"
                )
    elif as_text(document.get("completed_on")):
        errors.append(
            f"{label}: completed_on is set while epic_status is {epic_status}"
        )
    resource = as_text(document.get("resource"))
    if stage == "published" and not resource:
        errors.append(
            f"{label}: a published EPIC requires resource with its GitHub issue URL"
        )
    if stage == "working" and resource:
        errors.append(f"{label}: a working EPIC must omit resource until publication")

    if not check_sections(document, label, REQUIRED_EPIC_SECTIONS, errors):
        return [], []

    spec_start, spec_end = section_bounds(
        document.body, "## Functional and technical specification"
    )
    spec_ids: list[str] = []
    serials: list[int] = []
    for index in range(spec_start + 1, spec_end):
        if not document.body[index].startswith("### "):
            continue
        match = SPEC_RE.match(document.body[index])
        if not match:
            errors.append(
                f"{label} line {document.body_offset + index}: specification heading must use SPEC-NNN-SSS"
            )
            continue
        block_id, block_number, serial = match.groups()
        spec_ids.append(block_id)
        serials.append(int(serial))
        if block_number != number:
            errors.append(f"{label}: {block_id} belongs to another EPIC")
    if not spec_ids:
        errors.append(f"{label}: specification has no SPEC blocks")
    if len(spec_ids) != len(set(spec_ids)):
        errors.append(f"{label}: SPEC block identifiers are duplicated")
    if serials and serials != list(range(1, len(serials) + 1)):
        errors.append(f"{label}: SPEC blocks must be numbered consecutively from 001")
    return spec_ids, parse_distribution(document, errors)


def validate_story_index(
    document: Document, number: str, errors: list[str]
) -> list[dict]:
    entries = as_list(document.get("stories"))
    if not entries:
        errors.append("epic.md: stories must list at least one story")
        return []
    seen: set[str] = set()
    serials: list[int] = []
    for position, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append(f"epic.md: stories[{position}] must be a mapping")
            continue
        identifier = as_text(entry.get("id"))
        match = STORY_ID_RE.match(identifier)
        if not match:
            errors.append(
                f"epic.md: stories[{position}] id '{identifier}' must read STORY-NNN-SSS"
            )
            continue
        if match.group(1) != number:
            errors.append(f"epic.md: {identifier} belongs to another EPIC")
        if identifier in seen:
            errors.append(f"epic.md: duplicate story id {identifier}")
        seen.add(identifier)
        serials.append(int(match.group(2)))
        if not as_text(entry.get("title")):
            errors.append(f"epic.md: {identifier} requires a title")
        if not as_text(entry.get("concept")):
            errors.append(f"epic.md: {identifier} requires a concept path")
    if serials and serials != list(range(1, len(serials) + 1)):
        errors.append("epic.md: stories must be numbered consecutively from 001")
    return [entry for entry in entries if isinstance(entry, dict)]


def validate_story_concept(
    document: Document,
    entry: dict,
    number: str,
    spec_ids: list[str],
    mapped_blocks: frozenset[str],
    stage: str,
    errors: list[str],
) -> None:
    label = document.path.name
    identifier = as_text(entry.get("id"))
    if as_text(document.get("type")) != "Story":
        errors.append(f"{label}: type must be Story")
    title = as_text(document.get("title"))
    title_match = STORY_TITLE_RE.match(title)
    if not title_match:
        errors.append(f"{label}: title must read 'STORY-NNN-SSS — name'")
    elif f"STORY-{title_match.group(1)}-{title_match.group(2)}" != identifier:
        errors.append(f"{label}: title identifier does not match {identifier}")
    elif title.split(" — ", 1)[1] != as_text(entry.get("title")):
        errors.append(f"{label}: title text does not match epic.md stories entry")
    if not as_text(document.get("description")):
        errors.append(f"{label}: description is required")
    if as_text(document.get("epic")) != f"EPIC-{number}":
        errors.append(f"{label}: epic must be EPIC-{number}")
    epic_concept = as_text(document.get("epic_concept"))
    if not epic_concept:
        errors.append(f"{label}: epic_concept must point at the EPIC concept")
    elif (
        Path(epic_concept).is_absolute()
        or (document.path.parent / epic_concept).resolve()
        != (document.path.parent / "epic.md").resolve()
    ):
        errors.append(f"{label}: epic_concept must resolve to the sibling epic.md")
    if not as_list(document.get("components")):
        errors.append(f"{label}: components must name at least one component")
    check_status(document, label, errors, stage)
    check_trust(document, label, errors, require_human=stage == "published")
    check_stale_after(document, label, errors)
    identifiers = check_sources(document, label, errors, required=False)
    check_footnotes(document, label, errors, identifiers)
    check_hygiene(document, label, errors)
    resource = as_text(document.get("resource"))
    entry_resource = as_text(entry.get("resource"))
    if stage == "published" and not resource:
        errors.append(
            f"{label}: a published story requires resource with its GitHub issue URL"
        )
    if stage == "published" and not entry_resource:
        errors.append(
            f"epic.md: {identifier} requires resource with its GitHub issue URL"
        )
    if (
        stage == "published"
        and resource
        and entry_resource
        and resource != entry_resource
    ):
        errors.append(
            f"{label}: resource must match epic.md stories entry for {identifier}"
        )
    if stage == "working" and (resource or entry_resource):
        errors.append(
            f"{label}: working story resources must be omitted until publication"
        )

    applicable = frozenset(
        as_text(block) for block in as_list(document.get("applicable_blocks"))
    )
    if applicable != mapped_blocks:
        errors.append(
            f"{label}: applicable_blocks differ from the distribution table "
            f"(frontmatter={sorted(applicable)}, table={sorted(mapped_blocks)})"
        )
    unknown = applicable - set(spec_ids)
    if unknown:
        errors.append(
            f"{label}: unknown applicable blocks {', '.join(sorted(unknown))}"
        )
    sections_valid = check_sections(document, label, REQUIRED_STORY_SECTIONS, errors)
    if sections_valid:
        start, end = section_bounds(document.body, "## Applicable specification")
        linked_blocks: set[str] = set()
        epic_path = (document.path.parent / "epic.md").resolve()
        for target in LINK_RE.findall("\n".join(document.body[start + 1 : end])):
            head, separator, fragment = target.partition("#")
            if not separator or not head:
                continue
            if (document.path.parent / head).resolve() != epic_path:
                continue
            match = SPEC_FRAGMENT_RE.match(fragment)
            if match:
                linked_blocks.add(match.group(1).upper())
        if linked_blocks != applicable:
            errors.append(
                f"{label}: Applicable specification links differ from applicable_blocks "
                f"(links={sorted(linked_blocks)}, frontmatter={sorted(applicable)})"
            )
    validate_local_links(document, label, errors)


def validate_index(path: Path, story_files: list[Path], errors: list[str]) -> None:
    label = "index.md"
    if not path.exists():
        errors.append(
            f"{label}: the EPIC directory requires an index.md listing its concepts"
        )
        return
    if has_frontmatter(path):
        errors.append(f"{label}: an EPIC index carries no frontmatter")
    text = path.read_text(encoding="utf-8")
    directory = path.parent.resolve()
    targets: set[str] = set()
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        head = target.split("#", 1)[0]
        if not head:
            continue
        candidate = (path.parent / head).resolve()
        if not candidate.is_file():
            errors.append(f"{label}: link target '{target}' does not exist")
            continue
        if candidate.parent == directory:
            targets.add(candidate.name)
        elif candidate.name == "epic.md" or STORY_FILE_RE.match(candidate.name):
            errors.append(
                f"{label}: concept link '{target}' must stay inside the EPIC directory"
            )
    if "epic.md" not in targets:
        errors.append(f"{label}: must link epic.md")
    for story in story_files:
        if story.name not in targets:
            errors.append(f"{label}: must link {story.name}")


def validate(target: Path, stage: str | None) -> list[str]:
    errors: list[str] = []
    directory = target.parent if target.is_file() else target
    if not directory.is_dir():
        return [f"{directory} is not a directory"]
    match = DIRECTORY_RE.match(directory.name)
    if not match:
        return [f"{directory.name}: EPIC directory must be named EPIC-NNN-slug"]
    number = match.group(1)
    resolved_stage = stage or infer_stage(directory)

    epic_path = directory / "epic.md"
    if not epic_path.is_file():
        return [f"{directory.name}: missing epic.md"]
    try:
        epic = read_document(epic_path)
    except (FrontmatterError, OSError) as error:
        return [str(error)]
    if not epic.data:
        return ["epic.md: missing YAML frontmatter"]

    spec_ids, rows = validate_epic_concept(epic, number, resolved_stage, errors)
    entries = validate_story_index(epic, number, errors)
    declared = [as_text(entry.get("id")) for entry in entries]

    story_files = sorted(
        path for path in directory.glob("STORY-*.md") if STORY_FILE_RE.match(path.name)
    )
    for path in sorted(directory.glob("*.md")):
        if path.name in {"epic.md", "index.md", "log.md"} or path in story_files:
            continue
        errors.append(f"{path.name}: unexpected concept in an EPIC directory")

    rows_by_block: dict[str, Distribution] = {}
    valid_destinations = {"DOCUMENT", "EPIC", *declared}
    for row in rows:
        if row.block_id in rows_by_block:
            errors.append(
                f"epic.md line {row.line}: duplicate distribution for {row.block_id}"
            )
        rows_by_block[row.block_id] = row
        if row.block_class not in {"context", "operational"}:
            errors.append(
                f"epic.md line {row.line}: class must be context or operational"
            )
        if not row.destinations:
            errors.append(f"epic.md line {row.line}: destination list is empty")
        unknown = row.destinations - valid_destinations
        if unknown:
            errors.append(
                f"epic.md line {row.line}: unknown destinations {', '.join(sorted(unknown))}"
            )
        if row.block_class == "operational" and not (
            row.destinations & ({"EPIC"} | set(declared))
        ):
            errors.append(
                f"epic.md line {row.line}: operational block must reach EPIC or a story"
            )

    if spec_ids:
        missing = set(spec_ids) - set(rows_by_block)
        extra = set(rows_by_block) - set(spec_ids)
        if missing:
            errors.append(
                f"epic.md: SPEC blocks missing from distribution: {', '.join(sorted(missing))}"
            )
        if extra:
            errors.append(
                f"epic.md: distribution references unknown blocks: {', '.join(sorted(extra))}"
            )

    found: dict[str, Path] = {}
    for path in story_files:
        match = STORY_FILE_RE.match(path.name)
        identifier = match.group(1) if match else ""
        if identifier in found:
            errors.append(
                f"{path.name}: duplicates story identifier already used by {found[identifier].name}"
            )
            continue
        found[identifier] = path
    for identifier in sorted(set(found) - set(declared)):
        errors.append(
            f"{found[identifier].name}: story concept is not declared in epic.md stories"
        )

    for entry in entries:
        identifier = as_text(entry.get("id"))
        concept = as_text(entry.get("concept"))
        concept_path = Path(concept) if concept else None
        if concept_path is None or concept_path.is_absolute():
            errors.append(
                f"epic.md: {identifier} concept '{concept}' must be a relative path"
            )
            continue
        path = (directory / concept_path).resolve()
        if path.parent != directory.resolve():
            errors.append(
                f"epic.md: {identifier} concept '{concept}' must stay inside the EPIC directory"
            )
            continue
        if not path.is_file():
            errors.append(f"epic.md: {identifier} concept '{concept}' does not exist")
            continue
        file_match = STORY_FILE_RE.match(path.name)
        if not file_match or file_match.group(1) != identifier:
            errors.append(
                f"epic.md: {identifier} concept path must name its STORY-NNN-SSS file"
            )
            continue
        if identifier in found and found[identifier].resolve() != path:
            errors.append(
                f"epic.md: {identifier} concept path does not match {found[identifier].name}"
            )
        try:
            story = read_document(path)
        except (FrontmatterError, OSError) as error:
            errors.append(str(error))
            continue
        if not story.data:
            errors.append(f"{path.name}: missing YAML frontmatter")
            continue
        mapped = frozenset(
            row.block_id for row in rows if identifier in row.destinations
        )
        validate_story_concept(
            story, entry, number, spec_ids, mapped, resolved_stage, errors
        )

    validate_index(directory / "index.md", story_files, errors)
    validate_local_links(epic, "epic.md", errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one EPIC concept directory.")
    parser.add_argument(
        "epic_directory", type=Path, help="EPIC directory or its epic.md"
    )
    parser.add_argument(
        "--stage",
        choices=("working", "published"),
        help="override the lifecycle stage inferred from the path",
    )
    args = parser.parse_args()

    errors = validate(args.epic_directory, args.stage)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"epic-management: {args.epic_directory} is a valid EPIC concept directory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
