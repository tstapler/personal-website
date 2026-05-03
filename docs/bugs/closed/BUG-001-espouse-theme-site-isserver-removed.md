# BUG-001: espouse Theme Uses Removed `.Site.IsServer` API [SEVERITY: High]

**Status**: ✅ Closed
**Discovered**: 2026-04-18
**Resolved**: 2026-04-18
**Impact**: `hugo serve` fails to build the site entirely — no local development possible without the fix applied in-session.

## Problem Description

Three partials in the `espouse` theme call `.Site.IsServer`, which was removed from Hugo's template API in newer versions. Hugo now exposes this via `hugo.IsServer`. The error causes a hard build failure, not a warning, so the dev server exits immediately.

## Reproduction Steps

1. Clone the repo with submodules (`git clone --recurse-submodules`)
2. Run `hugo serve -D --baseURL http://localhost`
3. Expected: dev server starts at `http://localhost:1313`
4. Actual: build fails with `can't evaluate field IsServer in type page.Site`

## Root Cause

Hugo removed `.Site.IsServer` from the `page.Site` type. The replacement is the global `hugo.IsServer` function. The three affected partials in the `espouse` submodule were written against the old API and have not been updated upstream.

## Files Likely Affected

- `themes/espouse/layouts/partials/html_head.html:25` — `{{ if not .Site.IsServer }}`
- `themes/espouse/layouts/partials/javascript.html:12` — `{{ if not .Site.IsServer }}`
- `themes/espouse/layouts/partials/service-worker.html:2` — `{{- if not .Site.IsServer }}`

## Fix Approach

Replace all three occurrences of `.Site.IsServer` with `hugo.IsServer`. Already patched in the working tree during the 2026-04-18 session — the fix needs to be committed to the `espouse` submodule and the submodule reference updated in the parent repo.

## Verification

Run `hugo serve -D --baseURL http://localhost` — server should start and reach `Web Server is available at http://localhost:1313/` without errors.

## Related Tasks

None yet.
