# Failure Taxonomy

## Locator

Symptoms: `NoSuchElementException`, empty element lists, selector works only on one viewport, element renamed or moved.

Next evidence: screenshot, HTML dump, selector search, product diff.

## Stale Element

Symptoms: `StaleElementReferenceException`, DOM rerender after locating.

Next evidence: rerender timing, framework lifecycle, page-object caching.

## Wait or Timing

Symptoms: `TimeoutException`, passes with sleep, fails under load, element present but not clickable.

Next evidence: loading indicators, network-backed result, explicit condition mismatch.

## Assertion Mismatch

Symptoms: Selenium steps succeed but expected text/state differs.

Next evidence: expected product behavior, recent app diff, test data state.

## Test Data

Symptoms: duplicate data, missing account/org/project, cleanup collision, shared environment contamination.

Next evidence: setup logs, API responses, database/test data records.

## Fixture Isolation

Symptoms: order-dependent failures, state leaks between tests, local parallelism fails while serial CI passes.

Next evidence: fixture scopes, browser/session reuse, xdist/parallel settings.

## Environment

Symptoms: browser/grid failures, driver mismatch, CI-only or local-only infrastructure issue.

Next evidence: browser version, driver version, grid logs, resource constraints.

## Product Regression

Symptoms: user-visible behavior changed and manual or lower-level tests confirm it.

Next evidence: recent app diff, manual reproduction, API response changes.

## Setup / Teardown

Symptoms: failure occurs before the test body starts or during cleanup; later tests inherit dirty state.

Next evidence: fixture/setup logs, teardown ownership, which resource was left behind.

## Cascade

Symptoms: many tests fail after one setup failure or serial suite stop.

Next evidence: first failure in chronological output.

## Flaky

Symptoms: intermittent reproduction under identical code and environment; passes on rerun.

Next evidence: rerun history, timing variance, parallelism settings — hand off to `flaky-detect`.

## Unknown

Symptoms: evidence insufficient for any category above.

Next evidence: whatever is missing from the Evidence Package (trace, screenshot, console, network) — collect before classifying.
