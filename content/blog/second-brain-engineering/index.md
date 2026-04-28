+++
title = "Building a Second Brain for Engineering Work"
description = "Most engineers treat learning as consumption. A Zettelkasten turns it into something that compounds — here's how to build one with Logseq or Obsidian."
summary = "How I use Zettelkasten, Logseq, and a custom sync tool to build a permanent, connected knowledge base from my engineering work."
categories = ["Career Development", "Productivity"]
tags = ["zettelkasten", "note-taking", "logseq", "obsidian", "engineering", "learning", "knowledge-management"]
date = "2026-04-27"
draft = false
+++

When I joined Google from Workiva, I was intimidated by the writing culture. From the outside it looked like engineers wrote documents the way academics wrote papers — precise, structured, permanent. What I came to understand is that the writing *is* the thinking. You don't write a design document to explain what you've already decided. You write it to find out where your thinking has holes.

The same principle applies to how you accumulate knowledge over a career. Most engineers I've met treat learning as consumption: read a book, take a course, close the tab. A year later, it's gone. Not because they're forgetful — because they never externalized the thinking in a way that connects to anything else.

Zettelkasten is the alternative.

---

## What Zettelkasten Is (and Isn't)

Niklas Luhmann was a German sociologist who published 70 books and 400+ papers over a 40-year career. His secret was a wooden box containing ~90,000 index cards. Each card had one idea. Each card linked to other cards. The box became a thinking partner — it would surface connections Luhmann hadn't consciously made, suggest directions he hadn't considered, and hold the accumulated output of decades of reading and thinking without losing any of it.

Zettelkasten is German for "slip box." The method:

1. **One idea per note** — not "chapter summary," not "book notes." One atomic idea that stands alone.
2. **Write in your own words** — if you can't restate it without the source, you don't own it yet.
3. **Link notes to notes** — a note that connects to nothing is storage. A note that links is thinking.
4. **Never delete** — Luhmann's insight was that old notes don't become wrong, they become context.

For engineers specifically, this maps onto things we already do: postmortems, design docs, ADRs, architecture notes. The difference is that in a Zettelkasten, your postmortem learnings can link to the distributed systems paper you read last year, which links to the incident from three jobs ago, which links to your notes on *Designing Data-Intensive Applications*. The value compounds.

---

## Why Engineers Resist It (And Why They Shouldn't)

The common objection is time: "I don't have time to take notes on everything." This misunderstands the practice.

You're not taking notes on everything. You're writing one note — one idea, your own words, with one or two links — when you encounter something worth keeping. That takes three minutes. What takes no time at all is never writing anything down, and the cost of that shows up years later when you're re-learning things you already knew, re-making decisions you already made, and re-solving problems you already solved.

The other objection is tooling: it feels like a yak shave. It doesn't have to be. You need a tool that supports bidirectional links and lets you write in plain text. That's it.

---

## Tools

### Logseq

[Logseq](https://logseq.com/) is what I use. It's local-first, open source, and built around the daily journal as the entry point — which matches how most engineers actually work. You capture in the journal, then promote ideas to permanent pages. It supports bidirectional links, graph view, and queries. Everything lives in plain Markdown on your filesystem.

The daily journal workflow removes the friction of "where does this go." It goes in today's journal. Later, you link it somewhere permanent if it deserves to live past the week.

### Obsidian

[Obsidian](https://obsidian.md/) is the other serious option. It has a larger plugin ecosystem, a stronger community around Zettelkasten specifically, and a more polished graph view. It's also local-first and Markdown-based. The tradeoff vs. Logseq is that Obsidian is more freeform — better if you want fine control over structure, but more setup required to get a workflow that actually sticks.

Both are good. Pick one. The tool matters less than the practice.

---

## Syncing Across Devices: Stelekit

One friction point with local-first tools is synchronization. Logseq and Obsidian both have paid sync options, but if you want full control over where your notes live — and as an engineer, you probably do — you need something else.

I built [Stelekit](https://github.com/tstapler/stelekit) to solve this. It handles syncing my Logseq vault across machines, keeping everything in version control without fighting the tools. If you're running Logseq and want a lightweight sync approach that doesn't require a subscription or a third-party cloud, it's worth a look.

---

## The Reading Foundation

Two books underpin all of this:

**{{< amazon asin="0671212095" title="How to Read a Book" >}}** — Mortimer J. Adler teaches you to read at four levels, the highest of which (syntopical reading) is reading multiple books on the same topic simultaneously and building your own synthesis. A Zettelkasten is where that synthesis lives.

**{{< amazon asin="3982438802" title="How to Take Smart Notes" >}}** — Sönke Ahrens is the book that formalizes Luhmann's system for a modern audience and explains why writing is not the output of thinking, it's the process.

Read those two first. Then start the box.

---

## Where to Start

1. Install Logseq or Obsidian (free, five minutes)
2. Read *How to Take Smart Notes* — it reframes the entire practice
3. For today's journal entry: write one note about one idea you encountered this week
4. Link it to one thing you already know

That's it. The compounding starts on day one.
