# Plan: Kubernetes DNS / ndots Debugging

**Source**: ~/Documents/personal-wiki/logseq/journals/2022_05_03.md (brief mention); external: pracucci.com/kubernetes-dns-resolution-ndots-options-and-why-it-may-affect-application-performances.html
**Target audience**: Homelab Kubernetes users and backend engineers seeing slow external DNS resolution or mysterious connection latency
**Tone**: Debugging story — you hit a weird problem, found a non-obvious cause, fixed it with one line
**Estimated length**: 700–900 words

---

## ⚠️ Research Gap: Personal Story Needed

The source journal (2022_05_03) only has a bullet: "Kubernetes ndots causing bad behavior" with two links. Before drafting, you need to write down the actual experience:

- What service was affected? (Journal mentions Transmission OVPN / homelab "Thesus" cluster)
- What was the symptom? (Slow DNS? Timeouts? Specific error messages?)
- How did you discover it was ndots? (Tcpdump? Logs? The pracucci.com article?)
- What exactly did you change, and what was the before/after?

Without this, the post is a tutorial, not a story. Your existing blog posts (Powerline, Ceph) work because they have a concrete "this happened to me" hook.

---

## Post Structure

### H2: The Symptom
- External HTTP calls slow or timing out intermittently
- Pinging external hosts works fine; curl is slow
- No obvious errors in pod logs
- Personal: what you were actually trying to do (run Transmission over VPN? Set up Thesus?)

### H2: The Investigation
- tcpdump or `kubectl exec` → dig to watch DNS queries
- Seeing 5 queries firing for every single hostname lookup
- The "why is it making 5 queries" realization

### H2: What ndots Actually Does
- `ndots:5` is the Kubernetes default: if a hostname has fewer than 5 dots, the resolver appends search domains first
- For `api.github.com` (2 dots): resolver tries `api.github.com.default.svc.cluster.local`, `api.github.com.svc.cluster.local`, `api.github.com.cluster.local`, `api.github.com.<search-domain>` before trying the bare hostname
- Each failed lookup is a real DNS round-trip — 4–5 × DNS latency before you get the right answer
- Diagram or table showing the query waterfall

### H2: Why Java Makes It Worse
- JVM caches DNS results (positive: 30s default, negative: 10s default in older JVMs)
- With ndots, the first lookup is slow; if the result isn't cached properly, every request pays the penalty
- Some JVM versions cache the first (wrong) NXDOMAIN, causing the external call to fail entirely until TTL expires

### H2: The Fix
- Pod-level: set `dnsConfig.options: [{name: ndots, value: "1"}]` in the pod spec
- Or use fully-qualified domain names with a trailing dot (`api.github.com.`)
- Service-level: only matters for pods making external calls; internal service discovery still works

### H2: Verification
- Before/after dig timing showing query count drop
- Before/after request latency

---

## Key Points to Nail
- The "5 queries for one hostname" is the satisfying reveal
- Keep the Java DNS caching note brief — it's a compounding factor, not the main story
- One-line fix after paragraphs of investigation pays off the story structure
- Link to the pracucci.com article — it's the authoritative reference and worth sending people to

## Next Step Before Drafting
Fill in the personal story details from memory. Even rough notes are enough to make this a real post rather than a tutorial reshuffled from the Pracucci article.
