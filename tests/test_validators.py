from __future__ import annotations

import subprocess
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

    def create_dependent_epic(
        self, dependency_rows: str, story_count: int = 2, published: bool = False
    ) -> Path:
        """Extend a complete fixture with stories and a dependency table."""
        epic = self.create_epic(published=published)
        path = epic / "epic.md"
        text = path.read_text(encoding="utf-8")
        entries = ""
        for serial in range(1, story_count + 1):
            name = "Implement example" if serial == 1 else "Consume example"
            slug = "implement-example" if serial == 1 else "consume-example"
            entries += (
                f"  - id: STORY-001-{serial:03}\n"
                f"    title: {name}\n"
                f"    concept: ./STORY-001-{serial:03}-{slug}.md\n"
            )
            if published:
                entries += f'    resource: "https://github.com/example/repository/issues/{serial + 1}"\n'
        before, rest = text.split("stories:\n", 1)
        _, after = rest.split("---", 1)
        text = before + "stories:\n" + entries + "---" + after
        text = text.replace(
            "## Affected components",
            "### SPEC-001-002: Example contract\n\n"
            "Publish the example contract.\n\n"
            "## Affected components",
        )
        text = text.replace("None.\n", DEPENDENCY_HEADER + dependency_rows)
        destinations = ", ".join(
            f"STORY-001-{serial:03}" for serial in range(1, story_count + 1)
        )
        text += f"| SPEC-001-002 | operational | {destinations} |\n"
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
        for serial in range(2, story_count + 1):
            identifier = f"STORY-001-{serial:03}"
            filename = f"{identifier}-consume-example.md"
            self.write(
                epic / filename,
                story.replace(
                    "STORY-001-001 — Implement example",
                    f"{identifier} — Consume example",
                )
                .replace(
                    "applicable_blocks: [SPEC-001-001]",
                    "applicable_blocks: [SPEC-001-002]",
                )
                .replace(
                    "- [SPEC-001-001: Example behavior](./epic.md#spec-001-001-example-behavior)",
                    "- [SPEC-001-002: Example contract](./epic.md#spec-001-002-example-contract)",
                )
                .replace("issues/2", f"issues/{serial + 1}"),
            )
            index = epic / "index.md"
            index.write_text(
                index.read_text(encoding="utf-8")
                + f"- [{identifier} — Consume example]({filename}) - Consume the example.\n",
                encoding="utf-8",
            )
        return epic

    def test_dependency_table_accepts_each_projection(self) -> None:
        epic = self.create_dependent_epic(
            "| STORY-001-001 | STORY-001-002 | Contract | start | Contract merged | native | SPEC-001-002 |\n"
            "| STORY-001-001 | STORY-001-002 | Client | integrate | Client merged | documented | [SPEC-001-002](#spec-001-002-example-contract) |\n"
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
        for output in (
            r"`Result = Ok \| Error`",
            r"Contract \\",
            r"Contract \\\| fallback",
        ):
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
                "story dependencies form a cycle" in error
                for error in validate_epic(epic, None)
            )
        )

    @staticmethod
    def dependency_row(
        producer: int, consumer: int, phase: str = "start", projection: str = "native"
    ) -> str:
        return (
            f"| STORY-001-{producer:03} | STORY-001-{consumer:03} | "
            r"Contract `A \| B` | "
            f"{phase} | Contract merged | {projection} | SPEC-001-002 |\n"
        )

    def check_dependency_graph(
        self, rows: str, story_count: int, expected_path: str | None
    ) -> None:
        for embedded in (False, True):
            with tempfile.TemporaryDirectory() as directory:
                with mock.patch.object(self, "root", Path(directory)):
                    epic = self.create_dependent_epic(rows, story_count, published=True)
                    if embedded:
                        self.embed_collection(epic)
                    for parser in (okf._yaml, None):
                        with self.subTest(embedded=embedded, fallback=parser is None):
                            with mock.patch.object(okf, "_yaml", parser):
                                epic_errors = validate_epic(epic, None)
                                bundle_errors, warnings = validate_bundle(
                                    epic.parent, strict=True
                                )
                            self.assertEqual(warnings, [])
                            if expected_path is None:
                                self.assertEqual(epic_errors, [])
                                self.assertEqual(bundle_errors, [])
                                continue
                            for errors in (epic_errors, bundle_errors):
                                diagnostic = next(
                                    (e for e in errors if "form a cycle" in e), ""
                                )
                                self.assertIn(expected_path, diagnostic)
                                self.assertIn("epic.md line ", diagnostic)
                                self.assertIn("phase=", diagnostic)
                                self.assertIn("projection=", diagnostic)
                            self.assertTrue(
                                any(
                                    f"{EPIC_DIRECTORY}/epic.md:" in e
                                    for e in bundle_errors
                                ),
                                bundle_errors,
                            )

    def test_all_dependency_phases_and_projections_participate_in_cycles(self) -> None:
        variants = (
            ("start", "native", "complete", "documented"),
            ("integrate", "documented", "complete", "documented"),
            ("start", "documented", "integrate", "documented"),
            ("start", "native", "start", "native"),
        )
        for phase_a, projection_a, phase_b, projection_b in variants:
            with self.subTest(phases=(phase_a, phase_b)):
                rows = self.dependency_row(1, 2, phase_a, projection_a)
                rows += self.dependency_row(2, 1, phase_b, projection_b)
                self.check_dependency_graph(
                    rows,
                    2,
                    "STORY-001-001 requires STORY-001-002 requires STORY-001-001",
                )

    def test_transitive_cycle_includes_every_implicated_edge(self) -> None:
        rows = self.dependency_row(1, 2)
        rows += self.dependency_row(2, 3, "integrate", "documented")
        rows += self.dependency_row(3, 1, "complete", "documented")
        self.check_dependency_graph(
            rows,
            3,
            "STORY-001-001 requires STORY-001-003 requires STORY-001-002 requires STORY-001-001",
        )
        epic = self.create_dependent_epic(rows, 3)
        diagnostic = next(e for e in validate_epic(epic, None) if "form a cycle" in e)
        for metadata in (
            "phase=start, projection=native",
            "phase=integrate, projection=documented",
            "phase=complete, projection=documented",
        ):
            self.assertIn(metadata, diagnostic)

    def test_self_dependencies_are_rejected_for_both_projections(self) -> None:
        for phase, projection in (("start", "native"), ("complete", "documented")):
            rows = self.dependency_row(1, 1, phase, projection)
            self.check_dependency_graph(rows, 2, "STORY-001-001 requires STORY-001-001")
            epic = self.create_dependent_epic(rows)
            self.assertTrue(
                any("cannot depend on itself" in e for e in validate_epic(epic, None))
            )

    def test_acyclic_dependency_graphs_pass_both_validators(self) -> None:
        graphs = {
            "independent": "",
            "linear": self.dependency_row(1, 2) + self.dependency_row(2, 3),
            "diamond": (
                self.dependency_row(1, 2)
                + self.dependency_row(1, 3)
                + self.dependency_row(2, 4, "integrate", "documented")
                + self.dependency_row(3, 4, "complete", "documented")
            ),
            "mixed_and_external": (
                self.dependency_row(1, 2)
                + self.dependency_row(1, 2, "integrate", "documented")
                + self.dependency_row(2, 3, "complete", "documented")
                + "| External registry | STORY-001-004 | Access | complete | Access granted | documented | SPEC-001-002 |\n"
            ),
        }
        for name, rows in graphs.items():
            with self.subTest(graph=name):
                self.check_dependency_graph(rows, 4, None)

    def test_cycle_path_is_deterministic_when_rows_are_reordered(self) -> None:
        rows = [self.dependency_row(1, 2), self.dependency_row(2, 1)]
        paths = []
        for ordered in (rows, list(reversed(rows))):
            epic = self.create_dependent_epic("".join(ordered))
            diagnostic = next(
                e for e in validate_epic(epic, None) if "form a cycle" in e
            )
            paths.append(diagnostic.split(" (", 1)[0])
        self.assertEqual(paths[0], paths[1])

    def test_bundle_preserves_dependency_metadata_and_routing_checks(self) -> None:
        invalid = {
            "unknown story": ("STORY-001-001", "STORY-001-009", "not a declared story"),
            "unknown consumer": (
                "STORY-001-002",
                "STORY-001-009",
                "consumer STORY-001-009",
            ),
            "invalid phase": ("| start |", "| begin |", "phase must be one of"),
            "invalid projection": (
                "| native |",
                "| optional |",
                "projection must be one of",
            ),
            "native completion": (
                "| start |",
                "| complete |",
                "native projection requires",
            ),
            "unknown spec": ("SPEC-001-002", "SPEC-001-099", "unknown SPEC-001-099"),
            "unrouted spec": (
                "SPEC-001-002",
                "SPEC-001-001",
                "not routed to STORY-001-002",
            ),
            "wrong columns": ("| Contract merged |", "", "must have seven columns"),
            "empty output": (r"Contract `A \| B`", "", "requires an output"),
            "empty release": (
                "Contract merged",
                "",
                "requires an output and a release condition",
            ),
            "empty spec": ("SPEC-001-002", "", "must reference a SPEC block"),
        }
        for name, (old, new, expected) in invalid.items():
            with self.subTest(case=name):
                epic = self.create_dependent_epic(
                    self.dependency_row(1, 2).replace(old, new), published=True
                )
                for errors in (
                    validate_epic(epic, None),
                    validate_bundle(epic.parent, False)[0],
                ):
                    self.assertTrue(any(expected in e for e in errors), errors)

    def test_bundle_dependency_checks_preserve_okf_consumer_tolerances(self) -> None:
        epic = self.create_dependent_epic(self.dependency_row(1, 2), published=True)
        path = epic / "epic.md"
        text = path.read_text(encoding="utf-8").replace(
            "## Affected components",
            "### SPEC-001-003: Background\n\nContext only.\n\n## Affected components",
        )
        text += "| SPEC-001-003 | context | DOCUMENT |\n"
        path.write_text(text, encoding="utf-8")
        self.assertEqual(validate_epic(epic, None), [])
        self.assertEqual(validate_bundle(epic.parent, True), ([], []))
        path.write_text(
            text.replace(
                self.dependency_row(1, 2),
                self.dependency_row(1, 2).replace("SPEC-001-002", "SPEC-001-003"),
            ),
            encoding="utf-8",
        )
        for errors in (
            validate_epic(epic, None),
            validate_bundle(epic.parent, False)[0],
        ):
            self.assertTrue(
                any("SPEC-001-003 must be operational" in e for e in errors), errors
            )
        path.write_text(
            text.replace("status: stable", 'status: stable\nstale_after: "2027-04-17"'),
            encoding="utf-8",
        )
        story = epic / STORY_FILE
        story.write_text(
            story.read_text(encoding="utf-8") + "\n[Future knowledge](./future.md)\n",
            encoding="utf-8",
        )
        errors, warnings = validate_bundle(epic.parent, False)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 2, warnings)
        for expected in ("stale_after", "future.md"):
            self.assertTrue(any(expected in warning for warning in warnings), warnings)
        strict_errors, warnings = validate_bundle(epic.parent, True)
        self.assertEqual(len(strict_errors), 2)
        self.assertEqual(warnings, [])

    def test_informational_links_and_legacy_prose_do_not_become_edges(self) -> None:
        epic = self.create_dependent_epic(self.dependency_row(1, 2), published=True)
        for filename, target in (
            (STORY_FILE, SECOND_STORY_FILE),
            (SECOND_STORY_FILE, STORY_FILE),
        ):
            path = epic / filename
            path.write_text(
                path.read_text(encoding="utf-8")
                + f"\nRelated: [other story](./{target}).\n",
                encoding="utf-8",
            )
        self.assertEqual(validate_epic(epic, None), [])
        self.assertEqual(validate_bundle(epic.parent, True), ([], []))
        path = epic / "epic.md"
        text = path.read_text(encoding="utf-8").replace(
            DEPENDENCY_HEADER + self.dependency_row(1, 2),
            "STORY-001-001 depends on STORY-001-002; STORY-001-002 depends on STORY-001-001.\n",
        )
        path.write_text(text, encoding="utf-8")
        # Structural compatibility is not semantic assurance; workflow review is required.
        self.assertEqual(validate_epic(epic, None), [])
        self.assertEqual(validate_bundle(epic.parent, True), ([], []))

    def test_dependency_cycles_fail_through_both_cli_entry_points(self) -> None:
        for embedded in (False, True):
            with tempfile.TemporaryDirectory() as directory:
                with mock.patch.object(self, "root", Path(directory)):
                    epic = self.create_dependent_epic(
                        self.dependency_row(1, 2)
                        + self.dependency_row(2, 1, "complete", "documented"),
                        published=True,
                    )
                    if embedded:
                        self.embed_collection(epic)
                    for script, target in (
                        ("validate_epic.py", epic),
                        ("validate_okf_bundle.py", epic.parent),
                    ):
                        for options in ([], ["-S"]):
                            result = subprocess.run(
                                [
                                    sys.executable,
                                    "-B",
                                    *options,
                                    str(PROJECT_ROOT / "scripts" / script),
                                    str(target),
                                ],
                                capture_output=True,
                                text=True,
                                check=False,
                            )
                            self.assertEqual(
                                result.returncode, 1, result.stdout + result.stderr
                            )
                            self.assertIn(
                                "story dependencies form a cycle",
                                result.stdout + result.stderr,
                            )

    def test_bundle_reports_missing_dependency_distribution_without_a_traceback(
        self,
    ) -> None:
        for heading in (None, "## GitHub distributions", "## GitHub distribution "):
            with self.subTest(heading=heading):
                epic = self.create_dependent_epic(
                    self.dependency_row(1, 2)
                    + self.dependency_row(2, 1, "complete", "documented"),
                    published=True,
                )
                path = epic / "epic.md"
                text = path.read_text(encoding="utf-8")
                if heading is None:
                    text = text.split("## GitHub distribution")[0]
                else:
                    text = text.replace("## GitHub distribution", heading)
                path.write_text(text, encoding="utf-8")
                for parser in (okf._yaml, None):
                    with mock.patch.object(okf, "_yaml", parser):
                        errors, _ = validate_bundle(epic.parent, False)
                    self.assertTrue(
                        any(
                            "requires a GitHub distribution section" in e
                            for e in errors
                        ),
                        errors,
                    )
                    self.assertTrue(any("form a cycle" in e for e in errors), errors)
                result = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        str(PROJECT_ROOT / "scripts" / "validate_okf_bundle.py"),
                        str(epic.parent),
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 1)
                self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_formatted_story_ids_cannot_hide_dependency_cycles(self) -> None:
        for producer in (
            "`STORY-001-002`",
            "[STORY-001-002](./STORY-001-002-consume-example.md)",
            "[story-001-002](./STORY-001-002-consume-example.md)",
        ):
            for role in ("producer", "consumer"):
                with self.subTest(producer=producer, role=role):
                    first = self.dependency_row(1, 2)
                    second = self.dependency_row(2, 1, "complete", "documented")
                    if role == "producer":
                        second = second.replace("STORY-001-002", producer, 1)
                    else:
                        first = first.replace("STORY-001-002", producer, 1)
                    rows = first + second
                    self.check_dependency_graph(
                        rows,
                        2,
                        "STORY-001-001 requires STORY-001-002 requires STORY-001-001",
                    )
                    epic = self.create_dependent_epic(rows)
                    self.assertTrue(
                        any(
                            f"{role} must use the bare story identifier STORY-001-002"
                            in e
                            for e in validate_epic(epic, None)
                        )
                    )

    def test_dependency_diagnostics_reference_exact_row_lines(self) -> None:
        rows = self.dependency_row(1, 2)
        rows += self.dependency_row(2, 3, "integrate", "documented")
        rows += self.dependency_row(3, 1, "complete", "documented")
        epic = self.create_dependent_epic(rows, 3, published=True)
        lines = (epic / "epic.md").read_text(encoding="utf-8").splitlines()
        for errors in (
            validate_epic(epic, None),
            validate_bundle(epic.parent, False)[0],
        ):
            diagnostic = next(e for e in errors if "form a cycle" in e)
            for row in rows.splitlines():
                self.assertIn(
                    f"epic.md line {lines.index(row) + 1}, phase=", diagnostic
                )

    def test_bundle_checks_distribution_only_to_resolve_dependency_routing(
        self,
    ) -> None:
        rows = self.dependency_row(1, 2)
        epic = self.create_dependent_epic(rows, published=True)
        path = epic / "epic.md"
        text = (
            path.read_text(encoding="utf-8")
            + "| Extra | malformed | distribution | row |\n"
        )
        path.write_text(text, encoding="utf-8")
        errors, _ = validate_bundle(epic.parent, False)
        self.assertTrue(
            any("distribution row must have three columns" in e for e in errors), errors
        )
        path.write_text(
            text.replace(DEPENDENCY_HEADER + rows, "None.\n"), encoding="utf-8"
        )
        self.assertEqual(validate_bundle(epic.parent, True), ([], []))

    def test_dependency_producer_cannot_name_several_stories(self) -> None:
        rows = self.dependency_row(1, 2).replace(
            "| STORY-001-001 |", "| STORY-001-001 or STORY-001-002 |", 1
        )
        epic = self.create_dependent_epic(rows, published=True)
        for errors in (
            validate_epic(epic, None),
            validate_bundle(epic.parent, False)[0],
        ):
            self.assertTrue(
                any(
                    "producer must name a single story identifier" in e for e in errors
                ),
                errors,
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

    def set_timestamp(self, epic: Path, key: str, value: str) -> None:
        """Write stale_after or the EPIC's first sources[].last_modified."""
        path = epic / "epic.md"
        if key == "stale_after":
            anchor, replacement = "sources:\n", f"stale_after: {value}\nsources:\n"
        else:
            anchor = "    title: Example specification\n"
            replacement = f"{anchor}    {key}: {value}\n"
        text = path.read_text(encoding="utf-8").replace(anchor, replacement, 1)
        path.write_text(text, encoding="utf-8")

    def test_stale_after_is_optional(self) -> None:
        for value in (None, "", '""'):
            with self.subTest(value=value):
                epic = self.create_epic()
                if value is not None:
                    self.set_timestamp(epic, "stale_after", value)
                self.assertEqual(validate_epic(epic, None), [])
                self.assertEqual(validate_bundle(epic.parent, strict=True), ([], []))

    def test_okf_timestamps_accept_utc_offset_datetimes(self) -> None:
        for key in ("stale_after", "last_modified"):
            for value in ("2027-04-17T00:00:00Z", '"2027-04-17T09:30:00+02:00"'):
                with self.subTest(key=key, value=value):
                    epic = self.create_epic()
                    self.set_timestamp(epic, key, value)
                    self.assertEqual(validate_epic(epic, None), [])
                    self.assertEqual(
                        validate_bundle(epic.parent, strict=True), ([], [])
                    )

    def test_okf_timestamps_reject_malformed_values(self) -> None:
        for key in ("stale_after", "last_modified"):
            for value, message in (
                ("2027-04-17T00:00:00", "explicit UTC offset, such as"),
                ('"2027-04-17T25:00:00Z"', "not a real ISO 8601 datetime"),
                ('"2027-02-31"', "not a real calendar date"),
            ):
                with self.subTest(key=key, value=value):
                    epic = self.create_epic()
                    self.set_timestamp(epic, key, value)
                    errors = validate_epic(epic, None)
                    bundle_errors, _ = validate_bundle(epic.parent, strict=False)
                    for found in (errors, bundle_errors):
                        self.assertTrue(
                            any(key in error and message in error for error in found),
                            found,
                        )

    def test_date_only_timestamps_fail_epic_and_warn_bundle(self) -> None:
        for key in ("stale_after", "last_modified"):
            with self.subTest(key=key):
                epic = self.create_epic()
                self.set_timestamp(epic, key, "2027-04-17")
                expected = "'2027-04-17' is date-only"
                self.assertTrue(
                    any(expected in error for error in validate_epic(epic, None))
                )
                errors, warnings = validate_bundle(epic.parent, strict=False)
                self.assertEqual(errors, [])
                self.assertTrue(any(expected in warning for warning in warnings))
                self.assertTrue(
                    any("2027-04-17T00:00:00Z" in warning for warning in warnings)
                )
                strict_errors, _ = validate_bundle(epic.parent, strict=True)
                self.assertTrue(any(expected in error for error in strict_errors))

    def test_epic_template_omits_stale_after_and_uses_datetimes(self) -> None:
        epic_template = okf.read_document(
            PROJECT_ROOT / "assets" / "epic-concept-template.md"
        )
        self.assertFalse(epic_template.has("stale_after"))
        for source in okf.as_list(epic_template.get("sources")):
            self.assertEqual(source["last_modified"], "{{ISO_8601_UTC}}")

    def embed_collection(self, epic: Path, root: Path | None = None) -> Path:
        """Move the bundle root from docs/epics to an ancestor, docs/ by default."""
        collection = epic.parent
        root = root or collection.parent
        index = collection / "index.md"
        body = index.read_text(encoding="utf-8").split("---\n", 2)[2].lstrip()
        index.write_text(body, encoding="utf-8")
        self.write(
            root / "index.md",
            '---\nokf_version: "0.2"\n---\n\n# Documentation\n\n'
            f"- [EPICs]({collection.relative_to(root).as_posix()}/index.md) - Published EPICs.\n",
        )
        return root

    def test_embedded_collection_is_published_and_valid(self) -> None:
        epic = self.create_epic()
        self.embed_collection(epic)
        self.assertEqual(okf.infer_stage(epic), "published")
        self.assertEqual(validate_epic(epic, None), [])
        self.assertEqual(validate_bundle(epic.parent, strict=True), ([], []))

    def test_embedded_collection_keeps_epic_checks(self) -> None:
        epic = self.create_epic()
        self.embed_collection(epic)
        index = epic.parent / "index.md"
        index.write_text("# EPIC index\n", encoding="utf-8")
        (epic / "epic.md").unlink()
        errors, _ = validate_bundle(epic.parent, strict=False)
        self.assertIn(
            f"epics/index.md: {EPIC_DIRECTORY} is published but not listed", errors
        )
        self.assertIn(f"epics/{EPIC_DIRECTORY}: missing epic.md", errors)
        index.unlink()
        errors, _ = validate_bundle(epic.parent, strict=False)
        self.assertTrue(
            any("EPIC collection requires an index" in error for error in errors)
        )

    def test_embedded_collection_index_rejects_frontmatter(self) -> None:
        epic = self.create_epic()
        self.embed_collection(epic)
        index = epic.parent / "index.md"
        index.write_text(
            '---\nokf_version: "0.2"\n---\n\n' + index.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        errors, _ = validate_bundle(epic.parent, strict=False)
        self.assertTrue(
            any(
                error.startswith("index.md: ../index.md already declares okf_version")
                for error in errors
            ),
            errors,
        )
        errors, _ = validate_bundle(epic.parent.parent, strict=False)
        self.assertIn(
            "epics/index.md: only the bundle root index may carry frontmatter", errors
        )

    def test_bundle_root_reports_epics_outside_the_collection(self) -> None:
        epic = self.create_epic()
        root = self.embed_collection(epic)
        errors, _ = validate_bundle(root, strict=False)
        self.assertTrue(
            any(
                error.startswith(f"epics/{EPIC_DIRECTORY}: EPIC directory outside")
                for error in errors
            ),
            errors,
        )

    def test_working_epic_stays_working_under_a_repository_bundle_root(self) -> None:
        published = self.create_epic()
        self.embed_collection(published, root=self.root)
        working = self.create_epic(published=False)
        self.assertEqual(okf.infer_stage(published), "published")
        self.assertEqual(okf.infer_stage(working), "working")
        self.assertEqual(validate_epic(working, None), [])
        self.assertEqual(validate_epic(published, None), [])
        self.assertEqual(validate_bundle(published.parent, strict=True), ([], []))

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
