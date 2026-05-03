# Plan: Zero-Downtime Deployments with PgBouncer and Spring Boot

**Sources**:
- ~/Documents/personal-wiki/logseq/pages/PGBouncer Signal Handling.md
- ~/Documents/personal-wiki/logseq/pages/Kubernetes Zero Downtime Deployment.md
- ~/Documents/personal-wiki/logseq/pages/Kubernetes Endpoint Deregistration.md
- ~/Documents/personal-wiki/logseq/pages/PGBouncer.md
- ~/Documents/personal-wiki/logseq/pages/Graceful Shutdown.md

**Target audience**: Backend engineers running Spring Boot services backed by Postgres on Kubernetes who still see connection errors during rolling deploys after "doing all the right things"

**Tone**: Debugging story that builds to a complete working recipe — explain each layer, show why any single layer isn't enough, deliver the combined solution

**Estimated length**: 1200–1600 words

---

## The Central Insight (Build the Post Around This)

Zero-downtime Postgres deployments require **three independent systems** to drain in the right order:

```
1. Kubernetes stops routing NEW traffic to the pod       (5–15s, async/best-effort)
2. PgBouncer drains client connections and DB pool       (10–60s, depends on pool mode)
3. Spring Boot finishes in-flight requests and closes    (5–30s, depends on query duration)
```

Each layer has its own docs. Nobody documents how they interlock. A misconfigured `preStop` hook at any layer causes dropped connections or connection errors during deploys.

---

## Post Structure

### H2: The Symptom
- Rolling deploy triggers 5xx errors or `Connection refused` / `connection pool exhausted` errors
- Happens even with `terminationGracePeriodSeconds` set and readiness probes configured
- The errors look random — some deploys are clean, some aren't
- Personal hook: frame this as something you investigated on-call or discovered when setting up Kubernetes for the first time properly

### H2: Why "Just Add a preStop Sleep" Isn't Enough

Walk through why the naive fix fails:

**The endpoint deregistration race**: When Kubernetes terminates a pod, three things happen *in parallel* — kubelet starts shutdown, kube-proxy updates iptables rules, and the endpoints controller removes the pod from the Service. The shutdown starts immediately; the traffic cut happens asynchronously (typically 5–15s). A `sleep 5` preStop hook on the app alone doesn't fix this — during those 5 seconds, traffic is still arriving at a pod that's already shutting down.

**The PgBouncer signal confusion**: Most people assume SIGTERM = graceful shutdown for any process. For PgBouncer < 1.23.0, SIGTERM meant *immediate exit*. For PgBouncer ≥ 1.23.0, SIGTERM now waits for all clients to disconnect (a "super safe" shutdown) — which in session mode can mean waiting *minutes*. The old graceful behavior was SIGINT, and immediate exit moved to SIGQUIT. If you upgraded PgBouncer without updating your preStop hook, you silently changed behavior.

### H2: The Three Layers You Need to Get Right

#### Layer 1 — Kubernetes Endpoint Deregistration
- Kubernetes is a distributed system; endpoint updates propagate asynchronously
- The formula: `preStop_delay ≥ endpoint_propagation (5s) + (readinessProbe.periodSeconds × failureThreshold) + buffer (2–5s)`
- Standard config: `5 + (2 × 3) + 2 = 13s`
- This delay goes on the *application* container's preStop hook, not just PgBouncer
- Show the YAML:
```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 13"]
readinessProbe:
  httpGet:
    path: /actuator/health
    port: 8080
  periodSeconds: 2
  failureThreshold: 3
```

#### Layer 2 — PgBouncer Graceful Shutdown
- Explain the SIGTERM vs SIGINT distinction and the 1.23.0 breaking change
- Show the two strategies and when to pick each:

| Signal | Priority | Use when |
|---|---|---|
| SIGTERM (1.23.0+) | App availability | DB has connection headroom; short-lived app connections |
| SIGINT | DB stability | Connection limits are tight; session lifetimes are unpredictable |

- The preStop formula for PgBouncer (transaction mode):
```bash
sleep 5                    # endpoint deregistration propagation
killall -TERM pgbouncer    # or -INT depending on strategy
sleep 45                   # max_transaction_duration + readiness probe window + buffer
```
- Full formula: `5s + max_transaction_duration + (readinessProbe.periodSeconds × 2) + buffer`
- Show complete YAML for transaction mode (the common case)

#### Layer 3 — Spring Boot Connection Drain
- Spring Boot needs `server.shutdown=graceful` in `application.properties` (Spring Boot 2.3+)
- Without it, SIGTERM triggers immediate context close — active DB queries get killed mid-flight
- `spring.lifecycle.timeout-per-shutdown-phase` controls how long to wait for in-flight requests
- The connection pool (HikariCP) closes separately — `spring.datasource.hikari.connection-timeout` and `minimumIdle` affect how quickly idle connections release
- Java ShutdownHook fires on SIGTERM, but only if PID 1 receives the signal — needs `exec` form in Dockerfile CMD or a proper init process (tini/dumb-init)
- Show the relevant `application.properties` settings:
```properties
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### H2: The Complete Recipe

Assemble all three layers into a single coherent Kubernetes deployment spec. This is the "copy this" section.

```yaml
# terminationGracePeriodSeconds must be > sum of all shutdown times
# PgBouncer: 5 + 45 = 50s
# App: 13s sleep + 30s graceful shutdown = 43s  
# Buffer: 10s
# Total: ~100s
terminationGracePeriodSeconds: 120

containers:
- name: pgbouncer
  lifecycle:
    preStop:
      exec:
        command: ["/bin/sh", "-c", "sleep 5 && killall -TERM pgbouncer && sleep 45"]

- name: app
  lifecycle:
    preStop:
      exec:
        command: ["/bin/sh", "-c", "sleep 13"]
  readinessProbe:
    httpGet:
      path: /actuator/health
      port: 8080
    periodSeconds: 2
    failureThreshold: 3
```

And the matching `application.properties`:
```properties
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### H2: Verifying It Works
- How to confirm: watch error rates during a rolling deploy in Datadog/Grafana
- Manual test: `kubectl rollout restart deployment/<name>` while running `wrk` or a simple `while true; do curl ...; done`
- What healthy looks like vs what a timing gap looks like in metrics
- One gotcha: `terminationGracePeriodSeconds` must be longer than your longest preStop hook + app shutdown time combined, or Kubernetes SIGKILL fires and you lose everything

---

## Key Points to Nail
- The PgBouncer 1.23.0 signal behavior change is a real footgun — many teams upgraded and unknowingly changed shutdown behavior
- The endpoint deregistration race is underappreciated; it's the reason `sleep 5` on the app alone doesn't work
- The formula-based approach makes the timing explainable and tunable, not just "try bigger numbers"
- `server.shutdown=graceful` is off by default in Spring Boot — this surprises most people

## Research Gaps
- Add personal example: what specifically broke, which layer was misconfigured
- Optional: production incident reference (PGBouncer Traffic Spike Incident 2025-09-28 in wiki has relevant detail)
- Verify Spring Boot version where `server.shutdown=graceful` was introduced (2.3, confirm)
