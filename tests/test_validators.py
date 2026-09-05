from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import okf  # noqa: E402
from validate_epic import validate as validate_epic  # noqa: E402
from validate_okf_bundle import validate as validate_bundle  # noqa: E402


EPIC_DIRECTORY = "EPIC-001-example"
STORY_FILE = "STORY-001-001-implement-example.md"


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def create_epic(self, published: bool = True, dot_prefix: bool = False) -> Path:
        if published:
            bundle = self.root / "docs" / "epics"
            epic = bundle / EPIC_DIRECTORY
            link_prefix = "./" if dot_prefix else ""
            self.write(
                bundle / "index.md",
                f"""---
okf_version: "0.2"
---

# EPIC index

## Active

- [EPIC-001 — Example]({link_prefix}{EPIC_DIRECTORY}/index.md) - Exercise the validators.
""",
            )
            status = "stable"
            epic_resource = (
                'resource: "https://github.com/example/repository/issues/1"\n'
            )
            story_resource = (
                'resource: "https://github.com/example/repository/issues/2"\n'
            )
            verified = (
                'verified:\n  - { by: "human:reviewer", at: 2026-09-05T08:01:00Z }\n'
            )
            story_entry_resource = (
                '    resource: "https://github.com/example/repository/issues/2"\n'
            )
        else:
            epic = self.root / "tmp" / EPIC_DIRECTORY
            status = "draft"
            epic_resource = ""
            story_resource = ""
            verified = ""
            story_entry_resource = ""

        self.write(
            epic / "index.md",
            f"""# EPIC-001 — Example

- [EPIC document](epic.md) - Exercise the validators.

## Stories

- [STORY-001-001 — Implement example]({STORY_FILE}) - Implement the example.
""",
        )
        self.write(
            epic / "epic.md",
            f"""---
type: EPIC
title: "EPIC-001 — Example"
description: Exercise the validators.
{epic_resource}status: {status}
generated: {{ by: codex/gpt-5, at: 2026-09-05T08:00:00Z }}
{verified}sources:
  - id: example
    resource: "https://example.com/spec"
    title: Example specification
epic_number: "001"
epic_status: Active
started_on: 2026-09-05
completed_on:
stories:
  - id: STORY-001-001
    title: Implement example
    concept: ./{STORY_FILE}
{story_entry_resource}---

## Description

Exercise the validators.

## Functional and technical specification

### SPEC-001-001: Example behavior

Implement the example behavior.

## Affected components

- example

## Dependencies

None.

## Execution order

Implement the only story.

## Acceptance criteria

- [ ] The example works.

## GitHub distribution

| Block        | Class       | Destination   |
| ------------ | ----------- | ------------- |
| SPEC-001-001 | operational | STORY-001-001 |
""",
        )
        self.write(
            epic / STORY_FILE,
            f"""---
type: Story
title: "STORY-001-001 — Implement example"
description: Implement the example.
{story_resource}status: {status}
generated: {{ by: codex/gpt-5, at: 2026-09-05T08:00:00Z }}
{verified}epic: EPIC-001
epic_concept: ./epic.md
components: [example]
applicable_blocks: [SPEC-001-001]
---

## Description

Implement the example.

## Applicable specification

- [SPEC-001-001: Example behavior](./epic.md#spec-001-001-example-behavior)

## Tasks

- [ ] Implement it.

## Acceptance criteria

- [ ] It works.

## Quality checklist

- [ ] Checks pass.
""",
        )
        return epic

    def test_valid_epic_passes_with_pyyaml_and_fallback(self) -> None:
        epic = self.create_epic()
        self.assertEqual(validate_epic(epic, None), [])
        with mock.patch.object(okf, "_yaml", None):
            self.assertEqual(validate_epic(epic, None), [])

    def test_valid_working_epic_passes(self) -> None:
        epic = self.create_epic(published=False)
        self.assertEqual(validate_epic(epic, None), [])

    def test_story_concept_must_stay_inside_epic_directory(self) -> None:
        epic = self.create_epic()
        outside = self.root / "outside-story.md"
        (epic / STORY_FILE).replace(outside)
        path = epic / "epic.md"
        text = path.read_text(encoding="utf-8").replace(
            f"concept: ./{STORY_FILE}", "concept: ../../../outside-story.md"
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(
            any(
                "must stay inside the EPIC directory" in error
                for error in validate_epic(epic, None)
            )
        )

    def test_story_resource_must_match_epic_index(self) -> None:
        epic = self.create_epic()
        path = epic / STORY_FILE
        text = path.read_text(encoding="utf-8").replace("issues/2", "issues/999")
        path.write_text(text, encoding="utf-8")
        self.assertTrue(
            any("resource must match" in error for error in validate_epic(epic, None))
        )

    def test_epic_concept_must_resolve_to_sibling(self) -> None:
        epic = self.create_epic()
        path = epic / STORY_FILE
        text = path.read_text(encoding="utf-8").replace(
            "epic_concept: ./epic.md", "epic_concept: ./not-the-epic.md"
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(
            any(
                "must resolve to the sibling" in error
                for error in validate_epic(epic, None)
            )
        )

    def test_applicable_links_must_match_frontmatter(self) -> None:
        epic = self.create_epic()
        path = epic / STORY_FILE
        text = path.read_text(encoding="utf-8").replace(
            "- [SPEC-001-001: Example behavior](./epic.md#spec-001-001-example-behavior)",
            "SPEC-001-001 is applicable, but it is not linked.",
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(
            any(
                "Applicable specification links differ" in error
                for error in validate_epic(epic, None)
            )
        )

    def test_fallback_rejects_unquoted_leading_zero(self) -> None:
        epic = self.create_epic()
        path = epic / "epic.md"
        text = path.read_text(encoding="utf-8").replace(
            'epic_number: "001"', "epic_number: 001"
        )
        path.write_text(text, encoding="utf-8")
        with mock.patch.object(okf, "_yaml", None):
            self.assertTrue(
                any(
                    "quote integer-like value" in error
                    for error in validate_epic(epic, None)
                )
            )

    def test_invalid_calendar_date_is_rejected(self) -> None:
        epic = self.create_epic()
        path = epic / "epic.md"
        text = path.read_text(encoding="utf-8").replace(
            "started_on: 2026-09-05", 'started_on: "2026-99-99"'
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(
            any(
                "not a real calendar date" in error
                for error in validate_epic(epic, None)
            )
        )

    def test_bundle_index_accepts_dot_prefixed_epic_link(self) -> None:
        epic = self.create_epic(dot_prefix=True)
        errors, warnings = validate_bundle(epic.parent, strict=True)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_working_templates_omit_publication_and_verification_fields(self) -> None:
        epic_template = okf.read_document(
            PROJECT_ROOT / "assets" / "epic-concept-template.md"
        )
        story_template = okf.read_document(
            PROJECT_ROOT / "assets" / "story-concept-template.md"
        )
        self.assertFalse(epic_template.has("resource"))
        self.assertFalse(epic_template.has("verified"))
        self.assertFalse(story_template.has("resource"))
        self.assertFalse(story_template.has("verified"))
        for story in okf.as_list(epic_template.get("stories")):
            self.assertNotIn("resource", story)

    def test_bundle_index_template_does_not_link_missing_backlog(self) -> None:
        text = (PROJECT_ROOT / "assets" / "bundle-index-template.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("](backlog.md)", text)


if __name__ == "__main__":
    unittest.main()
