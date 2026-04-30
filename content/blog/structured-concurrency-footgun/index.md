+++
title = "Structured Concurrency is a Footgun for Mixed-Experience Teams"
description = "Kotlin coroutines make a promise the JVM's type system cannot enforce. For real-time web applications maintained by teams with mixed concurrency experience, that gap causes repeated, silent production failures. Java virtual threads are the safer default."
summary = "The concurrency model you choose is an implicit contract with your entire team. Kotlin coroutines are brilliant engineering — but they make a promise the JVM's type system cannot enforce, and the failure modes are silent, gradual, and catastrophic. Here's why we deprecated Reactor the week virtual threads hit GA, and what we'd tell ourselves before we started."
categories = ["Software Engineering", "Infrastructure"]
tags = ["kotlin", "java", "concurrency", "virtual-threads", "coroutines", "jvm", "reactor", "project-loom", "platform-engineering"]
keywords = ["kotlin coroutines blocking", "dispatcher starvation", "virtual threads vs coroutines", "project loom java 21", "structured concurrency risks", "reactor scheduler starvation", "blockhound", "mixed experience teams concurrency"]
date = "2026-04-26"
draft = true
+++

The concurrency model you choose is an implicit contract with your entire team. Kotlin coroutines are brilliant engineering — the M:N threading model, structured lifecycle, backpressure-aware flows, and coroutine scopes represent genuinely sophisticated thinking about asynchronous computation. But they make a promise the JVM's type system cannot enforce: that `suspend` functions are non-blocking. That promise is violated constantly in production code, the violations compile without warning, and the failure modes are silent, gradual, and catastrophic. For teams where not everyone deeply understands concurrency, this is a liability, not a feature.

This isn't an argument against coroutines in general. It's an argument that for real-time web applications with mixed-experience teams and blocking I/O dependencies — which describes a large fraction of production JVM services — Java virtual threads have a substantially better risk profile.

---

## A Real Production Failure Pattern

We ran a Backend for Frontend serving real-time trader traffic. Latency-sensitive, always-on, and shared across multiple teams — each team owned their slice of the BFF, but the service was a monolith and the deployment was shared. On the frontend, RxJS. On the backend, Project Reactor on the JVM.

Reactor promised us M:N scheduling: lightweight reactive pipelines, non-blocking I/O, the ability to handle thousands of concurrent in-flight requests on a handful of threads. That promise held in the happy path. What it didn't tell us was what would happen when any single team introduced a blocking call into their slice of the reactive pipeline.

Here's the specific mechanism: Reactor's schedulers — `Schedulers.boundedElastic()` and `Schedulers.parallel()` — are application-wide singletons by default. They're not owned by a team, they're not scoped to a request type, they're not namespaced to a feature. Every reactive pipeline in the entire application shares them. When a blocking call occupies a thread in `boundedElastic()`, that thread isn't available to handle any other team's request. When enough blocking calls pile up simultaneously, the scheduler saturates. Every request in the system slows down — not just the ones touching the team's code.

That's how it presented in production. General latency degradation. Slow database metrics that didn't match what the database was actually doing. P99s climbing without a clear localized cause. The first instinct was to look at the database, the downstream services, the network. Thread dumps eventually showed the real picture: Reactor scheduler threads sitting in `BLOCKED` state. But tracing which team's code was responsible required significant investigation — reading the thread dump was only the beginning, because identifying the call site in a shared reactive pipeline under load is not a one-step process.

This happened five or six times. Not once, where you postmortem it and fix it. Repeatedly, across different engineers on different teams, across different quarters. The reason it kept happening is simple: **the compiler doesn't warn you.** An engineer joining one team had no way to know that calling a blocking API in the wrong scheduler context was a cross-team incident waiting to happen. It wasn't in the onboarding docs. Code review caught it sometimes — when the reviewer knew to look for it. Not always. The test suite didn't catch it, because the problematic load pattern didn't materialize under test.

Every engineer who introduced a block was competent. They were doing the obvious thing — using the synchronous client for a library they'd just integrated, or wrapping a legacy API call they didn't control. The tools gave them nothing. No compiler error. No IDE warning. No test failure. The first signal was production latency.

The fix was to deprecate Reactor and RxJS in new code the week virtual threads hit GA in Java 21. Old code was migrated incrementally. We haven't had a scheduler starvation incident since.

The lesson isn't "your engineers need better training." The lesson is that **this is a type system problem masquerading as a knowledge problem.** You cannot train your way out of a failure mode the compiler refuses to surface. Every new engineer who joins, every team that rotates oncall, every library upgrade that changes blocking behavior in a transitive dependency — they all reset the clock on when the next incident happens. The knowledge has to be re-taught because the tools don't encode it.

---

## What Structured Concurrency Promises

The M:N threading model is the core pitch: map many logical concurrent tasks (coroutines) onto a smaller number of OS threads, eliminating the one-thread-per-request overhead that limits platform thread scalability. A server with 200 platform threads can run hundreds of thousands of coroutines simultaneously, because coroutines suspend at I/O boundaries instead of blocking their underlying thread. The thread goes back to the pool while the coroutine waits for the network, database, or disk.

Structured concurrency extends this with a lifecycle guarantee: coroutines launched within a scope are children of that scope. If a parent coroutine is cancelled, all children are cancelled. If any child fails, the parent and siblings can be cancelled. This creates a supervision tree with predictable cleanup semantics — no leaked goroutines, no fire-and-forget futures floating in the void. In theory, it's exactly what you want for request handling.

`suspend` functions compose cleanly. They look like synchronous code. They're testable with `runTest`. The Flow API brings reactive stream semantics to sequential code without RxJava's callback hell. For Kotlin-native teams that have fully bought in, coroutines are genuinely excellent tools. The problem is the gap between the model's promises and what the type system enforces.

---

## The Contract the Type System Cannot Enforce

Here is the contract you sign when you write a `suspend` function: "I will not block my underlying thread." Here is what the Kotlin compiler checks: nothing.

```kotlin
suspend fun fetchUser(id: Long): User {
    Thread.sleep(500) // Blocks the dispatcher thread. Compiles fine.
    return userRepository.findById(id) // JDBC blocking call. Compiles fine.
}
```

This function suspends in name only. `Thread.sleep()` parks the OS thread. A blocking JDBC call parks the OS thread. The function has the `suspend` marker, so it can be called from coroutines — but it behaves identically to a regular blocking function from the runtime's perspective. The coroutine scheduler does not know the thread is blocked. The thread does not return to the pool. Nothing is logged. No exception is thrown.

The fix is to wrap blocking calls in `withContext(Dispatchers.IO)`, which moves execution to a thread pool designed for blocking work. But the language doesn't require it. The compiler doesn't enforce it. The programmer has to know to do it — and has to correctly identify every blocking call, including those buried in third-party libraries.

Languages with typed effects solve this. In Haskell, `IO` is a type-level marker — a function that performs I/O cannot masquerade as pure. In Scala, ZIO encodes effects in the type signature: `ZIO[R, E, A]` explicitly declares its requirements and failure modes. Calling a blocking operation in the wrong context is a type error, not a runtime surprise. Kotlin has no equivalent. The `suspend` modifier is a calling convention, not an effect contract.

---

## The Failure Modes, Ranked by Severity

### 1. Dispatcher Starvation (Silent, Gradual, Lethal)

Every coroutine runs on a dispatcher. Dispatchers map coroutines to thread pools. The defaults:

| Dispatcher | Thread Pool Size | Intended For |
|---|---|---|
| `Dispatchers.Default` | `max(2, CPU cores)` | CPU-bound computation |
| `Dispatchers.IO` | `max(64, CPU cores)` | Blocking I/O |
| `Dispatchers.Main` | 1 (Android UI thread) | UI updates |

An 8-core server has 8 `Default` dispatcher threads. If 8 coroutines simultaneously block those threads — `Thread.sleep()`, blocking JDBC, blocking file I/O, anything — the dispatcher is starved. Every other coroutine waiting to run on `Default` blocks. The application doesn't crash. It doesn't throw. It slows down asymptotically.

What does this look like in production? The database appears slow. The service latency climbs. P99s spike. Your monitoring shows the database query time is fine; your service latency is not. You add more instances. The same thing happens at a lower request rate. You're in the wrong dispatcher thread pool and the runtime is not telling you.

Diagnosis requires knowing what to look for in a thread dump. `jstack` or async-profiler will show your `Default` dispatcher threads in `TIMED_WAITING` or `WAITING` state inside blocking calls — but only if you know to look at `DefaultDispatcher-worker-*` threads and understand that these threads should not be parked.

### 2. `runBlocking` Inside a Coroutine (Immediate, Deadlock Risk)

`runBlocking` is the bridge from synchronous to coroutine code. It creates a coroutine and blocks the current thread until it completes. The documentation says not to use it inside coroutines. Engineers of varying experience will use it anyway — it's the obvious solution when you're in a suspend context and need to call a suspending function from a Java callback, a test, or a synchronous entry point.

The deadlock scenario:

```kotlin
// On Dispatchers.Default with 8 threads. All 8 are running request handlers.
suspend fun handleRequest() {
    val result = runBlocking { // Blocks thread 1
        someOtherSuspendFun() // Needs a Default dispatcher thread to run
    }
}
```

`runBlocking` parks thread 1 waiting for `someOtherSuspendFun()` to complete. `someOtherSuspendFun()` needs a `Default` dispatcher thread to execute. If threads 2-8 are also blocked in `runBlocking`, there are no threads available. Deadlock. The server stops responding. No exception. No log entry. Timeouts, eventually.

The transitive risk makes this worse: libraries that internally use `runBlocking` carry the same risk. Retrofit's blocking adapter, some legacy OkHttp interceptors, synchronous gRPC stubs — if a library you're using internally calls `runBlocking` and you're running on a dispatcher with limited threads, you have the same problem without having written a single line of blocking code yourself.

### 3. Silent Cancellation Propagation (Surprising at Scale)

`coroutineScope` provides structured concurrency with a specific semantic: if any child coroutine fails with a non-cancellation exception, all sibling coroutines are immediately cancelled, and the scope propagates the exception upward.

`CancellationException` is the mechanism. It's thrown at every suspension point in a cancelled coroutine. Critically, it's supposed to be re-thrown, not caught — catching it silently is a bug. But it extends `Exception`, not `Error`, so any `catch (e: Exception)` block that doesn't explicitly re-throw `CancellationException` swallows it.

```kotlin
coroutineScope {
    launch { fetchFromDatabase() }      // coroutine A
    launch {
        try {
            fetchFromSlowService()       // coroutine B — throws after timeout
        } catch (e: Exception) {
            logger.error("Failed", e)   // Swallows CancellationException
            // coroutine A is already cancelled. This log entry is the only evidence.
        }
    }
}
```

At request-handling scale, one consistently flaky downstream service generates a steady stream of cancellations that silently terminate legitimate in-flight work. If the catch block doesn't re-throw `CancellationException`, the failure disappears from your error metrics entirely. You may observe higher-than-expected cache miss rates or incomplete response data without ever seeing an exception in your logs.

### 4. The Library Ecosystem Trap

The JVM ecosystem is enormous and predominantly blocking. JDBC is blocking. Most HTTP clients default to blocking mode. File I/O is blocking. Libraries written before coroutines existed are blocking. Libraries written by developers unfamiliar with coroutines are blocking.

`Dispatchers.IO` exists precisely because blocking I/O is unavoidable. The pattern is correct: wrap blocking calls in `withContext(Dispatchers.IO)`. The problem is that this requires every engineer who introduces a new dependency to audit that dependency for blocking calls, understand which dispatcher it's running on, and apply the wrapper correctly. It requires the same audit for every upgrade of existing dependencies, because a library can introduce blocking calls in a minor version.

A junior engineer adding a new third-party API client will use whatever Java API the library exposes. If the library's synchronous client is the obvious entry point, they'll use it. They will not receive a compiler warning. They will cause a production incident — possibly not immediately, possibly not under normal load, possibly only during a traffic spike when the `Default` dispatcher saturates.

---

## Why the Type System and Static Analysis Cannot Save You — Yet

The obvious fix is to make the tools detect this — much like Go's race detector makes data races detectable. That's the right instinct. Here's why we're not there yet.

There are three levels at which this problem can be solved, and each language or runtime picks a different one.

### Level 1: The Type System (Compile-Time — Strongest)

The theoretically ideal solution encodes "blocking vs. non-blocking" in the type signature. If calling a blocking function in a non-blocking context is a type error, the compiler catches it before it compiles, let alone reaches production.

Two ecosystems actually do this. Haskell's `IO` monad makes effects explicit in the type — a pure function cannot perform I/O, and the compiler enforces it. Scala's ZIO encodes effects in the type signature: `ZIO[R, E, A]` explicitly declares requirements and failure modes; blocking work must be wrapped in `ZIO.blocking`, which shifts it to a blocking-aware thread pool. Effect-TS does the same in TypeScript.

Why doesn't Kotlin have this? Kotlin has no effect system. Adding one would be a major language redesign, not an incremental improvement. And that's just the language — the JVM ecosystem is enormous. Every JDBC driver, every Apache HTTP client, every `Thread.sleep()` call in the entire library graph would need annotation for the type system to actually catch violations. This option is not available to JVM teams today.

### Level 2: Runtime Instrumentation (Test-Time — Strong)

The next best thing is to detect violations at runtime during test execution. This is what Go's race detector does for data races.

Go's `-race` flag instruments memory accesses at runtime to detect concurrent reads and writes without synchronization. It doesn't prevent races at compile time — it detects them when the racy code path is actually exercised during a test run. Crucially, Go ships this as a first-class, blessed tool with a strong community norm: run with `-race` in CI by default.

**BlockHound** is the JVM's closest equivalent for blocking detection. It instruments the JVM to throw `BlockingOperationError` when a blocking call occurs on a thread registered as non-blocking. `kotlinx-coroutines-core` ships a `CoroutinesBlockHoundIntegration` — first-class support, not bolted on. But it's not part of the standard toolchain. There's no community norm of "run with BlockHound in CI." Teams have to discover it, configure it, and maintain it themselves.

The gap between Go's race detector and BlockHound is not technical. It's cultural. The race detector ships with the language and has a blessed, visible community norm. BlockHound requires you to already know what the problem is before you can configure the solution.

### Level 3: Discipline and Code Review (Production — Weakest)

This is what most Reactor and coroutine teams actually rely on. It fails when: new engineers join, code reviews have gaps, the blocking call is inside a third-party JAR, or the team is under deadline pressure. This is not a knowledge problem you can train your way out of permanently. Knowledge resets with every new hire.

### A Note on How Go Goroutines Actually Work

There's a subtlety worth naming. Go goroutines avoid the blocking problem not through a type system but through the runtime: Go intercepts standard library blocking calls — network I/O, file I/O, `time.Sleep` — and parks the goroutine transparently. The goroutine suspends; the OS thread is reused. This is exactly what Java virtual threads do. Neither is a type-level solution; both are runtime scheduling solutions that make blocking safe without requiring programmer annotation. Go's `-race` flag detects data races — a separate problem entirely.

The conclusion: virtual threads solve the blocking problem by **eliminating the constraint** rather than detecting violations of it. There's nothing to detect because blocking is safe by design.

---

## The Team Experience Dimension

This isn't hypothetical. We saw this pattern five or six times in a shared BFF serving real-time trader traffic — each time caused by a different engineer on a different team, each time presenting as generalized latency rather than a localized failure, each time requiring expert-level thread dump analysis to diagnose.

Senior engineers who have internalized the coroutine model write correct coroutine code. The model is powerful for them. Junior and mid-level engineers will write blocking code in coroutines — not because they're careless or incompetent, but because the language does not prevent it, the mental model isn't obvious from the syntax, the blocking version of an API they already know is right there, and the test passes because it doesn't exercise the problematic load pattern.

The oncall dimension makes this worse. When your service stops responding at 3am, the engineer who gets paged needs to diagnose the problem with a thread dump. A traditional thread dump showing platform threads in `BLOCKED` state on a JDBC connection is readable — you know what's happening and where. A coroutine dispatcher thread dump showing `DefaultDispatcher-worker-*` threads in `WAITING` state requires knowing the coroutine threading model to interpret correctly. The engineers most likely to introduce the bug are often the engineers least equipped to diagnose it under pressure.

The knowledge asymmetry compounds over time. The senior engineers who understand coroutines deeply are also the engineers consulted to fix production incidents they didn't cause. The pattern is: junior engineer introduces blocking call in coroutine → production incident → senior engineer diagnoses and fixes → no systemic change because the solution requires significant concurrency background to teach effectively. The cycle repeats.

---

## What Virtual Threads Actually Trade Off

Java virtual threads (Project Loom, stable in Java 21) address the scalability problem from a different direction: instead of suspending at logical checkpoints, the JVM unmounts virtual threads from their carrier OS threads when they block. Blocking code becomes non-blocking at the platform level without requiring programmer annotation.

```java
// This blocking JDBC call unmounts the virtual thread when waiting for the DB.
// The carrier thread is free to execute other virtual threads.
User user = jdbcTemplate.queryForObject(
    "SELECT * FROM users WHERE id = ?", userRowMapper, id
);
```

No `withContext`. No dispatcher selection. The blocking call works exactly as it always has, but the JVM handles the scheduling. JDBC, blocking HTTP clients, file I/O — all safe on virtual threads without modification.

**The visible failure mode**: Virtual threads can be *pinned* to their carrier thread when blocking inside a `synchronized` block or native frame. Pinned threads don't yield the carrier thread, which can cause carrier thread starvation analogous to dispatcher starvation in coroutines. The critical difference: the JVM makes this visible. `-Djdk.tracePinnedThreads=full` logs a stack trace every time a virtual thread pins. JFR events expose pinning. The failure mode has an observable signal.

**What you lose compared to coroutines**:

- No built-in Flow/reactive streams equivalent — you'd use something else (RxJava, Reactor, or CompletableFuture chains)
- `StructuredTaskScope` (the Java equivalent of coroutine scopes) is still in preview as of Java 21-22 — not production-stable
- No Android support — Kotlin coroutines are the only option there
- Less ergonomic cancellation and lifecycle management
- The Kotlin ecosystem (Flow, StateFlow, SharedFlow, lifecycle-aware coroutines in Compose) assumes coroutines throughout — if you're building in that ecosystem, virtual threads are fighting the current

For a Kotlin-first microservice using Ktor or Spring WebFlux, coroutines are the natural fit. For a Java or Kotlin service using Spring MVC with blocking JDBC and third-party REST clients, virtual threads give you the same M:N scalability with substantially safer failure modes.

---

## What You Can Do Today (And Why It's Not Enough)

The obvious response is: just add tooling. That's the right instinct. There are real tools and they're worth using. Here's an honest picture of what each one catches — and where each one stops.

### BlockHound

```kotlin
// build.gradle.kts
testImplementation("io.projectreactor.tools:blockhound:1.0.9.RELEASE")
```

```kotlin
BlockHound.install(
    CoroutinesBlockHoundIntegration()
)
```

Instruments the JVM to throw `BlockingOperationError` when a blocking call is made on a coroutine dispatcher thread. Catches `Thread.sleep()`, `Object.wait()`, blocking socket and file I/O, JDBC calls — if your test exercises the code path. Misses blocking calls your test suite doesn't exercise, and blocking calls inside third-party JARs that aren't on BlockHound's known-blocking list.

I've been in codebases where BlockHound was added to a TODO comment in the test setup file and never actually configured.

### Detekt Coroutine Rules

```yaml
coroutines:
  active: true
  GlobalCoroutineUsage:
    active: true
  InjectDispatcher:
    active: true   # most operationally valuable
  SuspendFunWithFlowReturnType:
    active: true
```

`InjectDispatcher` is the most useful rule: bans hardcoded dispatchers, forces them to be injected, makes dispatcher choice visible at call sites and testable. Catches structural antipatterns; cannot see inside third-party JARs.

### IntelliJ's `BlockingMethodInNonBlockingContext` Inspection

Zero configuration. Covers a list of known stdlib blocking methods inside `suspend` functions. A senior engineer reading that list could name five real-world blocking patterns it won't catch. It's a per-engineer IDE guardrail, not a CI enforcement mechanism.

### The Honest Assessment

Even with all three active, coverage is bounded by your test suite. The configuration surface drifts — BlockHound integrations fall out of date, Detekt suppressions accumulate, IDE inspections aren't uniformly enabled. The underlying problem remains: you're adding detectors next to a footgun, not removing the footgun.

Compare this to virtual threads: there is no configuration. Blocking is safe. The only thing to configure is `Executors.newVirtualThreadPerTaskExecutor()`.

The mitigation stack is real, it helps, and you should use it if you're committed to coroutines. But it's defense-in-depth for a problem virtual threads don't have.

---

## The Recommendation

**Real-time web applications** with blocking I/O dependencies and **mixed-experience teams**: Java 21+ virtual threads. The failure modes are visible. Blocking code works without modification. The oncall engineer at 3am gets a readable signal.

**Android**: Kotlin coroutines. There is no alternative. Invest in deep team education on dispatchers and lifecycle-aware coroutine APIs.

**Kotlin-first teams building event-driven systems** where the entire team understands coroutines, has BlockHound in CI, and has audited their dependency surface: coroutines and Flow. You're getting real value from the model and your team can defend it operationally.

The test I'd apply: can your most junior engineer write safe concurrent code in a production service without a senior engineer reviewing every coroutine boundary? With virtual threads, probably yes — blocking code works, pinning is visible, nothing is silent. With Kotlin coroutines, probably not.

We deprecated Reactor in new code the week virtual threads hit GA in Java 21. We haven't had a scheduler starvation incident since.

Choose the model your whole team can operate safely, not just the model your best engineers can use brilliantly.
