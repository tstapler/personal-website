# Feature Plan: Cloudflare Pages Deployment

## Epic Overview

**User Value**
Migrating to Cloudflare Pages provides a global edge network for the personal website, significantly improving load times (TTFB) and reliability. It simplifies the deployment pipeline by removing the need for Kubernetes maintenance for static content, while enabling "Preview Deployments" for every Pull Request to visualize changes before merging.

**Success Metrics**
- **Performance**: TTFB < 50ms globally (p95).
- **Efficiency**: Deployment time < 3 minutes (currently ~5-10m with container build/push/pull).
- **Reliability**: 99.99% availability via Cloudflare Edge.
- **Quality**: 100% of PRs get an automatic preview URL.

**Scope**
- **Included**:
    - Integration of Cloudflare Pages deployment into GitHub Actions.
    - Utilization of existing Bazel `//:site_optimized` artifact.
    - Configuration of `wrangler.toml` for headers/routing.
    - Parallel operation with existing Kubernetes deployment during transition.
- **Excluded**:
    - Decommissioning of Kubernetes cluster (out of scope for this feature).
    - DNS migration (handled separately, though Cloudflare Pages provides a subdomain).

**Constraints**
- Must use the existing Bazel build system (`//:site_optimized`).
- Must not disrupt the current `ghcr.io` container workflow.
- Requires Cloudflare API Token and Account ID (to be added to GitHub Secrets).

## Architecture Decisions

### ADR 001: Direct Upload via GitHub Actions
- **Context**: Cloudflare Pages supports both "Git Integration" (Cloudflare builds the site) and "Direct Upload" (CI builds and uploads).
- **Decision**: Use **Direct Upload** via GitHub Actions.
- **Rationale**:
    - We already have a sophisticated Bazel build pipeline (`//:site_optimized`) that handles PurgeCSS, Critical CSS, and Gzip.
    - Replicating this build logic in Cloudflare's native build environment would be redundant and error-prone.
    - Keeps Bazel as the single source of truth for build artifacts.
- **Consequences**:
    - Requires managing Cloudflare credentials in GitHub Secrets.
    - We retain full control over the build environment.

### ADR 002: Artifact Extraction Strategy
- **Context**: `//:site_optimized` outputs a tarball (`site_optimized_dir.tar`), but Cloudflare Pages expects a directory.
- **Decision**: Extract the tarball in the CI pipeline before upload.
- **Rationale**:
    - Modifying the Bazel rule to output a directory tree is possible but can be messy with Bazel's hermeticity (TreeArtifacts).
    - Extracting a tarball is a trivial, fast operation in the CI runner.
- **Consequences**:
    - CI workflow needs an explicit extraction step (`tar -xf ...`).

## Story Breakdown

### Story 1: Deployment Configuration & Pipeline [1 week]
**User Value**: Enables the actual deployment capability, connecting the code to the cloud.
**Acceptance Criteria**:
- GitHub Actions workflow `cloudflare.yml` exists.
- Workflow successfully builds `//:site_optimized`.
- Workflow authenticates with Cloudflare and uploads the artifact.
- Deployments trigger on push to `master` (Production) and PRs (Preview).

### Story 2: Site Configuration & Verification [3 days]
**User Value**: Ensures the deployed site behaves correctly (caching, redirects, headers).
**Acceptance Criteria**:
- `wrangler.toml` is created with appropriate compatibility flags.
- Cache-Control headers are configured for static assets.
- Deployed site passes a "smoke test" (homepage loads, assets load).

## Atomic Task Decomposition

### Task 1.1: Create Cloudflare Workflow
- **Objective**: Implement the GitHub Actions workflow for Cloudflare Pages.
- **Context Boundary**:
    - Files: `.github/workflows/cloudflare.yml`
    - Concepts: GitHub Actions, Bazel, Cloudflare Pages Action.
- **Prerequisites**: Cloudflare API Token and Account ID available.
- **Implementation Approach**:
    1.  Define workflow triggers (push to master, pull_request).
    2.  Add `bazel build //:site_optimized` step.
    3.  Add `tar -xf` step to extract artifact to `./dist`.
    4.  Use `cloudflare/pages-action` to upload `./dist`.
- **Validation Strategy**:
    - Run workflow on a branch.
    - Verify "Success" status in GitHub Actions.
    - Verify a Preview URL is generated.
- **INVEST Check**: Independent, Valuable, Small (2h), Testable.

### Task 2.1: Configure Wrangler & Headers
- **Objective**: Define Cloudflare-specific configuration.
- **Context Boundary**:
    - Files: `wrangler.toml`, `content/_headers` (or handled in `wrangler.toml`).
    - Concepts: Cloudflare Pages Configuration, HTTP Headers.
- **Prerequisites**: Task 1.1 (to test the config).
- **Implementation Approach**:
    1.  Create `wrangler.toml` in root.
    2.  Define `pages_build_output_dir` (though CI overrides this, it's good documentation).
    3.  Configure `compatibility_date`.
    4.  (Optional) Add `_headers` file for custom caching rules if not using `wrangler.toml` headers (Pages supports `_headers` file in output dir).
- **Validation Strategy**:
    - Deploy and inspect HTTP response headers via `curl -I`.
- **INVEST Check**: Independent, Valuable, Micro (1h), Testable.

### Task 3.1: Documentation & Cleanup
- **Objective**: Update project documentation to reflect the new deployment method.
- **Context Boundary**:
    - Files: `README.md`, `ARCHITECTURE.md`.
    - Concepts: Documentation.
- **Prerequisites**: Task 1.1.
- **Implementation Approach**:
    1.  Update `README.md` with "Deployed on Cloudflare Pages" badge.
    2.  Update `ARCHITECTURE.md` to describe the dual deployment (K8s + Pages).
- **Validation Strategy**:
    - Review rendered Markdown.
- **INVEST Check**: Independent, Valuable, Micro (1h), Testable.

## Known Issues

### 🐛 Configuration Risk: Missing Secrets [SEVERITY: High]
- **Description**: Workflow will fail if `CLOUDFLARE_API_TOKEN` or `CLOUDFLARE_ACCOUNT_ID` are missing from GitHub Secrets.
- **Mitigation**:
    - Add a check in the workflow or documentation to ensure secrets are present.
    - **Action**: User must manually add secrets to GitHub repo.

### 🐛 Build Risk: Large Artifact Size [SEVERITY: Low]
- **Description**: If the site grows significantly, the tarball upload might slow down.
- **Mitigation**:
    - `//:site_optimized` already uses PurgeCSS and Gzip.
    - Cloudflare Pages has a 25MB limit per file (we are well under) and 20,000 files limit.
- **Prevention**: Monitor build size.

## Dependency Visualization

```
[Start]
   |
   +---> [Task 1.1: Create Cloudflare Workflow]
   |       |
   |       +---> [Task 2.1: Configure Wrangler]
   |
   +---> [Task 3.1: Documentation]
```

## Integration Checkpoints
- **After Task 1.1**: A PR should trigger a build and produce a Cloudflare Preview URL.
- **After Task 2.1**: The Preview URL should serve assets with correct headers.
- **Final**: Merge to `master` triggers Production deployment.

## Context Preparation Guide
- **Task 1.1**:
    - Load `.github/workflows/main.yml` (reference).
    - Load `BUILD.bazel` (reference target names).
- **Task 2.1**:
    - Research `wrangler.toml` schema for Pages.

## Success Criteria
- [ ] `cloudflare.yml` workflow passes.
- [ ] Preview URL generated for PRs.
- [ ] Production URL updates on merge to master.
- [ ] Site loads correctly (CSS/JS working).
