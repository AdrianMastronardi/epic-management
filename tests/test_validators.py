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
SECOND_STORY_FILE = "STORY-001-002-consume-example.md"
DEPENDENCY_HEADER = """| Producer | Consumer | Output | Phase | Release condition | Projection | Spec |
| -------- | -------- | ------ | ----- | ----------------- | ---------- | ---- |
"""


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

    def create_dependent_epic(self, dependency_rows: str) -> Path:
        """Extend the working fixture with a second story and a dependency table."""
        epic = self.create_epic(published=False)
        path = epic / "epic.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            f"    concept: ./{STORY_FILE}\n",
            f"    concept: ./{STORY_FILE}\n"
            "  - id: STORY-001-002\n"
            "    title: Consume example\n"
            f"    concept: ./{SECOND_STORY_FILE}\n",
        )
        text = text.replace(
            "## Affected components",
            "### SPEC-001-002: Example contract\n\n"
            "Publish the example contract.\n\n"
            "## Affected components",
        )
        text = text.replace("None.\n", DEPENDENCY_HEADER + dependency_rows)
        text += "| SPEC-001-002 | operational | STORY-001-001, STORY-001-002 |\n"
        path.write_text(text, encoding="utf-8")

        first = epic / STORY_FILE
        story = first.read_text(encoding="utf-8")
        first.write_text(
            story.replace(
                "applicable_blocks: [SPEC-001-001]",
                "applicable_blocks: [SPEC-001-001, SPEC-001-002]",
            ).replace(
                "\n## Tasks",
                "- [SPEC-001-002: Example contract](./epic.md#spec-001-002-example-contract)\n"
                "\n## Tasks",
            ),
            encoding="utf-8",
        )
        self.write(
            epic / SECOND_STORY_FILE,
            story.replace(
                "STORY-001-001 — Implement example", "STORY-001-002 — Consume example"
            )
            .replace(
                "applicable_blocks: [SPEC-001-001]", "applicable_blocks: [SPEC-001-002]"
            )
            .replace(
                "- [SPEC-001-001: Example behavior](./epic.md#spec-001-001-example-behavior)",
                "- [SPEC-001-002: Example contract](./epic.md#spec-001-002-example-contract)",
            ),
        )
        index = epic / "index.md"
        index.write_text(
            index.read_text(encoding="utf-8")
            + f"- [STORY-001-002 — Consume example]({SECOND_STORY_FILE}) - Consume the example.\n",
            encoding="utf-8",
        )
        return epic

    def test_dependency_table_accepts_each_projection(self) -> None:
        epic = self.create_dependent_epic(
            "| STORY-001-001 | STORY-001-002 | Contract | start | Contract merged | native | SPEC-001-002 |\n"
            "| STORY-001-002 | STORY-001-001 | Client | integrate | Client merged | documented | [SPEC-001-002](#spec-001-002-example-contract) |\n"
            "| External schema registry | STORY-001-002 | Registry access | complete | Access granted | documented | SPEC-001-002 |\n"
        )
        self.assertEqual(validate_epic(epic, None), [])

    def assert_native_projection_rejected(self, row: str) -> None:
        epic = self.create_dependent_epic(row)
        self.assertTrue(
            any(
                "native projection requires a start-phase dependency" in error
                for error in validate_epic(epic, None)
            )
        )

    def test_dependency_table_accepts_escaped_pipes(self) -> None:
        for output in (r"`Result = Ok \| Error`", r"Contract \\", r"Contract \\\| fallback"):
            with self.subTest(output=output):
                epic = self.create_dependent_epic(
                    f"| STORY-001-001 | STORY-001-002 | {output}| start | "
                    r"Check `ok\|error` passes | native | SPEC-001-002 |" + "\n"
                )
                self.assertEqual(validate_epic(epic, None), [])

    def test_dependency_table_rejects_partial_spec_identifiers(self) -> None:
        for block in ("SPEC-001-0029", "SPEC-001-002suffix", "SPEC-001-002-extra"):
            for spec in (block, f"SPEC-001-002, {block}"):
                with self.subTest(spec=spec):
                    epic = self.create_dependent_epic(
                        "| STORY-001-001 | STORY-001-002 | Contract | start | "
                        f"Contract merged | native | {spec} |\n"
                    )
                    self.assertTrue(
                        any(
                            f"dependency references unknown {block}" in error
                            for error in validate_epic(epic, None)
                        )
                    )

    def test_native_projection_requires_start_phase(self) -> None:
        self.assert_native_projection_rejected(
            "| STORY-001-001 | STORY-001-002 | Contract | complete | Contract merged | native | SPEC-001-002 |\n"
        )

    def test_native_projection_requires_story_producer(self) -> None:
        self.assert_native_projection_rejected(
            "| External team | STORY-001-002 | Contract | start | Contract merged | native | SPEC-001-002 |\n"
        )

    def test_dependency_table_rejects_inconsistent_references(self) -> None:
        epic = self.create_dependent_epic(
            "| STORY-001-009 | STORY-001-002 | Contract | begin | Contract merged | documented | SPEC-001-001 |\n"
        )
        errors = validate_epic(epic, None)
        for expected in (
            "producer STORY-001-009 is not a declared story",
            "phase must be one of start, integrate, complete",
            "SPEC-001-001 is not routed to STORY-001-002",
        ):
            self.assertTrue(any(expected in error for error in errors), expected)

    def test_native_dependency_cycle_is_rejected(self) -> None:
        epic = self.create_dependent_epic(
            "| STORY-001-001 | STORY-001-002 | Contract | start | Contract merged | native | SPEC-001-002 |\n"
            "| STORY-001-002 | STORY-001-001 | Client | start | Client merged | native | SPEC-001-002 |\n"
        )
        self.assertTrue(
            any(
                "native dependency projections form a cycle" in error
                for error in validate_epic(epic, None)
            )
        )

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
