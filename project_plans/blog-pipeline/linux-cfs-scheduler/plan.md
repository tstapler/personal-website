# Plan: Understanding Linux CFS Scheduling and Kubernetes Latency

**Source**: ~/Documents/personal-wiki/logseq/pages/Linux CFS Scheduler.md
**Target audience**: Platform/backend engineers running services on Kubernetes who see mysterious latency with low CPU utilization
**Tone**: Investigative — start with a symptom that confused you, work through the misconception, reveal the real mechanism
**Estimated length**: 900–1200 words

---

## Post Structure

### H2: The Symptom Nobody Expects
- CPU utilization looks fine (20–30%), but service latency is high and inconsistent
- Leads you to check everything except the scheduler
- Set up: "I assumed CFS was deprioritizing my I/O-bound service. I was wrong."

### H2: What CFS Actually Does (The Misconception)
- Brief, accessible explanation of vruntime — the "fairness" accounting
- CFS actually **favors** tasks waking from I/O sleep: they have low accumulated vruntime, so they're scheduled sooner
- This is the opposite of the common assumption
- Source: Linux kernel docs + Knowledge Synthesis 2026-02-18 verification

### H2: The Real Culprit: Run Queue Depth
- When many threads become runnable simultaneously, the scheduling **period** extends
- Default: `sched_min_granularity_ns` = 0.75ms × 100 runnable tasks = 75ms scheduling period
- An I/O-bound task waking up may wait the full period before getting a timeslice
- **The compounding problem**: a request touching 5–10 services each adding 25–75ms = 125–750ms of pure scheduler wait

### H2: Kubernetes Makes This Worse
- `cpu.shares` and CPU requests: a pod requesting 200m gets `cpu.shares = 204`; requesting 2000m gets 2048
- Under contention, low-request pods get proportionally less CPU — not because they're I/O-bound, but because they asked for less
- CPU throttling via `cfs_quota_us`: quota exhausted → hard throttle until next 100ms period
- Right-sizing CPU requests is critical; under-requesting is a latency trap

### H2: EEVDF — What Changed in Kernel 6.6
- CFS replaced by EEVDF (Earliest Eligible Virtual Deadline First) in October 2023
- Better explicit latency handling, virtual deadlines for latency-sensitive tasks
- `sched_setattr()` for per-task latency hints
- Core mechanisms (shares, bandwidth control, cgroup integration) unchanged — this analysis still applies

### H2: What to Actually Tune and Watch
- Monitor: CPU Pressure (PSI), scheduler latency, context switches, thread density
- Tune: reduce thread count, use async I/O, avoid thread-per-request models
- Kubernetes: set CPU requests accurately, consider CPU affinity for latency-critical pods

---

## Key Points to Nail
- The "CFS deprioritizes I/O-bound tasks" myth is confidently wrong and widespread — this is the hook
- The math example (100 tasks × 0.75ms = 75ms period) makes the mechanism concrete
- The compounding across hops is the "oh that explains it" moment
- Don't oversell tuning — monitor first, tune only if PSI/scheduler latency is visible

## Research Gaps
- None: source wiki page is comprehensive with references
- Optional addition: a real Datadog or Grafana screenshot showing the pattern (if available)
