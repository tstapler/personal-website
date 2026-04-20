+++
title = "Zero-Downtime Postgres Deployments: Getting PgBouncer, Spring Boot, and Kubernetes to Cooperate"
description = "How to wire PgBouncer graceful shutdown, Spring Boot connection drain, and Kubernetes endpoint deregistration together so rolling deploys stop dropping connections"
summary = "Three independent systems need to coordinate for zero-downtime Postgres deployments — and the docs for each only cover that layer in isolation. Here's the complete recipe."
categories = ["Infrastructure", "Software Development"]
tags = ["kubernetes", "pgbouncer", "spring-boot", "postgres", "zero-downtime", "graceful-shutdown", "platform-engineering"]
keywords = ["pgbouncer graceful shutdown kubernetes", "spring boot zero downtime deployment", "kubernetes endpoint deregistration", "pgbouncer sigterm sigint", "rolling deploy connection errors"]
date = "2026-04-18"
draft = true
+++

## The Problem That Shouldn't Still Be Happening

At [Fanatics Betting and Gaming](https://www.fanatics.com/sports-betting), availability isn't an abstract SLO — it's table stakes for the business. Real money gaming customers expect their funds to be safe and their bets to go through, and our traffic pattern doesn't give us much room for error. Our peak load isn't a gradual ramp; it's a step function. A Super Bowl commercial airs, and within seconds a substantial chunk of our customer base hits the login endpoint simultaneously and tries to place a bet before the next snap. Then traffic drops back down to baseline.

That pattern shapes how we think about infrastructure. We pre-scale before major events rather than relying on autoscaling to catch up, and we're cautious about Postgres connection counts — Postgres has a fixed `max_connections`, and each connection is a heavyweight resource. PgBouncer is what keeps hundreds of application pods from each holding a pool of open connections to the database. It sits between the app and Postgres, multiplexing many application connections down to a smaller number of real database connections.

Which means during a rolling deploy, we're not just restarting application pods — we're tearing down and recreating the connection proxy layer that the entire service depends on. And if the shutdown sequencing is off by a few seconds, customers see errors at exactly the moment they're trying to place a bet.

We ran into this the hard way during a live incident. One application had long-running database queries that were holding connections open on a shared PgBouncer instance — not ideal, I know, but we were moving fast and that was the architecture we had. Those held connections were starving other services of pool capacity, so the remediation was to restart the PgBouncer pods with a higher `default_pool_size`. Reasonable fix. Except when PgBouncer came back up, it restarted cold: no warm connections, nothing pre-established to the database. Under normal circumstances that's fine — the pool warms up quickly. Under incident conditions with traffic already elevated, that cold start meant every incoming request had to wait for a brand-new database connection to be established while the pool rebuilt itself. We'd fixed the pool size problem and created a connection warming problem in its place.

That incident made us properly audit the shutdown and startup sequencing. What we found was that getting to truly zero connection errors during a PgBouncer restart requires three independent systems to coordinate in the right order, and each system's documentation only covers its own layer.

The three layers:

1. **Kubernetes** stops routing new traffic to the pod (asynchronous, takes 5–15s)
2. **PgBouncer** drains its client and database connection pools (10–60s, depending on pool mode)
3. **Spring Boot** finishes in-flight requests and closes cleanly (5–30s, depending on query duration)

Miss the timing on any one of these, and you drop connections. Get all three right, and rolling deploys become silent.

---

## Why "Just Add a preStop Sleep" Doesn't Work

The standard advice is to add a preStop hook with a sleep so the pod stays alive long enough to drain. That's correct, but incomplete — and where it fails is instructive.

### The Endpoint Deregistration Race

When Kubernetes decides to terminate a pod, three things kick off *in parallel*:

- `kubelet` starts the pod shutdown sequence (preStop hooks, then SIGTERM)
- `kube-proxy` updates iptables rules on all nodes to stop routing to the pod
- The endpoints controller removes the pod from the Service's endpoint list

The problem is that kubelet starts immediately, while the traffic cutoff is asynchronous. In a typical cluster, endpoint propagation takes 5–15 seconds. Add a short preStop sleep on your app container and Kubernetes runs it *while traffic is still arriving*. By the time the sleep finishes and SIGTERM fires, in-flight requests that arrived during those seconds get killed.

A `sleep 5` on the app alone doesn't solve this — the sleep needs to be long enough to cover endpoint propagation plus the time for readiness probe failures to register.

### The PgBouncer Signal Trap

Most people assume SIGTERM means graceful shutdown for any well-behaved Unix process. For PgBouncer, this assumption is version-dependent and has bitten a lot of teams.

**Before PgBouncer 1.23.0**: SIGTERM meant *immediate exit*. SIGINT was the graceful shutdown signal — it paused new connections and waited for active ones to drain.

**PgBouncer 1.23.0+**: SIGTERM now performs a "super-safe shutdown" that waits for every client to disconnect. In session mode, that can mean waiting *minutes*. Immediate exit moved to SIGQUIT.

If you upgraded PgBouncer without updating your preStop hook, you silently changed shutdown behavior. A hook that used to exit quickly now hangs waiting for the last session to close — and if `terminationGracePeriodSeconds` expires first, Kubernetes sends SIGKILL and tears down the pod anyway, hard.

Beyond the version issue, there's a genuine signal strategy choice depending on what you're optimizing for:

| Signal | Closes first | Use when |
|--------|-------------|----------|
| SIGTERM (1.23.0+) | Client-facing connections | DB has connection headroom; short connection lifetimes |
| SIGINT | Database-facing connections | DB connection limits are tight; connection lifetime is unpredictable |

For most Spring Boot setups in transaction pooling mode, SIGTERM is the right call — you have headroom, and you want in-flight requests to complete.

---

## The Three Layers, Properly Configured

### Layer 1: Kubernetes Endpoint Deregistration

The preStop hook on your application container exists to bridge the gap between when Kubernetes starts the shutdown sequence and when traffic actually stops arriving. The timing formula:

```
preStop delay = endpoint propagation (5s) + (readinessProbe.periodSeconds × failureThreshold) + buffer (2–5s)
```

For a standard readiness probe configuration (`periodSeconds: 2, failureThreshold: 3`):

```
5 + (2 × 3) + 2 = 13 seconds
```

This goes on the **app container**, not PgBouncer:

```yaml
containers:
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

The sleep keeps the pod alive and healthy while traffic drains away. After the sleep, SIGTERM fires and the app starts its own graceful shutdown.

### Layer 2: PgBouncer Graceful Shutdown

PgBouncer's preStop hook needs its own initial delay to allow endpoint propagation, then sends the signal, then waits for connections to drain.

For transaction pooling mode (the most common setup), the drain wait depends on your longest running transaction. A conservative formula:

```
PgBouncer drain = max_transaction_duration + (readinessProbe.periodSeconds × 2) + buffer
```

With a 30-second max transaction duration:

```
30 + (2 × 2) + 5 = 39 seconds → round up to 45s
```

```yaml
containers:
- name: pgbouncer
  lifecycle:
    preStop:
      exec:
        command: ["/bin/sh", "-c", "sleep 5 && killall -TERM pgbouncer && sleep 45"]
```

The leading `sleep 5` on PgBouncer is the same endpoint propagation delay — you don't want new connections coming into PgBouncer after you've signaled it to drain.

Session pooling mode takes significantly longer (minutes, not seconds) because PgBouncer has to wait for entire sessions to close. If you're on session mode and deploying frequently, this is a strong argument to switch to transaction mode.

One thing graceful shutdown doesn't solve on its own: PgBouncer restarts cold. After the new pod comes up, it has no pre-established database connections — the pool warms up as requests come in. Under normal traffic that's imperceptible. During or immediately after a traffic spike, that cold pool means every request is waiting for a fresh database connection to be negotiated while the pool rebuilds. If you're restarting PgBouncer as part of incident remediation (changing pool sizes under load, for example), consider whether the cold-start cost is acceptable given current traffic, or whether the restart itself will make things worse before they get better. A `min_pool_size` setting can help here — it tells PgBouncer to proactively establish connections on startup rather than waiting for demand.

### Layer 3: Spring Boot Connection Drain

Spring Boot has had graceful shutdown support since 2.3, but it's **off by default**. Without it, SIGTERM immediately closes the application context — active database queries get killed mid-flight.

Turn it on in `application.properties`:

```properties
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

With graceful shutdown enabled, Spring Boot stops accepting new requests, waits up to `timeout-per-shutdown-phase` for in-flight requests to complete, then closes the connection pool and exits. The timeout should be at least as long as your slowest expected query.

One more thing that silently breaks this: if your container's `CMD` is a shell script rather than a direct exec, SIGTERM goes to the shell, not your Java process, and never propagates. Use the exec form:

```dockerfile
# Wrong — SIGTERM goes to sh, not java
CMD ["sh", "-c", "java -jar app.jar"]

# Right — SIGTERM goes directly to java
CMD ["java", "-jar", "app.jar"]
```

Or use a proper init process like [tini](https://github.com/krallin/tini) if you need shell features.

---

## The Complete Recipe

Put it all together. The key constraint: `terminationGracePeriodSeconds` must be longer than the longest path through your shutdown sequence — otherwise Kubernetes fires SIGKILL and none of the graceful logic matters.

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      # PgBouncer: 5s delay + 45s drain = 50s
      # App: 13s sleep + 30s graceful shutdown = 43s
      # Buffer: 15s
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

And the matching Spring Boot config:

```properties
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

---

## Verifying It Works

Don't trust configuration — test it. The simplest approach:

```bash
# Terminal 1: steady stream of requests
while true; do curl -s -o /dev/null -w "%{http_code}\n" http://your-service/health; sleep 0.1; done

# Terminal 2: trigger a rolling restart
kubectl rollout restart deployment/your-app
```

Watch for any non-200 responses during the rollout. If you see a burst of errors right after a pod enters `Terminating`, endpoint deregistration is the culprit — increase the preStop sleep. Errors that persist longer point to PgBouncer drain timing or Spring Boot not draining cleanly.

In Datadog or Grafana, the healthy signature is a flat error rate through the entire deployment. A spike that correlates exactly with pod termination events is the timing gap showing itself.

One last gotcha worth knowing: PgBouncer silently ignores errors returned by `server_check_query` — a quirk that's been present for years ([GitHub #683](https://github.com/pgbouncer/pgbouncer/pull/683)). If you're relying on health checks to detect broken connections, they may not behave as expected.

For services with bursty traffic patterns, there's a related trap with the default `server_check_query = SELECT 1`. When PgBouncer releases a database connection back to the pool, it moves to `sv_used` state and has to pass a health check before it becomes available in `sv_idle`. With the default `server_check_delay = 30s`, a wave of incoming requests can find most of the pool stuck in `sv_used` — connections exist but aren't ready. The health checks run serially and become the bottleneck, driving HikariCP acquisition timeouts.

The fix is counterintuitive: disable the health check entirely.

```ini
[pgbouncer]
server_check_query =        # empty string = no health check
server_check_delay = 600    # 10 minutes
```

This keeps connections in `sv_idle` immediately after release, which is exactly what you want when a traffic spike hits. You're trading proactive connection health verification for immediate connection availability — in practice, TCP keepalive and application-level error handling catch stale connections well enough, and the proactive checks were giving a false sense of safety anyway (see the GitHub issue above).

---

## Further Reading

- [Delaying Shutdown to Wait for Pod Deletion Propagation](https://gruntwork.io/blog/delaying-shutdown-to-wait-for-pod-deletion-propagation) — the definitive write-up on endpoint deregistration timing
- [PgBouncer changelog for 1.23.0](https://www.pgbouncer.org/changelog.html) — where the SIGTERM behavior change is documented
- [Spring Boot Graceful Shutdown docs](https://docs.spring.io/spring-boot/docs/current/reference/html/web.html#web.graceful-shutdown)
