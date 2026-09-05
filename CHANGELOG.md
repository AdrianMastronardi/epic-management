# Changelog

All notable changes to this project are documented in this file.

The format is loosely adapted from [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Entries are grouped by area, in this fixed order. Sections with no entries for a given version are omitted.

- **Skill** covers the agent-facing workflow and invocation interface: `SKILL.md`, `agents/openai.yaml`, and `references/`.
- **Templates** covers files under `assets/` that the skill turns into repository artifacts.
- **Validation** covers deterministic checks under `scripts/`.
- **Documentation** covers human-facing project documentation, including this changelog.
- **Infrastructure** covers formatting rules, editor configuration, and repository plumbing.

Within each section, entries are sorted in case-insensitive alphabetical order by filename.

## [0.2.0] - 2026-08-20

Adopts [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) as the storage format for EPIC knowledge. Published EPICs now live in a conformant knowledge bundle rooted at `docs/epics/`, where one EPIC is one concept directory holding an `epic.md` concept, one `Story` concept per story, and an index. Frontmatter records provenance with `sources`, authorship with `generated`, review with `verified`, document lifecycle with `status`, and execution lifecycle with `epic_status`, so the checkpoint approval this skill already required becomes a recorded human verification event rather than an untracked one.

This release changes artifact paths and adds the `migrate` operation, which converts a legacy `docs/epic-index.md` and flat `docs/epics/EPIC-NNN-name.md` layout into the bundle after an exact-write preview and without touching GitHub. Story concepts link their specification blocks instead of duplicating them, while generated GitHub issue bodies still embed the complete applicable text.

### Skill

- `agents/openai.yaml`: advertises the new `migrate` operation.
- `references/github-publication.md`: publishes into the bundle, assigns the frontmatter that publication owns, updates the bundle index, resolves story block links into complete issue text, and requires both validators before commit.
- `references/okf-bundle.md`: defines the OKF format contract for EPIC artifacts, including bundle layout, concept types, frontmatter families, the actor convention, trust events, source and link policy, the restricted YAML style, index structure, history through git rather than a log file, conformance, and the legacy migration map.
- `SKILL.md`: replaces the single-document artifact model with the OKF concept directory, adds the `migrate` operation and mode, records `generated` and `verified` at the moments they actually occur, separates `status` from `epic_status`, moves per-EPIC metadata out of the index and into the concept, leaves history to git instead of a bundle log, and requires bundle validation before publication completes.

### Templates

- `assets/backlog-concept-template.md`: replaces `assets/epic-backlog-template.md` with an `EPIC Backlog` concept carrying OKF frontmatter.
- `assets/bundle-index-template.md`: provides the bundle-root index, declaring `okf_version` and grouping published EPICs by execution status without linking optional concepts that have not been created.
- `assets/epic-backlog-template.md`: removed in favor of `assets/backlog-concept-template.md`.
- `assets/epic-concept-template.md`: replaces `assets/epic-template.md` with a working `type: EPIC` concept whose title, provenance, lifecycle, and story index live in frontmatter and whose body holds the specification blocks and distribution table; publication-owned resource and human-verification fields remain absent until publication.
- `assets/epic-index-template.md`: becomes the per-EPIC directory index listing the EPIC concept and its story concepts.
- `assets/epic-template.md`: removed in favor of `assets/epic-concept-template.md`.
- `assets/story-concept-template.md`: provides a working `type: Story` concept with `applicable_blocks` frontmatter and an applicable specification section that links its blocks in the EPIC concept, leaving publication-owned resource and human-verification fields absent until publication.

### Validation

- `scripts/okf.py`: adds shared OKF frontmatter parsing and checks, using PyYAML when importable and a strict parser for the documented subset otherwise, keeping both parsers aligned on quoted leading-zero identifiers, and providing reusable actor, calendar date, trust, lifecycle, source, footnote, and hygiene validation.
- `scripts/validate_epic.py`: validates an EPIC concept directory rather than a single file, checking frontmatter families, lifecycle values against the working or published stage, bounded story concept paths, story metadata and resources against the EPIC index, exact specification-link agreement, story numbering and file presence, the directory index, footnote attribution, link targets, and completion requirements.
- `scripts/validate_okf_bundle.py`: adds OKF v0.2 conformance validation for the whole bundle, accepting normalized relative root links, separating hard failures from the tolerances OKF grants consumers, checking any independently maintained `log.md` it finds without requiring one, and offering `--strict`.
- `tests/test_validators.py`: covers valid working and published bundles with PyYAML and the fallback parser plus regressions for concept containment, metadata projection, parser parity, real dates, optional index links, and normalized root links.

### Documentation

- `CHANGELOG.md`: documents the OKF adoption release.
- `CONTRIBUTING.md`: restates the project invariants around the bundle, conformance, evidence-based provenance, the two lifecycle axes, and lossless migration, and requires exercising both validators with and without PyYAML.
- `README.md`: documents the bundle model, the `migrate` operation, the recorded provenance and trust guarantees, git as the bundle's history, both validation commands, and the new package structure.

### Infrastructure

- `.gitignore`: keeps the bytecode cache produced by the shared validator module out of version control.

## [0.1.1] - 2026-08-16

### Skill

- `references/github-publication.md`: requires a new publication to start from the approved working EPIC under `tmp/`, defines native GitHub relationships, and records the separated index and backlog requirements for active and completed EPICs.
- `SKILL.md`: defines the lifecycle boundary, separates published index and future backlog state, requires direct document and story links, controls lifecycle statuses, and bounds completed-EPIC summaries.

### Templates

- `assets/epic-backlog-template.md`: provides an optional separate home for future EPICs without published documents or GitHub issues.
- `assets/epic-index-template.md`: provides a generic published EPIC index with relative document links, controlled status, structured story links, exceptional notes, and bounded completion summaries.

### Validation

- `scripts/validate_epic.py`: makes draft-labelling diagnostics apply accurately to both working and versioned EPIC documents.

### Documentation

- `CONTRIBUTING.md`: adds the temporary-to-versioned publication boundary, index/backlog separation, and complete index-entry requirements to the project invariants.
- `README.md`: documents the artifact lifecycle, index/backlog separation, native GitHub relationships, and active and completed index states.

## [0.1.0] - 2026-08-15

Initial release of Epic Management, a cross-host skill for Codex and Claude Code that transforms a functional and technical specification into one self-contained, versioned EPIC document and a traceable set of GitHub issues without losing source information.

The EPIC document divides the complete specification into stable `SPEC-NNN-SSS` blocks, classifies each block as `context` or `operational`, and maps every operational block to the EPIC issue, one or more story issues, or both. Generated issue bodies include the complete applicable text rather than only summaries, identifiers, or links, so no implementation depends on an ignored temporary file.

The skill provides `help`, `prepare`, `refine`, `publish`, `prepare-and-publish`, `resume`, and `inspect`. Empty invocations show English help without reading the repository or changing state. Publication requires an exact preview and explicit approval, reuses resources by deterministic identity, resumes partial runs without duplication, and leaves documentation pull requests open for human review.

### Skill

- `agents/openai.yaml`: defines Codex discovery metadata, an operation-focused description, and a default prompt that opens the help interface.
- `references/github-publication.md`: defines the approval-gated publication protocol, including repository preconditions, lossless issue-body generation, all-state duplicate detection, exact-write previews, resource-by-resource readback, repository archival, pull-request creation, and post-merge cleanup.
- `SKILL.md`: defines the dual-host invocation contract, explicit operation dispatch, portable resource resolution, single-document invariant, lossless source consumption, block classification and routing, coverage checkpoint, idempotent publication and resumption, formatting requirements, and completion conditions. It prevents remote mutations before approval, temporary-path dependencies, draft-labelled EPIC artifacts, and story implementation during backlog management.

### Templates

- `assets/epic-template.md`: provides the canonical English EPIC structure with functional and technical specification blocks, affected components, dependencies, execution order, global acceptance criteria, a GitHub distribution table, and executable story sections with exact `Applicable blocks` declarations.

### Validation

- `scripts/validate_epic.py`: validates the EPIC title and number, required section order, consecutive and unique specification and story identifiers, distribution-table coverage, contextual and operational routing, story-to-table agreement, required story subsections, unresolved placeholders, forbidden `tmp/` references, and accidental draft labelling.

### Documentation

- `CHANGELOG.md`: documents the complete initial release using fixed, consistently ordered release areas.
- `CONTRIBUTING.md`: defines contribution scope, project invariants, English-language and Markdown requirements, validation and compatibility checks, changelog expectations, and licensing terms.
- `LICENSE`: licenses the project under the MIT License with copyright held by Adrian Mastronardi.
- `README.md`: documents the problem, guarantees, operations, dual-host installation and usage, end-to-end workflow, EPIC document model, validation commands, package structure, license, and contribution entry point.

### Infrastructure

- `.gitattributes`: normalizes supported text formats to LF line endings.
- `.markdownlint-cli2.jsonc`: configures structural Markdown rules while preserving logical prose lines and manually maintained table diffs.
- `.vscode/extensions.json`: recommends the Markdownlint and Prettier editor integrations.
- `.vscode/settings.json`: enables Markdown formatting and lint fixes on save, preserves logical prose lines, normalizes final newlines, and trims trailing whitespace.
