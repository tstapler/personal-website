#!/usr/bin/env python3
"""
PurgeCSS Analysis Script

Analyzes Hugo site output to identify used vs unused CSS selectors.
Generates report and safelist for dynamic classes.
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
import json


def extract_html_classes_and_ids(html_content):
    """Extract all class names and IDs from HTML content."""
    classes = set()
    ids = set()

    # Find class attributes: class="foo bar baz"
    class_pattern = r'class=["\']([\w\s\-_]+)["\']'
    for match in re.finditer(class_pattern, html_content):
        classes.update(match.group(1).split())

    # Find id attributes: id="foo"
    id_pattern = r'id=["\']([\w\-_]+)["\']'
    for match in re.finditer(id_pattern, html_content):
        ids.add(match.group(1))

    return classes, ids


def extract_css_selectors(css_content):
    """Extract CSS selectors from CSS content."""
    selectors = set()

    # Remove comments
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)

    # Extract selectors (simple approach - matches most common patterns)
    # Matches: .class, #id, element, .class:hover, etc.
    selector_pattern = r'([.#]?[\w\-_]+(?::[\w\-_]+)?(?:\[[\w\-_="]+\])?)\s*[,{]'

    for match in re.finditer(selector_pattern, css_content):
        selector = match.group(1).strip()
        if selector and not selector.startswith('@'):
            selectors.add(selector)

    return selectors


def analyze_site(site_dir):
    """Analyze site directory and return usage statistics."""
    site_path = Path(site_dir)

    # Collect all used classes and IDs from HTML
    all_classes = set()
    all_ids = set()
    html_files = list(site_path.rglob('*.html'))

    print(f"Analyzing {len(html_files)} HTML files...")
    for html_file in html_files:
        try:
            content = html_file.read_text(encoding='utf-8')
            classes, ids = extract_html_classes_and_ids(content)
            all_classes.update(classes)
            all_ids.update(ids)
        except Exception as e:
            print(f"Warning: Could not read {html_file}: {e}", file=sys.stderr)

    print(f"Found {len(all_classes)} unique classes and {len(all_ids)} unique IDs")

    # Collect all CSS selectors
    all_selectors = set()
    css_files = list(site_path.rglob('*.css'))

    print(f"Analyzing {len(css_files)} CSS files...")
    total_css_size = 0

    for css_file in css_files:
        try:
            content = css_file.read_text(encoding='utf-8')
            selectors = extract_css_selectors(content)
            all_selectors.update(selectors)
            total_css_size += len(content)
        except Exception as e:
            print(f"Warning: Could not read {css_file}: {e}", file=sys.stderr)

    print(f"Found {len(all_selectors)} CSS selectors")
    print(f"Total CSS size: {total_css_size:,} bytes ({total_css_size/1024:.1f} KB)")

    # Analyze usage
    used_selectors = set()
    unused_selectors = set()

    for selector in all_selectors:
        # Check if selector matches any used class or ID
        is_used = False

        if selector.startswith('.'):
            # Class selector
            class_name = selector[1:].split(':')[0].split('[')[0]
            if class_name in all_classes:
                is_used = True
        elif selector.startswith('#'):
            # ID selector
            id_name = selector[1:].split(':')[0].split('[')[0]
            if id_name in all_ids:
                is_used = True
        else:
            # Element selector or pseudo-selector - assume used
            is_used = True

        if is_used:
            used_selectors.add(selector)
        else:
            unused_selectors.add(selector)

    # Generate dynamic class safelist patterns
    safelist_patterns = [
        r'^is-.*',      # State classes
        r'^has-.*',     # State classes
        r'^active$',    # Common state
        r'^nav-.*',     # Navigation classes
        r'^menu-.*',    # Menu classes
        r'^ui-.*',      # UI framework classes
        r'^semantic-.*', # Semantic UI classes
    ]

    # Calculate statistics
    used_count = len(used_selectors)
    unused_count = len(unused_selectors)
    total_count = used_count + unused_count
    unused_percentage = (unused_count / total_count * 100) if total_count > 0 else 0

    return {
        'html_files': len(html_files),
        'css_files': len(css_files),
        'total_css_size': total_css_size,
        'total_css_kb': total_css_size / 1024,
        'classes_found': len(all_classes),
        'ids_found': len(all_ids),
        'total_selectors': total_count,
        'used_selectors': used_count,
        'unused_selectors': unused_count,
        'unused_percentage': unused_percentage,
        'safelist_patterns': safelist_patterns,
        'sample_unused': sorted(list(unused_selectors))[:20],
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze.py <site_directory>", file=sys.stderr)
        sys.exit(1)

    site_dir = sys.argv[1]

    if not Path(site_dir).exists():
        print(f"Error: Directory {site_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("PurgeCSS Analysis Report")
    print("=" * 60)

    stats = analyze_site(site_dir)

    print("\n📊 Statistics:")
    print(f"  HTML files analyzed: {stats['html_files']}")
    print(f"  CSS files analyzed: {stats['css_files']}")
    print(f"  Total CSS size: {stats['total_css_kb']:.1f} KB")
    print(f"  Classes found in HTML: {stats['classes_found']}")
    print(f"  IDs found in HTML: {stats['ids_found']}")
    print(f"  Total CSS selectors: {stats['total_selectors']}")
    print(f"  Used selectors: {stats['used_selectors']}")
    print(f"  Unused selectors: {stats['unused_selectors']}")
    print(f"  Unused percentage: {stats['unused_percentage']:.1f}%")

    if stats['unused_percentage'] > 30:
        potential_savings = stats['total_css_kb'] * (stats['unused_percentage'] / 100)
        print(f"\n💡 Potential savings: ~{potential_savings:.1f} KB ({stats['unused_percentage']:.0f}% reduction)")

    print("\n🔒 Safelist patterns (for dynamic classes):")
    for pattern in stats['safelist_patterns']:
        print(f"  {pattern}")

    print("\n📝 Sample unused selectors (first 20):")
    for selector in stats['sample_unused']:
        print(f"  {selector}")

    # Output JSON for programmatic use
    output_file = Path("purgecss_analysis.json")
    with output_file.open('w') as f:
        json.dump(stats, f, indent=2)
    print(f"\n✅ Full report saved to: {output_file}")


if __name__ == '__main__':
    main()
