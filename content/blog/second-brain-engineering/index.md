+++
title = "Building a Second Brain for Engineering Work"
description = "Most engineers treat learning as consumption. A Zettelkasten turns it into something that compounds — here's how to build one with Logseq or Obsidian."
summary = "How I use Zettelkasten, Logseq, and a custom sync tool to build a permanent, connected knowledge base from my engineering work."
categories = ["Career Development", "Productivity"]
tags = ["zettelkasten", "note-taking", "logseq", "obsidian", "engineering", "learning", "knowledge-management"]
date = "2026-04-27"
draft = false
+++

I run Manjaro Linux on a fully encrypted NVMe drive. If you've done the same, you know the experience: occasionally, after a restart, something stops cooperating. Screen goes black. A driver disappears. The system boots slowly for no obvious reason. Before I had a note-taking system, I'd burn an hour retracing my steps — digging through browser history, re-Googling searches I'd already run, trying to reconstruct what I'd tried and what had worked last time. I'd find the right incantation, fix it, and promptly forget everything I'd just learned.

Over time I started logging every attempt in my vault: what I tried, what I observed, what changed. When my boot times stayed stubbornly slow despite everything I'd tried, I searched my vault for the laptop's name, copied the whole thread of notes, and dropped them into a conversation with an LLM. Instead of starting from scratch, I was starting from a complete record of where I'd already been. The LLM could skip past the things I'd already ruled out and spitball with me about what was left. We landed on the answer quickly: LUKS 1 encryption decrypting in software on every boot, rather than using the hardware acceleration my CPU supported. Upgrading to LUKS 2 and binding the key to the hardware rather than prompting for a software password on every decrypt fixed it permanently.

Without the notes, I would not have had a useful conversation. The LLM would have suggested the same things I'd already tried, and I would have had no way to tell it otherwise.

That's the cost of treating learning as consumption: read a book, work a problem, close the tab, fix the bug, move on. A year later it's gone — not because you're forgetful, but because you never externalized the thinking in a way that connects to anything else.

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

The daily journal as the capture point is the key design choice: it removes the friction of "where does this go." It goes in today's journal. Later, you link it somewhere permanent if it deserves to live past the week. If you want to start without thinking about structure, start with Logseq.

### Obsidian

[Obsidian](https://obsidian.md/) has a larger plugin ecosystem, a stronger community specifically around Zettelkasten, and a more polished graph view. It's also local-first and Markdown-based. The tradeoff: Obsidian gives you a blank canvas, which means you'll spend more time deciding on structure upfront. That's the right call if you already know roughly how you want to organize your notes, or if you want fine-grained control over how your vault grows.

**Deciding rule**: if you've never done this before and want to start immediately, use Logseq — the journal gives you a default workflow for free. If you've tried journaling tools and found they didn't stick, or you want a plugin ecosystem and are willing to configure your own system, use Obsidian.

---

## Syncing Across Devices: Stelekit

Six years into using Logseq, the Android app became unusable for me. Cold boot: over 20 seconds before I could write anything. If the app got backgrounded and Android reclaimed its memory, I'd come back to another full load. The cause was architectural — the non-database version of Logseq loaded every journal file into memory on startup. Six years of daily notes is a lot of journal files.

I looked into contributing a fix. Logseq's mobile app is written in ClojureScript, and after spending time with it I decided that wasn't the path I wanted to take. Instead I used LLMs to help me build [Stelekit](https://github.com/tstapler/stelekit) — a Logseq-compatible rewrite in Kotlin with Compose Multiplatform. The goal was straightforward: fast startup, lazy loading, and a codebase I could actually reason about across Android, desktop, and anything else I wanted to target later.

The sync problem came along for the ride. Logseq's vault is plain Markdown on disk, but notes modified on two machines produce merge conflicts that git can't resolve cleanly on its own. Stelekit handles the conflict patterns Logseq actually produces, keeps everything in version control, and doesn't require a subscription or a third-party cloud. If you're running Logseq and hitting the same performance wall on mobile — or just want sync that you control — it's worth a look.

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

The failure mode isn't starting — it's the week three drop-off when you're busy and it feels like overhead. The fix is to make the bar low enough that there's no excuse: one note, one link, three minutes. If a week goes by without any notes, the practice hasn't failed — just open the journal and write one thing. The archive doesn't expire. The connections you made in month one are still there in month twelve, and they're worth more then than they were when you wrote them.
