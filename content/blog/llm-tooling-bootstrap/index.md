+++
title = "The Knowledge, Applied: Build the LLM Tools That Build Better Tools"
description = "The most leveraged thing you can do with an AI coding assistant isn't ask it to write code — it's use it to build the toolchain that makes it more capable, consistent, and cheap to operate."
summary = "Lewis Dartnell's book on restarting civilization argues you don't begin with advanced technology — you begin by learning to build the tools that make advanced technology possible. The same logic applies to your LLM development setup. Here's what that toolchain looks like after a year and a half of building it."
categories = ["Software Development", "AI Tools"]
tags = ["claude", "ai", "workflow", "productivity", "dotfiles", "skills", "automation"]
keywords = ["llm tooling", "claude code skills", "claude code hooks", "ai workflow automation", "dotfiles ai", "prompt engineering", "agent development"]
date = "2026-04-26"
draft = true
+++

In *The Knowledge*, Lewis Dartnell argues that the way to rebuild civilization from scratch isn't to memorize how smartphones or jet engines work. It's to understand which foundational technologies unlock all subsequent ones. You start with iron smelting — not because iron is the end goal, but because iron tools let you build the machines that let you build the infrastructure that eventually reaches everything else. The leverage is in the bootstrapping sequence, not the endpoint.

The same logic applies to LLM tooling. The most powerful thing you can do with Claude Code isn't to ask it to write a function or fix a bug. It's to build the tools that make Claude Code better at writing functions and fixing bugs — and then use *those* tools to build the next layer.

---

## The Loop That Made Me Start Building

The specific failure that pushed me to start building was Playwright.

I was trying to write UI tests, and every session turned into a correction loop. Claude would connect to the Playwright MCP server and try to work directly with the raw tool output — which is verbose, token-hungry, and not how you actually want to drive a browser. The right approach is a testing script: navigate to the page, query for the specific elements you care about, take targeted screenshots, assert on what you find. If you give Claude a skill that describes this pattern, it executes it cleanly. Without one, it burns tokens reading raw MCP output and still doesn't get the result right.

So I'd correct it. Explain the pattern. Watch it apply the pattern, sometimes correctly, sometimes not. Then the session would end and the next session would start from scratch. Same corrections. Same explanations. Same mistakes.

This wasn't a Claude problem specifically — it was a *tooling* problem. I was treating an LLM like a search engine: ask a question, get an answer, next question. But an LLM coding assistant is more like a new engineer on the team. You don't re-explain the same conventions every morning. You write them down once, and everyone works from that.

The difference once I had a Playwright skill: tasks that used to take minutes of back-and-forth now complete in one shot, in seconds.

---

## What the Primitive State Looks Like

The solution most people reach for first is `CLAUDE.md` — a project-level instructions file that loads into every session. That's a meaningful step up. But it's still a static document, and a large `CLAUDE.md` is a token cost that degrades every session, not just the ones that need those instructions.

The insight that unlocks the next layer: **instructions should be loaded on demand, not all at once.** An expert consultant doesn't recite their entire resume before every conversation. They answer the specific question. Your AI toolchain should work the same way.

---

## The First Tools: Skills

A skill, in Claude Code terms, is a markdown file containing structured instructions for a specific domain. It's loaded into context when invoked, not before. A 2,000-token skill for reviewing database schemas costs nothing when you're working on the frontend — and is immediately available when you need it.

After about a year and a half of building these, I have around 126 skills covering everything from Spring Boot testing patterns to Kubernetes DNS debugging to Jujutsu version control. But the count matters less than which layer of the stack you invest in first.

The skills that deliver the most leverage aren't the domain-specific ones. They're the *meta* skills — the iron smelters:

`/meta:refine-claude-md` — analyzes your current CLAUDE.md, identifies redundancy and gaps, and produces a tighter version. What used to take a manual audit and careful editing is now a single invocation.

`/meta:new-agent` — guides agent design: tool selection, context scoping, and the patterns that keep agents reliable instead of flaky.

`/skill:create` — drafts the structure of a new skill from a description of what it should do. Produces a file you can iterate on rather than starting from a blank page.

These meta-skills compound directly: every new skill I build goes faster than the last because the tools for building skills are better. But there's a less obvious compounding that matters more: **when Anthropic ships new capabilities, the meta-skills are what let you absorb them.**

Claude Code has changed significantly in a year and a half. New primitives keep arriving — the loop command for polling workflows, background tasks for async agents, the question syntax for pausing mid-task to request human input — none of these existed when I wrote my first skills. A skill that teaches the model how to build agents needs to know about subagent patterns. A skill for managing configuration needs to know about the current hook types. These meta-skills go stale about once a month as the platform evolves, and you need infrastructure to keep them current.

That's where the skill evaluator comes in. Point it at a GitHub repository or a website, and it downloads the content, analyzes it against your current library, and recommends what to adopt or update. When Anthropic publishes new guidance on how Claude Code should work, I don't read through my 126 skills manually to find which ones are outdated. The evaluator does it for me — and incorporates the new patterns with minimal effort on my part.

---

## Agents and Commands

Skills handle *how* to approach a problem. Agents handle *doing* a specific class of work with their own isolated context window — they don't inherit the parent session's state, which means they can run in parallel without contaminating each other's reasoning.

Before I had dedicated agents, researching a new technology meant one long, meandering session that would cover architecture, pivot to pitfalls, then circle back to questions the earlier context had already muddied. Now I spawn three agents simultaneously — one for stack research, one for known failure modes, one for architecture tradeoffs — and synthesize their output into a clean document. Each agent reasons clearly because it only sees its own scoped question, not an hour of accumulated context noise.

Commands are the glue layer: multi-step workflows that orchestrate agents and skills into repeatable pipelines. The `sdd:*` command family implements a full spec-driven development workflow where each step gates the next on a written artifact. The `knowledge:*` commands chain agent calls to process wiki entries, extract learnings, and cross-link concepts. You could do all of this manually — the commands make it a single invocation.

---

## Enforcement: Hooks as CI/CD for AI Behavior

Most developers underinvest in enforcement. Skills and agents improve what the model *tries* to do. Hooks determine what it's *allowed* to do — and make certain behaviors automatic without consuming any context at all.

My `settings.json` has a single PreToolUse hook that fires before every Bash command:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "/home/tstapler/.claude/hooks/rtk-rewrite.sh"
      }]
    }]
  }
}
```

This hook routes every shell command through RTK (Rust Token Killer), a CLI proxy that transparently rewrites verbose commands into token-efficient equivalents. `git status` becomes `rtk git status`, which filters the output to exactly what the model needs and discards the rest. The savings run 60–90% on common dev operations — automatically, without the model thinking about it.

That's the hook pattern at its best: invisible, automatic, compounding. The model doesn't have to remember to use RTK. It runs commands normally and the hook handles the rest.

For behavioral guardrails, the `hookify` plugin lets you define enforcement rules in plain markdown:

```markdown
---
name: require-tests-before-stop
enabled: true
event: stop
action: block
conditions:
  - field: transcript
    operator: not_contains
    pattern: "pytest|npm test|cargo test"
---

Tests not detected in session transcript. Run tests before completing.
```

This rule fires when the model tries to stop, checks whether tests were run, and blocks completion if not. The rule lives in a file, not in CLAUDE.md. It's versioned, composable, and costs zero tokens in every session where it doesn't fire.

---

## The Toolchain Is Production Code

The toolchain needs to be reliable. Skills that give inconsistent advice are worse than no skills — they introduce noise you have to filter. Agents that misunderstand their tool interfaces waste context.

Treat your dotfiles like production code. My dotfiles repo runs a GitHub Actions pipeline on every push: Python type checking with mypy, linting with ruff, and behavioral tests with pytest for scripts that process structured data. It's not comprehensive. It's enough to catch the regressions that matter — a script that used to produce valid YAML now produces a syntax error, a type annotation that silently broke when a dependency changed.

The same discipline applies to the skills themselves — the evaluator scores frequently-used skills against a quality rubric after changes, flagging anything that has drifted. Same instinct as running a test suite before shipping.

---

## The Honest Cost

Expect a short-term productivity hit. You could skip all of this and just use off-the-shelf tools. You'll get results faster in week one.

But the ROI isn't just the time savings — it's understanding how the sausage is made. When you've built a skill from scratch, you understand why skills degrade, what makes a good agent prompt different from a bad one, and why token efficiency matters at the margins. That understanding makes you better at evaluating other people's tooling too, not just consuming it. You can look at someone else's Claude Code setup on GitHub and immediately see what's worth adopting, what conflicts with your setup, and what's outdated. You don't get that from just using Claude Code out of the box.

---

## What to Build First

If you're starting from scratch, the order matters:

**1. CLAUDE.md, minimal.** Not comprehensive — just the highest-leverage constraints. What it should never do, what it should always do, which tools to prefer for common operations. Keep it under 200 lines.

**2. Three skills in domains you touch daily.** Pick the three things you re-explain most often and package them as skills. The Playwright pattern, the testing conventions, the deploy workflow — whatever you spend the most time correcting.

**3. One meta-skill.** Before you have 10 skills, write a skill about how to write skills — what level of specificity works, what examples to include. This is the iron smelter: everything subsequent is faster because of it.

**4. One hook.** Start low-stakes: a PreToolUse hook that runs a linter on file writes, or a Stop hook like the test-enforcement rule above. See how the mechanism works before depending on it.

**5. CI for your dotfiles.** Set up the pipeline before the toolchain is large enough to have regressions. Retrofitting tests onto 100 skills is much harder than starting with an empty repo that already has a working CI run.

The endpoint isn't a specific set of tools. It's a setup where every new tool you need is faster to build than the last, and where the tools themselves stay reliable because the infrastructure around them enforces quality.

Dartnell's argument in *The Knowledge* is that civilization's real achievement isn't the smartphone — it's the accumulated stack of foundational technologies that made the smartphone buildable. The same is true here. The goal isn't 126 skills. It's a system where the 127th skill takes thirty minutes to build correctly, incorporates the latest platform capabilities automatically, and works reliably from day one.

---

## Further Reading

- [*The Knowledge: How to Rebuild Our World from Scratch*](https://amzn.to/3Opxkmw) — Lewis Dartnell. The source of the framing here. Required reading if you care about foundational technology and compounding capability.
- [How I use LLMs to help me write code](https://simonw.substack.com/p/how-i-use-llms-to-help-me-write-code) — Simon Willison. Practical philosophy from one of the most prolific LLM tool-builders working today; Willison treats his tool collection as a compounding asset in exactly the way this post argues for.
- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) — Community-curated list of skills, hooks, slash-commands, agents, and plugins for Claude Code. The best starting point for exploring what others have built and finding patterns worth adopting into your own setup.
- [Promptware Engineering](https://arxiv.org/html/2503.02400v1) — Academic framing of prompts as first-class software engineering artifacts requiring requirements, design, testing, and version control — the research underpinning for treating your skills and CLAUDE.md like production code.
- [Claude Code Hooks](https://docs.anthropic.com/en/docs/claude-code/hooks) — Anthropic documentation for the PreToolUse, PostToolUse, and Stop hook mechanisms.
- [Manifest-Driven Development: My AI Workflow After a Year of Getting It Wrong]({{< ref "/blog/manifest-driven-development" >}}) — The companion post on the overall workflow: phase gates, spec artifacts, and fresh-session enforcement. The skills and agents described here are the tools that workflow runs on.
