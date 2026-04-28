# Blog Post Pipeline

Track post ideas from wiki candidate → published.

**Stages**: 💡 Candidate | 📋 Outlined | ✍️ Drafting | 👀 Review | ✅ Published

---

## The Knowledge, Applied: Build the LLM Tools That Build Better Tools

**Stage**: 👀 Review
**Source**: Conversation-derived — Playwright correction loop origin story + dotfiles toolchain
**Hook**: You don't start by building the best LLM toolchain. You start by building the tools that let you build it — and the compounding is what makes the difference after six months.
**Effort**: Low
**Draft**: content/blog/llm-tooling-bootstrap/index.md
**Added**: 2026-04-26

---

## Manifest-Driven Development: My AI Workflow After a Year of Getting It Wrong

**Stage**: ✍️ Drafting
**Source**: ~/Documents/personal-wiki/logseq/pages/Manifest-Driven Development.md
**Hook**: Every AI session starts from scratch — here's the structured workflow I built to stop losing context, polluting implementations with planning noise, and re-explaining my codebase every morning.
**Effort**: Medium
**Draft**: content/blog/manifest-driven-development/index.md
**Added**: 2026-04-18

---

## Zero-Downtime Deployments with PgBouncer: Graceful Shutdown, Spring Boot, and the Gap Nobody Documents

**Stage**: 👀 Review
**Source**: ~/Documents/personal-wiki/logseq/pages/PGBouncer Signal Handling.md + Kubernetes Zero Downtime Deployment.md + Kubernetes Endpoint Deregistration.md
**Hook**: Getting truly zero-downtime Postgres deployments requires PgBouncer graceful shutdown, Spring Boot connection drain, and Kubernetes endpoint deregistration to all coordinate — and the official docs for each only cover that layer in isolation.
**Effort**: Medium
**Plan**: project_plans/blog-pipeline/pgbouncer-zero-downtime/plan.md
**Draft**: content/blog/pgbouncer-zero-downtime/index.md
**Added**: 2026-04-18

---

## STRONG CANDIDATES

---

## Understanding Linux CFS Scheduling: Why Your Kubernetes Services Feel Sluggish

**Stage**: 📋 Outlined
**Source**: ~/Documents/personal-wiki/logseq/pages/Linux CFS Scheduler.md
**Hook**: Debunks the myth that CFS deprioritizes I/O-bound services — the real culprit is scheduling period length and run queue depth, and it explains mysterious Kubernetes latency spikes.
**Effort**: Low
**Plan**: project_plans/blog-pipeline/linux-cfs-scheduler/plan.md
**Added**: 2026-04-18

---

## Lazy-Loading Container Images with Stargz: Cut Your Cold Start Time in Half

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/pages/Stargz.md
**Hook**: Seekable compression lets containers start before the full image downloads — 2-5x cold start improvements with minimal operational overhead.
**Effort**: Low
**Added**: 2026-04-18

---

## Spring Boot Container Startup: AOT, GraalVM, and Project CraC Compared

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/pages/GitHub Actions Integration for Container Startup Optimization.md
**Hook**: Four paths to faster Spring Boot container startup with honest effort/risk assessments and Helm modification examples for each.
**Effort**: Low
**Added**: 2026-04-18

---

## Managing LLM Context Windows: From Token Economics to Infinite Context

**Stage**: 📋 Outlined
**Source**: ~/Documents/personal-wiki/logseq/pages/Context Window Management.md
**Hook**: Context windows are the critical bottleneck in LLM applications — a comparison of six management strategies with concrete tradeoffs and selection criteria.
**Effort**: Low
**Plan**: project_plans/blog-pipeline/llm-context-windows/plan.md
**Added**: 2026-04-18

---

## The Function Coloring Problem: Why Async/Await Isn't the Holy Grail

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/pages/Colored Concurrency.md
**Hook**: JavaScript, Python, and Kotlin all struggle with sync/async incompatibility while Go sidesteps it entirely — here's why, with a real Spring Framework bug and performance numbers.
**Effort**: Low
**Added**: 2026-04-18

---

## Local-First Architecture: Building Apps That Work Offline and Sync Seamlessly

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/pages/Local-First Software.md
**Hook**: Local-first is a paradigm shift for personal productivity tools — CRDTs make offline collaboration possible without sacrificing sync, and the trade-offs are finally mature enough to ship.
**Effort**: Low
**Added**: 2026-04-18

---

## Measuring Developer Velocity: PR Throughput as a Leading Indicator

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/pages/PR Throughput.md
**Hook**: PR throughput (merged PRs/eng/week) became the standard velocity metric — and AI tools are already shifting the benchmarks to 9.2 for early adopters vs 4.8 baseline.
**Effort**: Low
**Added**: 2026-04-18

---

## Migrating to Ceph Bluestore: A Step-by-Step Guide to a Modern Storage Backend

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/journals/2022_02_26.md, 2022_03_13.md
**Hook**: A complete Ceph Bluestore migration with custom tooling — what to expect, where it gets tricky, and the performance implications nobody warns you about.
**Effort**: Medium
**Added**: 2026-04-18

---

## Debugging DNS Resolution in Kubernetes: When ndots Configuration Causes Silent Failures

**Stage**: 📋 Outlined
**Source**: ~/Documents/personal-wiki/logseq/journals/2022_05_03.md
**Hook**: DNS caching in Java plus misconfigured Kubernetes search domains caused hours of investigation — the fix was a single ndots setting that almost nobody knows to check.
**Effort**: Medium
**Plan**: project_plans/blog-pipeline/kubernetes-dns-ndots/plan.md
**Note**: ⚠️ Needs personal story details filled in before drafting — see plan.md
**Added**: 2026-04-18

---

## Optimize S3 Transfer Speeds: Tuning AWS CLI Concurrency for Your Homelab

**Stage**: 📋 Outlined
**Source**: ~/Documents/personal-wiki/logseq/journals/2024_01_25.md
**Hook**: Simple concurrency tuning can dramatically speed up S3 transfers — here's how to find the sweet spot without overwhelming your infrastructure.
**Effort**: Low
**Plan**: project_plans/blog-pipeline/s3-transfer-tuning/plan.md
**Note**: ⚠️ Needs actual benchmark numbers before drafting — see plan.md
**Added**: 2026-04-18

---

## Finding Your Database Bottleneck: Using PGHero and SQL Diffs for Postgres Analysis

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/journals/2024_01_25.md
**Hook**: Most people don't know which queries and tables actually get hit — PGHero and sqlglot make it dead simple to find and fix the inefficiencies that actually matter.
**Effort**: Medium
**Added**: 2026-04-18

---

## Upgrading PostgreSQL Without Pain: Managing Replication Slots During Major Version Upgrades

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/journals/2024_04_20.md
**Hook**: Replication slots are the hidden obstacle in Postgres major-version upgrades — understanding why they must be dropped first saves you a midnight rollback.
**Effort**: Low
**Added**: 2026-04-18

---

## MODERATE CANDIDATES

---

## The AI Coding Tools Productivity Paradox: When 56% Faster Means Less Reliable

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/pages/AI Coding Tool Productivity.md
**Hook**: MIT shows 56% speed gains, METR 2025 shows experienced developers 19% slower — the productivity evidence for AI coding tools is genuinely contradictory and worth unpacking.
**Effort**: Medium
**Added**: 2026-04-18

---

## Service Mesh Architecture: When Sidecar Proxies Make Sense (and When They Don't)

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/pages/Service Mesh.md
**Hook**: Istio, Linkerd, and Consul each solve mTLS and distributed tracing differently — here's when the operational complexity is actually worth it.
**Effort**: Medium
**Added**: 2026-04-18

---

## gRPC Performance Tuning: Why Default Thread Pools Destroy Your Latency

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/pages/gRPC Java Executors.md
**Hook**: gRPC-Java's default CachedThreadPool creates latency disasters under load — here's how to properly size executors and why the defaults exist at all.
**Effort**: Medium
**Added**: 2026-04-18

---

## High-Performance AWS Networking: Avoiding TCP Window Scaling Bottlenecks at Scale

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/pages/AWS Network Performance Optimization.md
**Hook**: ENA Express, TCP window scaling, and MTU tuning are often ignored until they become the ceiling — a practical guide to finding your actual network bottleneck on AWS.
**Effort**: Medium
**Added**: 2026-04-18

---

## Java Virtual Threads at Scale: When Your Profiler Becomes the Bottleneck

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/pages/Java Virtual Threads Performance Profiling.md
**Hook**: Traditional profilers can cause 30-50% performance degradation when used with virtual threads — here's what changes and how to monitor without hurting yourself.
**Effort**: Medium
**Added**: 2026-04-18

---

## Building Autonomous AI Agents with Claude Code: Architecture and Implementation Patterns

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/pages/Claude Code Sub-Agents.md
**Hook**: Sub-agents in Claude Code give each task its own context window — here's the architecture, when to use it, and patterns for building reliable multi-agent workflows.
**Effort**: Medium
**Added**: 2026-04-18

---

## From SLIs to Error Budgets: Building Reliable Services That Ship Fast

**Stage**: 💡 Candidate
**Source**: ~/Documents/personal-wiki/logseq/pages/Service Quality.md
**Hook**: Error budgets turn reliability vs. deployment velocity from a political argument into a math problem — here's how to set them up so they actually change behavior.
**Effort**: Medium
**Added**: 2026-04-18
