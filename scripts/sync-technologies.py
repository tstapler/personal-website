#!/usr/bin/env python3
"""
Regenerates data/technologies.yaml from three sources:
  - Blog post frontmatter tags (content/blog/**/index.md)
  - GitHub API (public repos via `gh` CLI — paginated, includes topics)
  - Personal wiki (~/Documents/personal-wiki/logseq/pages/)

Run from the repo root:
    python3 scripts/sync-technologies.py
"""

import re
import json
import subprocess
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent
CONTENT_DIR = REPO_ROOT / "content" / "blog"
WIKI_PAGES = Path.home() / "Documents" / "personal-wiki" / "logseq" / "pages"
DATA_OUT = REPO_ROOT / "data" / "technologies.yaml"

TECH_CATALOG = [
    dict(name="Kubernetes",  slug="kubernetes",   icon="img/tech-logos/kubernetes.svg",       category="Infrastructure",
         blog_tags=["kubernetes","kubeadm","kubespray","gke"],
         github_langs=[], github_topics=["kubernetes"]),
    dict(name="Python",      slug="python",       icon="img/tech-logos/python-logo-notext.svg", category="Languages",
         blog_tags=["python"],
         github_langs=["Python"], github_topics=["python"]),
    dict(name="Go",          slug="go",           icon="img/tech-logos/gopher.svg",            category="Languages",
         blog_tags=["golang","go"],
         github_langs=["Go"], github_topics=["golang","go"]),
    dict(name="Ansible",     slug="ansible",      icon="img/tech-logos/ansible.svg",           category="Infrastructure",
         blog_tags=["ansible"],
         github_langs=[], github_topics=["ansible"]),
    dict(name="Rust",        slug="rust",         icon="img/tech-logos/rust.svg",              category="Languages",
         blog_tags=["rust"],
         github_langs=["Rust"], github_topics=["rust"]),
    dict(name="Kotlin",      slug="kotlin",       icon="img/tech-logos/kotlin.svg",            category="Languages",
         blog_tags=["kotlin","coroutines"],
         github_langs=["Kotlin"], github_topics=["kotlin"]),
    dict(name="TypeScript",  slug="typescript",   icon="img/tech-logos/typescript.svg",        category="Languages",
         blog_tags=["typescript"],
         github_langs=["TypeScript"], github_topics=["typescript"]),
    dict(name="Java",        slug="java",         icon="img/tech-logos/java.svg",              category="Languages",
         blog_tags=["java","jvm","virtual-threads","project-loom","reactor"],
         github_langs=["Java"], github_topics=["java"]),
    dict(name="PostgreSQL",  slug="postgresql",   icon="img/tech-logos/postgresql.svg",        category="Databases",
         blog_tags=["postgres","postgresql","pgbouncer"],
         github_langs=[], github_topics=["postgres","postgresql"]),
    dict(name="Spring Boot", slug="spring-boot",  icon="img/tech-logos/spring.svg",            category="Frameworks",
         blog_tags=["spring-boot","spring"],
         github_langs=[], github_topics=["spring-boot"]),
    dict(name="AWS",         slug="aws",          icon="img/tech-logos/aws.svg",               category="Cloud",
         blog_tags=["aws","s3","ec2","eks","rds","cloudwatch"],
         github_langs=[], github_topics=["aws"]),
    dict(name="GCP",         slug="gcp",          icon="img/tech-logos/gcp.svg",               category="Cloud",
         blog_tags=["gcp","gke","google-cloud"],
         github_langs=[], github_topics=["gcp","google-cloud"]),
    dict(name="Terraform",   slug="terraform",    icon="img/tech-logos/terraform.svg",         category="Infrastructure",
         blog_tags=["terraform"],
         github_langs=[], github_topics=["terraform"]),
    dict(name="Ceph",        slug="ceph",         icon="img/tech-logos/ceph.svg",              category="Infrastructure",
         blog_tags=["ceph","storage-cluster"],
         github_langs=[], github_topics=["ceph"]),
    dict(name="Linux",       slug="linux",        icon="img/tech-logos/linux.svg",             category="Infrastructure",
         blog_tags=["linux","kernel"],
         github_langs=[], github_topics=["linux"]),
    dict(name="Hugo",        slug="hugo",         icon="img/tech-logos/hugo.svg",              category="Frameworks",
         blog_tags=["hugo"],
         github_langs=[], github_topics=["hugo"]),
    dict(name="Anthropic",   slug="anthropic",    icon="img/tech-logos/anthropic.svg",         category="AI",
         blog_tags=["claude","ai","llm","anthropic"],
         github_langs=[], github_topics=["claude","llm","ai"]),
]


def get_blog_tag_counts() -> dict[str, int]:
    """Count how many blog posts mention each tag."""
    counts: dict[str, int] = defaultdict(int)
    for md in CONTENT_DIR.rglob("*.md"):
        text = md.read_text(errors="replace")
        m = re.search(r'tags\s*[=:]\s*\[([^\]]*)\]', text, re.IGNORECASE)
        if m:
            raw = m.group(1)
            tags = [t.strip().strip('"\'') for t in raw.split(',') if t.strip()]
            for tag in tags:
                counts[tag.lower()] += 1
    return counts


def get_github_username() -> str:
    try:
        return subprocess.check_output(
            ["gh", "api", "user", "--jq", ".login"], text=True
        ).strip()
    except Exception:
        return ""


def get_github_data() -> tuple[set[str], set[str]]:
    """Return (languages, topics) across all user repos via gh CLI (paginated, single call)."""
    username = get_github_username()
    if not username:
        print("  ⚠  Could not resolve GitHub username — skipping GitHub")
        return set(), set()

    try:
        raw = subprocess.check_output(
            [
                "gh", "repo", "list", username,
                "--limit", "200",
                "--json", "name,primaryLanguage,repositoryTopics",
            ],
            text=True,
        )
        repos = json.loads(raw)
    except Exception as e:
        print(f"  ⚠  gh repo list failed: {e}")
        return set(), set()

    languages: set[str] = set()
    topics: set[str] = set()
    for repo in repos:
        if lang := (repo.get("primaryLanguage") or {}).get("name"):
            languages.add(lang)
        for t in repo.get("repositoryTopics") or []:
            if name := t.get("name"):
                topics.add(name)

    return languages, topics


def get_wiki_page_names() -> set[str]:
    """Return exact lowercased stems of all Logseq page files."""
    if not WIKI_PAGES.exists():
        print("  ⚠  Wiki not found at", WIKI_PAGES)
        return set()
    return {p.stem.lower() for p in WIKI_PAGES.glob("*.md")}


def build_entry(tech: dict, blog_counts: dict, gh_langs: set, gh_topics: set, wiki_names: set) -> dict:
    blog_count = sum(blog_counts.get(t, 0) for t in tech["blog_tags"])
    github = (
        any(l in gh_langs for l in tech["github_langs"])
        or any(t in gh_topics for t in tech["github_topics"])
    )
    # Exact match against page stem — avoids "go" matching "ongoing", etc.
    slug_lower = tech["slug"].lower()
    name_lower = tech["name"].lower()
    wiki = any(n == slug_lower or n == name_lower for n in wiki_names)
    return {
        "name": tech["name"],
        "slug": tech["slug"],
        "icon_url": tech["icon"],
        "category": tech["category"],
        "blog_count": blog_count,
        "github": github,
        "wiki": wiki,
    }


def entry_to_yaml(e: dict) -> str:
    return (
        f"  - name: {e['name']}\n"
        f"    slug: {e['slug']}\n"
        f"    icon_url: {e['icon_url']}\n"
        f"    category: {e['category']}\n"
        f"    blog_count: {e['blog_count']}\n"
        f"    github: {'true' if e['github'] else 'false'}\n"
        f"    wiki: {'true' if e['wiki'] else 'false'}\n"
    )


def main():
    import datetime
    today = datetime.date.today().isoformat()

    print("📚 Reading blog tags...")
    blog_counts = get_blog_tag_counts()
    print(f"   {sum(blog_counts.values())} tag occurrences across {len(blog_counts)} unique tags")

    print("🐙 Fetching GitHub data...")
    gh_langs, gh_topics = get_github_data()
    print(f"   {len(gh_langs)} languages, {len(gh_topics)} topics")

    print("📓 Scanning wiki pages...")
    wiki_names = get_wiki_page_names()
    print(f"   {len(wiki_names)} pages")

    entries = [build_entry(t, blog_counts, gh_langs, gh_topics, wiki_names) for t in TECH_CATALOG]
    entries.sort(key=lambda e: (-e["blog_count"], e["name"].lower()))

    lines = [
        f"# Auto-generated by scripts/sync-technologies.py\n",
        f"# Sources: blog post tags, GitHub repos, personal wiki\n",
        f"# Last updated: {today}\n",
        f"technologies:\n",
    ]
    for e in entries:
        lines.append(entry_to_yaml(e))

    DATA_OUT.write_text("".join(lines))
    print(f"\n✅ Wrote {len(entries)} technologies to {DATA_OUT.relative_to(REPO_ROOT)}")
    for e in entries:
        srcs = []
        if e["blog_count"]: srcs.append(f"{e['blog_count']} posts")
        if e["github"]: srcs.append("github")
        if e["wiki"]: srcs.append("wiki")
        print(f"   {e['name']:<15} ({', '.join(srcs) or 'catalog only'})")


if __name__ == "__main__":
    main()
