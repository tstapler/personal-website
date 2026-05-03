# Plan: Managing LLM Context Windows

**Source**: ~/Documents/personal-wiki/logseq/pages/Context Window Management.md
**Target audience**: Engineers building LLM-powered features or tools who have hit context ceiling issues or cost problems
**Tone**: Practical and opinionated — not a survey, make clear recommendations with honest tradeoffs
**Estimated length**: 1000–1400 words

---

## Post Structure

### H2: The Constraint Nobody Talks About
- Context windows sound huge (128K, 1M tokens) until you're actually building something
- The zero-sum constraint: `input_tokens + output_tokens ≤ window_size` — 90% input means 10% for response
- Hidden cost: structured data (JSON, code, tables) costs 2–3x more tokens than prose
- Personal angle: what specifically hit this limit while building something (Claude Code, MDD workflow, etc.)

### H2: The Lost-in-the-Middle Problem
- LLMs pay more attention to content at the beginning and end of context (primacy + recency bias)
- Critical information buried in the middle gets underweighted or ignored
- This is empirically documented (link to the arxiv paper)
- Practical implication: context order is load-bearing, not just context size

### H2: Six Strategies (With When to Use Each)
Keep each strategy tight — one paragraph + a "use this when" line.

1. **Truncation** — cut old/low-priority content; fast, lossy, fine for conversation history
2. **Dynamic model routing** — route by input size to the right model; preserves fidelity, adds ops complexity
3. **Memory buffering** — compress old conversation into summaries; good for chatbots, sliding window effect
4. **Hierarchical summarization** — multi-level compression of long docs; good for structured docs, bad for technical/unstructured content
5. **Context compression** — remove redundancy without paraphrasing, 40–60% reduction; good for logs/transcripts
6. **RAG** — retrieve only relevant chunks at query time; best for large knowledge bases, trades latency for scale

### H2: Selection Criteria (Decision Table)
A simple table: scenario → recommended strategy. Makes it scannable and reference-worthy.

| Scenario | Strategy |
|---|---|
| Long conversation history | Memory buffering |
| Large document analysis | Hierarchical summarization or RAG |
| Verbose/redundant input | Context compression |
| Large knowledge base | RAG |
| Cost-sensitive, quality secondary | Truncation |
| Mixed input sizes | Dynamic model routing |

### H2: For AI Agents Specifically
- Agents need multiple memory types simultaneously
- Working memory (current task) + episodic (recent history, compressed) + semantic (RAG) + procedural (cached action sequences)
- Context budget allocation: treat each layer as a token cost, not unlimited
- Personal angle: how the MDD workflow handles this with 3-layer memory architecture

### H2: Practical Takeaways
- Measure before optimizing: count tokens, find where the budget actually goes
- Context order matters as much as context size
- RAG is the right default for knowledge-heavy apps; everything else is a tradeoff

---

## Key Points to Nail
- The "lost in the middle" insight is genuinely surprising and actionable — lead with it prominently
- The zero-sum input/output constraint is underappreciated; make it concrete with numbers
- Avoid making this a comprehensive survey — pick a recommendation for the common cases
- Personal angle: working in Claude Code daily makes this lived experience, not just theory

## Research Gaps
- Add a personal example of hitting the context wall (specific project or session)
- Optional: token count comparison showing structured vs prose cost difference
