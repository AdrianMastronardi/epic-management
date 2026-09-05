#!/usr/bin/env python3
"""Shared Open Knowledge Format helpers for the epic-management skill.

Parses the restricted frontmatter style documented in references/okf-bundle.md.
PyYAML is used when importable; otherwise a strict parser for that subset runs,
so the bundled validators work without third-party dependencies.
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

try:  # pragma: no cover - environment dependent
    import yaml as _yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - environment dependent
    _yaml = None


ACTOR_RE = re.compile(
    r"^(?:human:[A-Za-z0-9._-]+|process:[A-Za-z0-9._-]+|[A-Za-z0-9._-]+/[A-Za-z0-9._+-]+)$"
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
LINK_RE = re.compile(r"\[[^\]^][^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:")
FOOTNOTE_REF_RE = re.compile(r"\[\^([^\]]+)\](?!:)")
PLACEHOLDER_RE = re.compile(r"\{\{[^{}]+\}\}")
TEMP_REF_RE = re.compile(r"(?<![A-Za-z0-9_.-])tmp/")
DRAFT_WORD_RE = re.compile(r"\bdrafts?\b", re.IGNORECASE)
LEADING_ZERO_INTEGER_RE = re.compile(r"^[+-]?0\d+$")

STATUS_VALUES = ("draft", "stable", "deprecated")
EPIC_STATUS_VALUES = ("Active", "Blocked", "Completed", "Cancelled")
RESERVED_NAMES = ("index.md", "log.md")
OKF_VERSION = "0.2"


class FrontmatterError(Exception):
    """Raised when a frontmatter block cannot be parsed."""


class Document:
    """One markdown file split into frontmatter data and body lines."""

    def __init__(
        self, path: Path, data: dict, body: list[str], body_offset: int, text: str
    ):
        self.path = path
        self.data = data
        self.body = body
        self.body_offset = body_offset
        self.text = text

    @property
    def body_text(self) -> str:
        return "\n".join(self.body)

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def has(self, key: str) -> bool:
        return key in self.data


def read_document(path: Path) -> Document:
    """Read a markdown file and parse its frontmatter block, if any."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return Document(path, {}, lines, 1, text)
    end = next(
        (index for index in range(1, len(lines)) if lines[index].strip() == "---"),
        None,
    )
    if end is None:
        raise FrontmatterError(f"{path}: frontmatter block is not closed by '---'")
    data = parse_yaml("\n".join(lines[1:end]), path)
    if not isinstance(data, dict):
        raise FrontmatterError(f"{path}: frontmatter must be a mapping")
    return Document(path, data, lines[end + 1 :], end + 2, text)


def has_frontmatter(path: Path) -> bool:
    with path.open(encoding="utf-8") as handle:
        return handle.readline().strip() == "---"


def parse_yaml(text: str, path: Path) -> dict:
    if _yaml is not None:
        try:
            return _yaml.safe_load(text) or {}
        except Exception as error:  # pragma: no cover - depends on input
            raise FrontmatterError(
                f"{path}: invalid YAML frontmatter: {error}"
            ) from error
    lines = [
        line for line in text.splitlines() if line.strip() and not _is_comment(line)
    ]
    value, index = _parse_block(lines, 0, _indent_of(lines[0]) if lines else 0, path)
    if index != len(lines):
        raise FrontmatterError(
            f"{path}: unsupported frontmatter style near {lines[index]!r}"
        )
    return value if isinstance(value, dict) else {}


def _is_comment(line: str) -> bool:
    return line.lstrip().startswith("#")


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_block(lines: list[str], index: int, indent: int, path: Path):
    if index >= len(lines):
        return None, index
    if lines[index].lstrip(" ").startswith("- "):
        return _parse_sequence(lines, index, indent, path)
    return _parse_mapping(lines, index, indent, path)


def _parse_sequence(lines: list[str], index: int, indent: int, path: Path):
    items: list = []
    while index < len(lines):
        line = lines[index]
        if _indent_of(line) != indent or not line.lstrip(" ").startswith("- "):
            break
        rest = line.lstrip(" ")[2:].strip()
        child = [" " * (indent + 2) + rest] if rest else []
        index += 1
        while index < len(lines) and _indent_of(lines[index]) > indent:
            child.append(lines[index])
            index += 1
        if not child:
            items.append(None)
            continue
        if len(child) == 1 and not _looks_like_key(rest):
            items.append(_parse_scalar(rest, path))
            continue
        value, consumed = _parse_block(child, 0, indent + 2, path)
        if consumed != len(child):
            raise FrontmatterError(f"{path}: unsupported list item near {rest!r}")
        items.append(value)
    return items, index


def _parse_mapping(lines: list[str], index: int, indent: int, path: Path):
    mapping: dict = {}
    while index < len(lines):
        line = lines[index]
        current = _indent_of(line)
        if current < indent or line.lstrip(" ").startswith("- "):
            break
        if current != indent:
            raise FrontmatterError(
                f"{path}: inconsistent indentation at {line.strip()!r}"
            )
        stripped = line.strip()
        if ":" not in stripped:
            raise FrontmatterError(f"{path}: expected 'key: value' at {stripped!r}")
        key, _, rest = stripped.partition(":")
        key = key.strip()
        rest = rest.strip()
        index += 1
        if rest:
            mapping[key] = _parse_scalar(rest, path)
            continue
        if index < len(lines) and (
            _indent_of(lines[index]) > indent
            or (
                _indent_of(lines[index]) == indent
                and lines[index].lstrip(" ").startswith("- ")
            )
        ):
            child_indent = _indent_of(lines[index])
            mapping[key], index = _parse_block(lines, index, child_indent, path)
            continue
        mapping[key] = None
    return mapping, index


def _looks_like_key(text: str) -> bool:
    if text.startswith(("{", "[", '"', "'")):
        return False
    key, separator, _ = text.partition(":")
    return bool(separator) and " " not in key.strip()


def _parse_scalar(text: str, path: Path):
    text = text.strip()
    if not text:
        return None
    if text.startswith("{") and text.endswith("}"):
        result = {}
        for part in _split_flow(text[1:-1]):
            key, separator, value = part.partition(":")
            if not separator:
                raise FrontmatterError(f"{path}: expected 'key: value' in {text!r}")
            result[key.strip()] = _parse_scalar(value, path)
        return result
    if text.startswith("[") and text.endswith("]"):
        return [_parse_scalar(part, path) for part in _split_flow(text[1:-1])]
    if len(text) > 1 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    if LEADING_ZERO_INTEGER_RE.match(text):
        raise FrontmatterError(
            f"{path}: quote integer-like value {text!r} so its leading zero survives"
        )
    return text


def _split_flow(text: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    quote = ""
    current = ""
    for character in text:
        if quote:
            current += character
            if character == quote:
                quote = ""
            continue
        if character in "\"'":
            quote = character
            current += character
            continue
        if character in "{[":
            depth += 1
        elif character in "}]":
            depth -= 1
        if character == "," and depth == 0:
            parts.append(current)
            current = ""
            continue
        current += character
    if current.strip():
        parts.append(current)
    return [part.strip() for part in parts if part.strip()]


def as_text(value) -> str:
    """Render a parsed scalar back to the text a producer wrote."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, dt.datetime):
        rendered = value.isoformat()
        return rendered.replace("+00:00", "Z")
    if isinstance(value, dt.date):
        return value.isoformat()
    return str(value)


def as_list(value) -> list:
    """Return a list for a value that may be a bare mapping or scalar."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def check_actor(value, label: str, errors: list[str]) -> None:
    text = as_text(value)
    if not text:
        errors.append(f"{label}: actor is missing")
    elif not ACTOR_RE.match(text):
        errors.append(
            f"{label}: '{text}' does not follow the actor convention "
            "(<producer>/<version>, human:<id>, or process:<id>)"
        )


def check_date(value, label: str, errors: list[str]) -> None:
    text = as_text(value)
    if not DATE_RE.match(text):
        errors.append(f"{label}: '{text}' is not an ISO 8601 YYYY-MM-DD date")
        return
    try:
        dt.date.fromisoformat(text)
    except ValueError:
        errors.append(f"{label}: '{text}' is not a real calendar date")


def check_datetime(value, label: str, errors: list[str]) -> None:
    text = as_text(value)
    if not DATETIME_RE.match(text):
        errors.append(f"{label}: '{text}' is not an ISO 8601 datetime")
        return
    try:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label}: '{text}' is not a real ISO 8601 datetime")
        return
    if parsed.tzinfo is None:
        errors.append(f"{label}: '{text}' must include a UTC offset")


def check_trust(
    document: Document, label: str, errors: list[str], require_human: bool
) -> None:
    """Validate the generated and verified frontmatter families."""
    generated = document.get("generated")
    if not isinstance(generated, dict):
        errors.append(f"{label}: generated must be a mapping with 'by' and 'at'")
    else:
        check_actor(generated.get("by"), f"{label}: generated.by", errors)
        check_datetime(generated.get("at"), f"{label}: generated.at", errors)
    entries = as_list(document.get("verified"))
    for position, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append(
                f"{label}: verified[{position}] must be a mapping with 'by' and 'at'"
            )
            continue
        check_actor(entry.get("by"), f"{label}: verified[{position}].by", errors)
        check_datetime(entry.get("at"), f"{label}: verified[{position}].at", errors)
    if require_human and not human_verifiers(document):
        errors.append(f"{label}: requires a verified entry by a human:<id> actor")


def human_verifiers(document: Document) -> list[str]:
    return [
        as_text(entry.get("by"))
        for entry in as_list(document.get("verified"))
        if isinstance(entry, dict) and as_text(entry.get("by")).startswith("human:")
    ]


def check_status(document: Document, label: str, errors: list[str], stage: str) -> None:
    status = as_text(document.get("status"))
    if status not in STATUS_VALUES:
        errors.append(f"{label}: status must be one of {', '.join(STATUS_VALUES)}")
        return
    if stage == "working" and status != "draft":
        errors.append(f"{label}: a concept under tmp/ must carry status: draft")
    if stage == "published" and status == "draft":
        errors.append(
            f"{label}: a published concept must carry status: stable or deprecated"
        )


def check_stale_after(document: Document, label: str, errors: list[str]) -> None:
    if document.has("stale_after") and document.get("stale_after") is not None:
        check_date(document.get("stale_after"), f"{label}: stale_after", errors)


def check_sources(
    document: Document, label: str, errors: list[str], required: bool
) -> set[str]:
    """Validate the sources family and return the declared source identifiers."""
    entries = as_list(document.get("sources"))
    if not entries:
        if required:
            errors.append(f"{label}: sources must record at least one material")
        return set()
    identifiers: set[str] = set()
    for position, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append(f"{label}: sources[{position}] must be a mapping")
            continue
        if not as_text(entry.get("resource")):
            errors.append(f"{label}: sources[{position}] requires a resource")
        identifier = as_text(entry.get("id"))
        if identifier:
            if identifier in identifiers:
                errors.append(f"{label}: duplicate source id '{identifier}'")
            identifiers.add(identifier)
        if entry.get("author") is not None:
            check_actor(
                entry.get("author"), f"{label}: sources[{position}].author", errors
            )
        if entry.get("last_modified") is not None:
            check_date(
                entry.get("last_modified"),
                f"{label}: sources[{position}].last_modified",
                errors,
            )
    return identifiers


def check_footnotes(
    document: Document, label: str, errors: list[str], identifiers: set[str]
) -> None:
    """Every footnote label used in a body must exist in that concept's sources."""
    used = {
        match
        for line in document.body
        for match in FOOTNOTE_REF_RE.findall(line)
        if not FOOTNOTE_DEF_RE.match(line.strip())
    }
    defined = {
        match.group(1)
        for line in document.body
        if (match := FOOTNOTE_DEF_RE.match(line.strip())) is not None
    }
    for unknown in sorted((used | defined) - identifiers):
        errors.append(f"{label}: footnote '[^{unknown}]' has no matching sources[].id")


def check_hygiene(document: Document, label: str, errors: list[str]) -> None:
    """Reject placeholders, temporary paths, and prose that labels the concept a draft."""
    if PLACEHOLDER_RE.search(document.text):
        errors.append(f"{label}: contains unresolved {{{{PLACEHOLDER}}}} values")
    if TEMP_REF_RE.search(document.text):
        errors.append(f"{label}: contains a forbidden tmp/ reference")
    if DRAFT_WORD_RE.search(document.body_text):
        errors.append(f"{label}: body must not label the concept a draft")


def body_links(document: Document) -> list[str]:
    return [target for line in document.body for target in LINK_RE.findall(line)]


def heading_positions(lines: list[str], prefix: str) -> list[tuple[str, int]]:
    return [
        (line, index) for index, line in enumerate(lines) if line.startswith(prefix)
    ]


def section_bounds(
    lines: list[str], heading: str, level: str = "## "
) -> tuple[int, int]:
    start = lines.index(heading)
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith(level)
        ),
        len(lines),
    )
    return start, end


def iter_concepts(root: Path):
    """Yield every non-reserved markdown file in a bundle, sorted by path."""
    for path in sorted(root.rglob("*.md")):
        if path.name not in RESERVED_NAMES:
            yield path


def is_bundle_root(path: Path) -> bool:
    """A bundle root is the directory whose index.md declares okf_version."""
    index = path / "index.md"
    if not index.is_file():
        return False
    try:
        document = read_document(index)
    except (FrontmatterError, OSError):
        return False
    return "okf_version" in document.data


def infer_stage(directory: Path) -> str:
    """An EPIC directory is published when it sits inside a bundle root."""
    return "published" if is_bundle_root(directory.resolve().parent) else "working"
