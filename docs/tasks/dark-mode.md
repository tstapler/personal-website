# Feature Plan: Dark Mode Implementation

## Epic Overview

**User Value**
Implement dark mode support for the site so visitors whose OS is configured for dark
preference get a comfortable reading experience without eye strain. The espouse theme
submodule already has all site colors extracted into CSS custom properties in
`themes/espouse/static/site-enhancements.css` (`:root { --color-primary, --toc-bg,
--feed-border, --meta-color, --summary-color, ... }`). The foundation is in place; dark
mode is purely an additive `@media (prefers-color-scheme: dark)` block overriding those
tokens.

**Success Metrics**
- Visitors with `prefers-color-scheme: dark` see inverted palette automatically
- No new JavaScript required — pure CSS media query
- All token-driven UI surfaces (nav, TOC, feed, cards, code blocks) respect dark values
- Light mode is pixel-identical to current state

**Scope**
- Included: dark-mode token overrides in `site-enhancements.css`, verification pass
  against rendered pages
- Excluded: manual theme toggle/switch (deferred), Pagefind search widget re-theming
  (follow-on task)

---

## Story Breakdown

### Story 1: Dark Token Override Block (1-2 hours)

**User Value**: Automatically presents correct contrast ratios under dark OS preference.

**Acceptance Criteria**:
- `@media (prefers-color-scheme: dark)` block added to `site-enhancements.css`
- All 12 `:root` tokens have dark-mode counterparts
- `hugo serve` shows correct dark palette when browser DevTools overrides color scheme

---

## Atomic Tasks

### Task 1.1: Add Dark-Mode Token Overrides to site-enhancements.css (2h)

**Scope**: Add `@media (prefers-color-scheme: dark)` block overriding all 12 tokens
currently defined in the `:root` block.

**Files** (2 files):
- `themes/espouse/static/site-enhancements.css` (modify — add ~20 lines at end)
- No other file requires changes; the rest of the CSS references `var(--token)` already

**Context**:
- The espouse submodule is a git submodule at `themes/espouse/`; changes must be
  committed there and then the parent repo's submodule pointer updated
- Existing tokens (light values):
  - `--color-primary: #1a6fad`
  - `--color-primary-dark: #155d96`
  - `--color-link: #4183C4`
  - `--color-success: #21ba45`
  - `--toc-bg: #f9fafb`
  - `--toc-border: #e2e8f0`
  - `--toc-label: #555`
  - `--tag-bg: #eef4fb`
  - `--anchor-color: #999`
  - `--feed-border: #e8e8e8`
  - `--meta-color: #888`
  - `--summary-color: #555`
- Suggested dark values (adjust visually):
  - `--color-primary: #5ba8e5`
  - `--color-primary-dark: #4a97d4`
  - `--color-link: #79b8f3`
  - `--color-success: #3dd68c`
  - `--toc-bg: #1e2530`
  - `--toc-border: #2e3a48`
  - `--toc-label: #a0aab4`
  - `--tag-bg: #1a2535`
  - `--anchor-color: #6b7280`
  - `--feed-border: #2e3a48`
  - `--meta-color: #9ca3af`
  - `--summary-color: #9ca3af`
- The `all.css` (Semantic UI bundle) uses hardcoded colors and is NOT token-driven;
  dark mode will only affect the token-driven surfaces. Full Semantic UI dark theming
  is out of scope for this task.

**Implementation**:
```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-primary:      #5ba8e5;
    --color-primary-dark: #4a97d4;
    --color-link:         #79b8f3;
    --color-success:      #3dd68c;
    --toc-bg:             #1e2530;
    --toc-border:         #2e3a48;
    --toc-label:          #a0aab4;
    --tag-bg:             #1a2535;
    --anchor-color:       #6b7280;
    --feed-border:        #2e3a48;
    --meta-color:         #9ca3af;
    --summary-color:      #9ca3af;
  }
}
```

**Success Criteria**:
- Open DevTools > Rendering > Emulate CSS media feature `prefers-color-scheme: dark`
- Blog feed items show lighter text against dark background via token changes
- TOC sidebar changes background color
- Tag pills change background
- Reading progress bar and focus outlines use the adjusted primary color
- Light mode (no override) is pixel-identical to current

**Testing**: `hugo serve -D` then DevTools media emulation

**Dependencies**: None

**Status**: Pending

---

### Task 1.2: Bump Espouse Submodule Pointer in Parent Repo (0.5h)

**Scope**: After Task 1.1 is committed to the espouse submodule, update the parent
repo's submodule reference to point at the new commit.

**Files** (1 file):
- `themes/espouse` (submodule pointer update — `git add themes/espouse`)

**Context**:
- Espouse is a submodule pointing at `github.com/tstapler/espouse`
- Pattern from prior work: commit to espouse, then from the parent repo run
  `git add themes/espouse` and commit with a message like
  "chore: update espouse submodule with dark mode token overrides"

**Success Criteria**:
- `git submodule status` shows the new SHA for `themes/espouse`
- CI build passes with the updated submodule

**Testing**: `bazel build //:site` or `hugo serve` confirms site builds against new SHA

**Dependencies**: Task 1.1

**Status**: Pending

---

## Dependency Visualization

```
Task 1.1: Add dark-mode token overrides (2h)
    |
    v
Task 1.2: Update submodule pointer in parent repo (0.5h)
    |
    v
Done — dark mode ships on next Cloudflare Pages deploy
```

Total estimated effort: 2.5 hours

---

## Context Preparation Notes

- Read `themes/espouse/static/site-enhancements.css` (242 lines) to see full token list
- Run `hugo serve -D --baseURL http://localhost` for live preview
- Use Chrome DevTools > Rendering > "Emulate CSS media feature" for dark mode testing
- The espouse submodule remote is `github.com/tstapler/espouse` (fork by Tyler Stapler)
- Commit to espouse first, then update pointer in parent; never commit parent without
  bumping the submodule SHA

## Known Limitations / Follow-On Work

- Semantic UI `all.css` uses hardcoded colors — background, text, card surfaces from
  Semantic will not invert. A full dark Semantic UI theme would require either a Fomantic
  dark theme build or a CSS filter hack (`invert(1) hue-rotate(180deg)`) — out of scope.
- Pagefind search widget has its own CSS variables; may need separate token overrides
- A manual theme toggle (button) could be added later as a non-breaking enhancement
  building on this foundation

## Links

- Token source: `themes/espouse/static/site-enhancements.css` (`:root` block, lines 1-14)
- Parent TODO: `/home/tstapler/Programming/personal-website/TODO.md`
- Related closed task: `docs/tasks/web-improvements.md` (UX improvements now done)
