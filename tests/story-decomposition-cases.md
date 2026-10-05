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
