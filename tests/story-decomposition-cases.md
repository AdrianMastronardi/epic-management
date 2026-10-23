# Story decomposition evaluation inputs

These are synthetic planning cases. Apply the skill's decomposition and handoff guidance to each case independently. Treat the supplied repository facts as fixture evidence; do not invent files or inspect a real product repository. Propose the story boundaries, required outputs and release conditions, an executable event sequence or unresolved blocker, candidate concurrent work, and a publication preview distinguishing native dependency edges from conditions in issue bodies. Preserve the difference between proposals and approved decisions. Do not implement stories, contact GitHub, or simulate human approval. Work only from this file and the supplied skill instructions; do not read any other file under `tests/`. Keep any evaluation artifacts in an isolated temporary directory.

## Case 1: Shared parser contract

A source specification requests two import adapters for different formats. The repository has separate adapter modules and test suites, but no shared normalized record type. Each adapter needs that type and compatibility fixtures before meaningful implementation can start. The record shape is already agreed in the source. Publishing the type and passing fixtures on the base branch is a small, independently verifiable delivery with no other work needed to complete it. Neither adapter needs the other's implementation. Each adapter must pass the shared fixtures and its own format tests.

## Case 2: Provider and consumer acceptance

An approved schema and compatible provider double already exist on the base branch. A provider story implements the real service, and a consumer story builds a UI in a separate module. Both can start and merge independently against the schema. The consumer's final acceptance must exercise the real provider, including its failure responses. The provider's acceptance can finish without the UI. No additional contract implementation is required.

## Case 3: Schema, client, and integration

The source assigns A ownership of a schema and its integration into an existing service, and B ownership of a generated client. A can publish a usable, validated schema without B. B can then generate and validate the client from that schema. A needs B's client only for its final integration. The source explains that a separate schema issue would add review overhead without advancing availability; it asks to retain A's scope if that scope is executable. Neither artifact exists initially.

## Case 4: Small cohesive change

The requested change adds one optional display field to an existing response and renders it in an existing component. The data path, rendering, and regression assertion are a small cohesive change reviewed together. There are no consumers waiting for an intermediate artifact, no independent work to unlock, and no external prerequisites.

## Case 5: Mutually unavailable outputs

A produces a schema that, under the supplied design, must be generated from B's completed client metadata. B generates that client metadata only from A's published schema. Neither output exists, and there is no bootstrap schema, fallback metadata, or approved design change. The source does not establish an order in which either output can be produced.

## Case 6: Resuming publication after delivery

An approved plan says B cannot start until A completes a validated adapter contract. A's entire deliverable is that contract and its passing fixtures. Publication started and both issues exist, but the native dependency edge has not yet been created. On resume, A's contract is merged, the required checks pass, and A is closed as completed. B has not started. Plan the remaining dependency actions without changing the durable prerequisite definition. Also explain how the result changes if the only observation is that A was closed as not planned, with no delivery evidence.

Consider three further variants independently, with A closed as completed and a linked merged pull request: the contract was merged into a release branch while B targets `main`, where the contract is absent; the contract is on B's base branch but a required compatibility check fails; or the contract's merge was reverted on B's base branch. Describe the remaining actions in each variant.

## Case 7: Two columns on one table

A source specification asks for a gift-message field and a delivery-window field on orders. Each field has its own form, API attribute, and tests, and neither feature reads the other's data. Repository facts: both fields are new columns on the `orders` table; migrations live in one directory as sequentially numbered files and the pipeline rejects a duplicate number; both attributes are added to the same `OrderSerializer` class; the end-to-end suite runs against a single staging database that accepts one run at a time.

## Case 8: Vendor credentials and demo order

The source describes a webhook handler for a payment vendor and a monthly revenue report. The repository's secrets documentation lists a vendor sandbox key that supports every handler code path and the automated tests. The vendor issues production credentials only after its own review, which has no date, and the handler's sign-off requires one live transaction. The report reads an existing ledger table that the handler never writes. The product owner's notes say they would rather see the handler finished before the report because the demo flows better that way.

## Case 9: Export job between two teams' work

The source defines three stories. The first reshapes the billing data model and ships as one migration with its updated repository layer; nothing from it is usable until that change is merged. The second builds an export job written directly against the reshaped model. The third replaces a permissions stub with a real permissions service behind an interface that already exists on the base branch, with a working stub implementation. The export job calls that interface and its sign-off includes a run with real permission denials. The first and third stories do not touch each other's modules.

## Case 10: Resuming an older publication

A published EPIC's `Dependencies` section says only “STORY-003 depends on STORY-002”, with no further detail, and GitHub shows STORY-003 blocked by STORY-002. The same EPIC's approved plan states that STORY-004 cannot start until STORY-001 delivers a merged configuration loader, which is STORY-001's entire deliverable; that edge was never created. On resume, STORY-001 is closed as completed, has no linked pull request, and the loader module is not on the base branch. STORY-004 has not started. Plan the remaining dependency actions.

## Case 11: A return gate outside the table

A creates a reusable encoder and B builds a downstream export adapter. The dependency table contains only B's native start dependency on A's merged encoder. A's tasks also include final acceptance against B's real adapter before A can close. A can publish the encoder before that acceptance. Both issue bodies include those tasks, and a publication request is pending. No remote resources exist yet.

## Case 12: Documented delivery conditions

A emits a validated schema and later integrates a generated SDK. B generates that SDK from A's schema. The table records B's schema start gate as documented because the schema becomes available before A closes, and A's SDK integration gate as documented because A can start without the SDK. There are no native blockers. Neither output exists. The source asks for a publication preview.

## Case 13: Three services

A delivers a protocol definition that B needs to start; nothing from A is usable until it merges. B delivers a compatibility library that C requires for integration. C supplies a signed fixture that A's acceptance criteria require before A closes. A can publish its protocol before completing acceptance. The table represents B's start condition as native and the other two conditions as documented. All three outputs are missing.

## Case 14: Partial publication with existing identities

Publication began for EPIC-014. STORY-014-001 owns both a schema and its final integration; STORY-014-002 generates a client from that schema. Their GitHub issues already exist, both are open and parented to EPIC-014, and no documentation branch or PR exists yet. The approved table says STORY-014-002 needs STORY-014-001's schema before starting, and STORY-014-001 needs STORY-014-002's real client before integration. Both conditions are documented. No output is delivered. The user asks to resume the previously approved publication without duplicate issues.

## Case 15: A prerequisite in another EPIC

EPIC-015's issue A requires a parser from EPIC-016's issue B before final acceptance. B's published body says that its parser verification requires A's real import command. A can implement that command early. The local EPIC table names B's issue URL as an external documented completion prerequisite. Consider both the supplied readable-body evidence and a variant where B's body and dependency list cannot be read. The user asks to publish A's plan.

## Case 16: Older prose-only plan

A legacy EPIC has no dependency table. Its prose says that A needs B's output for integration and B needs A's output to start, with both outputs available before their producers close. Existing open issues match that prose and have no native blockers. The local structural validators pass. The user first asks for inspection, then asks to resume by updating the issue bodies and adding any missing dependency relationships. No normalization or new design has been approved.

## Case 17: Source insists on retaining scope

The source requires A to own a schema and final client integration, B to generate the client from A's schema, and each issue to retain its entire stated scope. It explicitly refuses a separate schema or integration issue. A can publish its schema early, and B can deliver the client before A integrates it. Neither artifact exists. The user asks to prepare a publishable plan from this source.

## Case 18: Navigation without execution gates

Two independent stories add optional display fields to separate response types. Neither needs the other's code, output, tests, or acceptance. Both bodies link to the other story under “Related work”, and both are direct children of the same EPIC. The source prefers showing the first field before the second in a demo. There are no execution prerequisites.
