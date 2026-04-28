+++
title = "The Long Road to Not Thinking About Concurrency"
description = "From JavaScript's colored functions and Python's asyncio, through Kotlin coroutines and Reactor, to Java virtual threads and Haskell's IO monad — a decade of watching the ecosystem try to make concurrent I/O safe."
summary = "Every language and runtime has a different answer to the same question: how do you write code that waits on I/O without wasting a thread? JavaScript gave us colored functions. Python copied that. Kotlin gave us coroutines that look synchronous but aren't. Java 21 gave us virtual threads that actually are synchronous. Haskell gave us the IO monad, which makes the whole question a type error. This is how my thinking about each of these evolved."
categories = ["Software Engineering"]
tags = ["concurrency", "async", "javascript", "python", "kotlin", "java", "haskell", "virtual-threads", "coroutines", "io-monad"]
keywords = ["colored functions async await", "python asyncio", "kotlin coroutines blocking", "java virtual threads project loom", "haskell io monad", "structured concurrency", "async runtimes comparison"]
date = "2026-04-26"
draft = true
bibliography = "structured-concurrency-footgun.bib"
+++

The central problem of concurrent I/O is deceptively simple: you want to wait for the network without wasting a thread. Every language and runtime has landed on a different answer, and each answer tells you something about the tradeoffs they were willing to make, the audience they were optimizing for, and — often — what they'd do differently with hindsight.

This is the order I encountered these ideas, and how my thinking about each one changed.

---

## The Colored Functions Problem

The best framing I know for why `async/await` is architecturally awkward comes from Bob Nystrom's 2015 post ["What Color is Your Function?"](https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/){{< cite "nystrom2015color" >}}. The premise: in an async/await language, functions have two colors — sync and async. The rules:

- A sync function can call a sync function. Fine.
- An async function can call either. Fine.
- **A sync function cannot call an async function.** This is the footgun.

The third rule means `async` is contagious. The moment you need to await anything, the function must be `async`. Every caller must then be `async`. Every caller's caller. You can't stop until you've recolored the entire call stack up to whatever top-level entry point accepts it. The type system didn't ask for this — it emerged as a consequence of the execution model.

I ran into this in JavaScript before I had words for it. Add an `await` somewhere in a utility function and suddenly you're updating twelve callers, then their callers, wondering why a one-line change rippled through half the codebase.

### JavaScript

JavaScript is single-threaded. There is one call stack, one event loop, no preemption. The original concurrency model was callbacks: pass a function to `setTimeout`, `fs.readFile`, or `XMLHttpRequest` and it will be called when the operation completes. This works until you have multiple asynchronous dependencies, at which point it produces callback hell.

Promises cleaned up the nesting. `async/await` made promise chains look synchronous. But the underlying model didn't change — you're still describing a continuation that will run when the event loop gets to it. The colors are still there; they're just less visible.

```javascript
// Looks like synchronous code — the color is invisible
async function getUser(id) {
  const row = await db.query('SELECT * FROM users WHERE id = $1', [id]);
  return row.rows[0];
}

// Sync functions can't call it without becoming async themselves
function computeSomething() {
  const user = getUser(42); // Returns a Promise, not a User
}
```

The reason JavaScript landed here is historical: there was no alternative. You cannot block the event loop — it's the only thread. M:N scheduling (many logical tasks, few OS threads) was the only model that makes sense for a single-threaded runtime. The color problem is an inherent consequence of that constraint, not a design failure.

What I didn't appreciate at the time: JavaScript's constraint is also a feature. Because there's one thread, there are no data races on shared mutable state, as long as you don't yield. The model is coherent even if it's awkward to propagate.

### Python

Python's `asyncio` imported the JavaScript model almost directly: `async def`, `await`, a single-threaded event loop — same colors, same contagion rules. The difference is that Python already had threads and a rich synchronous ecosystem before `asyncio` arrived in 3.4.{{< cite "pep3156asyncio" >}} The friction is worse than in JavaScript, where async was the model from the start.

```python
import asyncio
import httpx

async def fetch_user(user_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/users/{user_id}")
        return response.json()

# requests.get() called from async context blocks the entire event loop
def legacy_fetch(url: str) -> str:
    import requests
    return requests.get(url).text  # Silent landmine in async context
```

The Python ecosystem split: `requests` vs `httpx`, `psycopg2` vs `asyncpg`, Flask vs FastAPI. Every popular library needed a rewrite or a wrapper. Code that worked in the sync world had to be audited before being called from async context — and libraries that internally used threads, blocking I/O, or `time.sleep()` became landmines that produced no warnings.

The GIL complicates this further. Python threads exist, but the Global Interpreter Lock prevents true parallel execution of Python bytecode.{{< cite "pythongil" >}} `asyncio` is more efficient for I/O-bound workloads because it avoids thread context switching — but the programming model is more complex, and the async/sync divide is more painful precisely because the existing synchronous ecosystem is so large.

What changed my thinking: the ecosystem split is a real, ongoing cost. A developer who reaches for `requests` inside an `asyncio` application won't get a type error or a clear runtime error — they'll get degraded performance, or in pathological cases, a hung event loop that requires knowing how the event loop works to diagnose.

---

## Structured Concurrency: The JVM Attempt

The JVM has always had real OS threads — preemptive, parallel, expensive. For many years the answer to concurrent I/O on the JVM was "use a thread pool and blocking I/O." It works, but thread-per-request doesn't scale past a few thousand concurrent connections: OS threads carry ~1MB stack overhead by default,{{< cite "jep425virtualthreads" >}} context switching is expensive, and the scheduler knows nothing about your application's structure.

Project Reactor and RxJava brought the reactive/event-loop model to the JVM. Kotlin coroutines tried to keep synchronous-looking code while achieving M:N scheduling underneath. Both ran into variants of the colored-function problem.

### Project Reactor

Before cataloguing what went wrong, it's worth being precise about what Reactor gets right. Event-loop concurrency on the JVM is genuinely good at something: squeezing high throughput from a small thread count when the work is almost entirely I/O-bound.

Reactor's `Flux` and `Mono` types give you a composable pipeline where each step is explicit about whether it runs on the caller, a specific scheduler, or the thread that completes the upstream operation. For services that are pure I/O fan-out — aggregate five upstream calls, merge, return — a reactive pipeline is a near-perfect fit. A handful of threads can service thousands of in-flight requests with no context switching overhead. Backpressure is built into the model: `Flux` can signal to upstream producers when it can't keep up, preventing the unbounded queue growth that kills thread-pool-based systems under load.{{< cite "reactordocs" >}}

The model also enforces something by accident that turns out to be valuable: because there's no blocking allowed, every operation that reaches out to the network or disk must be explicitly modelled as a deferred value. The call graph is a declaration of what the system does, not a description of how threads move through it. For services where latency attribution matters, this is genuinely useful.

The problems start when "no blocking" is a convention rather than a constraint.

### Kotlin Coroutines

Coroutines recolor functions with `suspend`. A `suspend` function can yield the underlying thread while waiting for I/O. Non-`suspend` functions cannot call `suspend` functions directly. The same contagion rules apply — though the color is explicit in the type signature rather than being a naming convention, which is arguably better than Python's runtime-only enforcement.

The model is genuinely elegant. `coroutineScope` gives you a supervision tree: child coroutines are cancelled if the parent is cancelled, exceptions propagate predictably, there are no fire-and-forget tasks leaking beyond their scope. `Flow` gives reactive stream semantics that read like sequential code. For teams that fully internalize it, it's powerful.

The problem is the contract the type system cannot actually enforce.

```kotlin
// The suspend modifier promises: "I will not block my underlying thread."
// The Kotlin compiler does not check this promise.
suspend fun fetchUser(id: Long): User {
    Thread.sleep(500)                   // Parks the OS thread. Compiles fine.
    return userRepository.findById(id)  // Blocking JDBC. Compiles fine.
}
```

`suspend` is a calling convention, not an effect marker.{{< cite "kotlindispatchers" >}} It tells the compiler how to transform the function into a state machine. It does not encode "this function performs only non-blocking work." A `suspend` function that calls `Thread.sleep()` or a blocking JDBC driver parks the underlying dispatcher thread without suspending the coroutine. The scheduler doesn't know. The thread doesn't return to the pool.

I ran into this in production running a Backend for Frontend serving real-time trader traffic. Reactor's schedulers — `Schedulers.boundedElastic()` and `Schedulers.parallel()` — are application-wide singletons.{{< cite "reactorschedulers" >}} Every reactive pipeline in a shared-deployment monolith shared the same thread pools. When any single team's code blocked a thread in the shared scheduler, every team's requests slowed down — not just the team whose code was at fault.

This happened five or six times, across different engineers on different teams, in different quarters. Each time it presented as general latency degradation: slow database metrics that didn't match what the database was doing, P99s climbing without a clear localized cause. Each time, diagnosis required the Datadog JVM profiler{{< cite "datadogjvmprofiler" >}} to show Reactor scheduler threads spending the bulk of their time in `BLOCKED` state — and tracing which team's code was responsible required significant investigation on top of that.

The lesson wasn't "train people better." It was: **the compiler doesn't warn you, so the knowledge has to be re-taught to every new engineer who joins.** Knowledge resets; type errors don't. Every new hire, every oncall rotation, every library upgrade that changes blocking behavior in a transitive dependency resets the clock on when the next incident happens.

### The Go Model (for contrast)

Go goroutines look entirely synchronous — no `async`, no `await`, no color. `go fetchUser()` launches a goroutine; inside, you write blocking code. The Go runtime intercepts standard library blocking calls — network I/O, file I/O, `time.Sleep` — and parks the goroutine transparently when they block, freeing the underlying OS thread for other goroutines.

The color problem doesn't exist because there's only one color. The tradeoff: code that goes through Go's standard library gets transparent scheduling. Code that calls into C via cgo, or uses raw `syscall` directly, can pin OS threads — and the boundaries are mostly invisible. Go's `-race` flag detects data races at test time,{{< cite "goracedetector" >}} but data races are a separate problem from blocking; in Go, blocking in any context is fine by design.

---

## Java Virtual Threads: Eliminating the Constraint

Java 21's virtual threads ([Project Loom](https://openjdk.org/jeps/444)) take Go's approach and apply it to the full JVM. Virtual threads are cheap (~few KB heap vs ~1MB stack for platform threads), and they write exactly like platform threads — blocking code, no annotations, no color.

```java
// This blocking JDBC call unmounts the virtual thread when waiting for the DB.
// The carrier OS thread is freed to run other virtual threads.
// No withContext. No dispatcher. No suspend modifier.
User user = jdbcTemplate.queryForObject(
    "SELECT * FROM users WHERE id = ?", userRowMapper, id
);
```

When a virtual thread blocks on a socket, a JDBC call, a lock, or `Thread.sleep()`, the JVM unmounts it from its carrier OS thread. The carrier becomes available for other virtual threads. When the blocking operation completes, the virtual thread is rescheduled. No programmer annotation required.

The remaining failure mode: virtual threads can be *pinned* to their carrier when blocking inside a `synchronized` block or a native frame.{{< cite "jep444virtualthreads" >}} Pinned threads don't yield the carrier, which can cause carrier thread starvation — analogous to dispatcher starvation in coroutines. The critical difference: the JVM makes this visible. `-Djdk.tracePinnedThreads=full` logs a stack trace every time pinning occurs. JFR (Java Flight Recorder) exposes pinning events. The failure has an observable signal rather than presenting as mysterious latency.

We deprecated Reactor in new code the week virtual threads hit GA. We haven't had nearly as many scheduler starvation incidents since.

**What virtual threads don't give you**: Java's `StructuredTaskScope` (the equivalent of `coroutineScope`) is still in preview as of Java 21-22 — not production-stable.{{< cite "jep453structuredconcurrency" >}} There's no built-in Flow equivalent. Cancellation is less ergonomic. If you're building in the Kotlin ecosystem where Flow, StateFlow, and lifecycle-aware coroutines are load-bearing, virtual threads are fighting the current.

---

## The Type System Answer: Haskell's IO Monad

Every approach so far is a runtime scheduling solution. They make blocking I/O cheaper, or they make violations of non-blocking contracts detectable. None of them make the violation impossible.

Haskell does something categorically different. It makes I/O a type.

In Haskell, every function that performs I/O has `IO` in its return type.{{< cite "haskellwikiio" >}} A pure function — one that takes inputs and returns an output with no side effects — cannot perform I/O. Not at runtime, not in tests, not behind a flag. The compiler refuses to compile code that performs I/O in a pure context.

```haskell
-- Pure function. Cannot do IO. The compiler enforces this.
double :: Int -> Int
double x = x * 2

-- IO action. The IO in the return type is the compiler's proof this does IO.
fetchUser :: Int -> IO User
fetchUser userId = do
  conn <- getConnection
  query conn "SELECT * FROM users WHERE id = ?" (Only userId)

-- Type error. Pure functions cannot use IO actions.
-- broken :: Int -> Int
-- broken x = fetchUser x  -- Won't compile: IO User is not User
```

The `IO` monad is the description of an action that will be performed when the runtime executes it. `<-` in `do` notation binds its result inside another `IO` context. You can't extract a value from `IO User` except inside another `IO` context — so the "color" propagates, but unlike `async/await`, the propagation is a type guarantee, not a convention.

This is the thing the colored functions post gestures at but doesn't quite land: the problem isn't that async propagates — all the models require some form of propagation. The problem is whether the propagation is enforced. In JavaScript and Python, it's a naming convention (`async def`) that the runtime validates at call time. In Kotlin, it's a compiler marker that enforces calling convention but not the contract behind it. In Haskell, it's a type — and the entire type system enforces it.

What this means in practice:

- **Testing pure functions requires no mocking.** A function with no `IO` in its signature provably cannot touch the database, the network, or the filesystem. You don't need a test double because there's nothing to double.
- **I/O boundaries are auditable from the type signature.** You can look at a function's type and know whether it touches the outside world. In Kotlin or Python, you cannot.
- **Blocking vs. non-blocking is derivable.** If a function is `IO`, it might block. If it's pure, it definitely won't. The information is in the type, not in documentation you have to remember to read.

Scala's ZIO extends this: `ZIO[R, E, A]` says "to run this, you need environment `R`, it might fail with `E`, and it produces `A`." Blocking I/O wrapped with `ZIO.blocking` shifts to a blocking-aware thread pool — and the type system records that the shift happened.{{< cite "ziodocs" >}} [Effect-TS](https://effect.website/) brings the same ideas to TypeScript.

The tradeoff is real. Haskell's purity is a substantial upfront investment. Reasoning about how to thread `IO` through a large codebase is non-trivial. The JVM doesn't have this, and retrofitting it would require annotating the entire library ecosystem — every JDBC driver, every `Thread.sleep()`, every Apache HTTP client call. ZIO exists and gets you most of the way, but it requires buying into a specific library ecosystem rather than the platform standard.

---

## Where I Landed

The progression I see across these models:

1. **JavaScript/Python async/await**: M:N scheduling on a single-threaded runtime where blocking is impossible. Forces color onto every function that touches I/O. Correct given the constraints; painful as the codebase and ecosystem grow.

2. **Kotlin coroutines**: M:N scheduling on the JVM with real parallelism. `suspend` makes the color explicit in the type signature, but doesn't enforce the contract behind it. Silent failure modes when blocking calls slip into the wrong dispatcher context.

3. **Java virtual threads**: sidesteps the problem by making blocking cheap. No color. Failure modes are visible (pinning logs) rather than silent (dispatcher starvation). Gives up structured lifecycle management and reactive stream ergonomics.

4. **Haskell IO monad / ZIO**: encodes the distinction between I/O-performing and pure code in the type system. The color is a type guarantee, not a convention. The compiler enforces it. High upfront cost; I/O boundaries are permanently visible and auditable.

The question I now ask about a concurrency model: does the failure mode require expert knowledge to diagnose, or does it leave a trace in the type system or the logs? Kotlin coroutines fail silently and require expert thread dump analysis. Java virtual threads leave a log entry and a stack trace. Haskell's IO monad fails at compile time. The earlier in the cycle you catch the violation, the less it matters how well the whole team understands the concurrency model.

For production JVM services with blocking I/O and mixed-experience teams, I'd reach for virtual threads before coroutines. For code where I/O boundary discipline matters — data pipelines, security-sensitive paths, anything where testability of pure logic is valuable — the IO monad framing is worth the overhead.

The thing I didn't understand early on: the color problem isn't a solvable API design question. It's a consequence of the execution model. You can make the colors cheap (virtual threads), make them a compile-time guarantee (IO monad), or accept them as an operational cost (async/await, coroutines). You can't make them disappear while keeping M:N scheduling and a shared mutable world.

{{< bibliography file="structured-concurrency-footgun.bib" />}}
