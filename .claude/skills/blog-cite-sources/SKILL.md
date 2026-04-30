---
name: blog-cite-sources
description: Research citable sources for blog post claims and produce a BibTeX bibliography file co-located with the post. Use when a blog post needs citations added, a .bib file needs to be created or expanded, or when researching authoritative references for technical claims. The .bib file is Zotero-importable and uses the annote field for research notes.
---

# Blog Cite Sources

Research authoritative sources for claims in a blog post and produce a BibTeX `.bib` file co-located with the post.

## When to Use

- A blog post makes technical claims that need citations
- A `.bib` file needs to be created or expanded for a post
- Researching primary sources (specs, RFCs, official docs, seminal papers) for accuracy

## Workflow

### 1. Read the post

Read the target post file. Identify claims that should be cited:
- Statistics or benchmarks
- Historical facts ("X was introduced in version Y")
- Design decisions attributed to a project or person
- Technical behavior described as fact
- References to external work (papers, posts, specs)

### 2. Research each claim

For each citable claim, search for the **most authoritative source**:
- Prefer: official docs, specs (PEPs, JEPs, RFCs), original papers, primary blog posts from authors
- Avoid: secondary summaries, Stack Overflow, Medium reposts

Use WebSearch to find and verify sources. Record the URL, publication date, and key facts.

### 3. Write the .bib file

Place the file at: `content/blog/<post-slug>/<post-slug>.bib`

Use standard BibTeX entry types:
- `@misc` — blog posts, web pages, documentation
- `@techreport` — PEPs, JEPs, RFCs, technical specs
- `@article` — journal/conference papers
- `@book` — books

**Required fields for all entries**:
- `url` — direct link to the source
- `urldate` — date accessed (ISO 8601: `{YYYY-MM-DD}`)
- `annote` — research notes (see below)

**annote field format** (this imports as an item note in Zotero):
```
annote = {1-3 sentence summary of what this source says and why it matters
          for the specific claim being cited. Note any caveats, date sensitivity,
          or contradictions with other sources.}
```

### 4. Return citation suggestions

After writing the `.bib` file, return a list of Hugo shortcode suggestions for each claim:

```
Claim: "Python's asyncio arrived in 3.4"
Key: pep3156asyncio
Shortcode: {{</* cite "pep3156asyncio" */>}}
Insert after: "...before `asyncio` arrived in 3.4."
```

## BibTeX Key Convention

`<lastname><year><topic>` — all lowercase, no spaces:
- `nystrom2015color`
- `pep3156asyncio`
- `jep444virtualthreads`

## Hugo Integration

The post's front matter must include:
```toml
bibliography = "<post-slug>.bib"
```

Inline citations use:
```
{{</* cite "key" */>}}
```

The bibliography section at the end of the post:
```
{{</* bibliography file="<post-slug>.bib" */>}}
```

## Zotero Import

To import the `.bib` file into Zotero:
1. `File → Import`
2. Select the `.bib` file
3. Annote fields import as item notes
