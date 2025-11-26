#!/usr/bin/env python3
"""
PurgeCSS Pruning Script

Removes unused CSS selectors while preserving safelisted patterns.
Uses analysis data to generate optimized CSS files.
"""

import re
import sys
import json
from pathlib import Path


def load_analysis(analysis_file):
    """Load analysis results from JSON file."""
    with open(analysis_file) as f:
        return json.load(f)


def extract_html_classes_and_ids(html_content):
    """Extract all class names and IDs from HTML content."""
    classes = set()
    ids = set()

    # Find class attributes
    class_pattern = r'class=["\']([\w\s\-_]+)["\']'
    for match in re.finditer(class_pattern, html_content):
        classes.update(match.group(1).split())

    # Find id attributes
    id_pattern = r'id=["\']([\w\-_]+)["\']'
    for match in re.finditer(id_pattern, html_content):
        ids.add(match.group(1))

    return classes, ids


def is_safelisted(selector, safelist_patterns):
    """Check if selector matches any safelist pattern."""
    # Remove leading . or # for pattern matching
    clean_selector = selector.lstrip('.#').split(':')[0].split('[')[0]

    for pattern in safelist_patterns:
        if re.match(pattern, clean_selector):
            return True
    return False


def prune_css(css_content, used_classes, used_ids, safelist_patterns):
    """
    Remove unused CSS rules while preserving structure and comments.
    Returns pruned CSS and statistics.
    """
    original_size = len(css_content)

    # Extract all CSS rules (simplified parser)
    # Pattern: selector(s) { ... }
    rule_pattern = r'([^{}]+)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'

    pruned_rules = []
    removed_count = 0
    kept_count = 0

    for match in re.finditer(rule_pattern, css_content):
        selectors_str = match.group(1).strip()
        declarations = match.group(2).strip()

        # Split multiple selectors (comma-separated)
        selectors = [s.strip() for s in selectors_str.split(',')]

        # Check if any selector is used
        keep_rule = False
        for selector in selectors:
            # Skip @-rules, keep them all
            if selector.startswith('@'):
                keep_rule = True
                break

            # Check if selector is used
            if selector.startswith('.'):
                class_name = selector[1:].split(':')[0].split('[')[0]
                if class_name in used_classes or is_safelisted(selector, safelist_patterns):
                    keep_rule = True
                    break
            elif selector.startswith('#'):
                id_name = selector[1:].split(':')[0].split('[')[0]
                if id_name in used_ids or is_safelisted(selector, safelist_patterns):
                    keep_rule = True
                    break
            else:
                # Element selectors, pseudo-elements - keep them
                keep_rule = True
                break

        if keep_rule:
            pruned_rules.append(f"{selectors_str} {{\n  {declarations}\n}}")
            kept_count += 1
        else:
            removed_count += 1

    # Reconstruct CSS
    pruned_css = '\n\n'.join(pruned_rules)

    # Preserve important comments (license, attribution)
    license_pattern = r'/\*!.*?\*/'
    licenses = re.findall(license_pattern, css_content, flags=re.DOTALL)
    if licenses:
        pruned_css = '\n'.join(licenses) + '\n\n' + pruned_css

    pruned_size = len(pruned_css)
    reduction_percentage = ((original_size - pruned_size) / original_size * 100) if original_size > 0 else 0

    stats = {
        'original_size': original_size,
        'pruned_size': pruned_size,
        'reduction_bytes': original_size - pruned_size,
        'reduction_percentage': reduction_percentage,
        'rules_kept': kept_count,
        'rules_removed': removed_count,
    }

    return pruned_css, stats


def collect_used_selectors(site_dir):
    """Scan site HTML to collect all used classes and IDs."""
    site_path = Path(site_dir)

    all_classes = set()
    all_ids = set()

    for html_file in site_path.rglob('*.html'):
        try:
            content = html_file.read_text(encoding='utf-8')
            classes, ids = extract_html_classes_and_ids(content)
            all_classes.update(classes)
            all_ids.update(ids)
        except Exception as e:
            print(f"Warning: Could not read {html_file}: {e}", file=sys.stderr)

    return all_classes, all_ids


def main():
    if len(sys.argv) < 4:
        print("Usage: prune.py <site_directory> <css_input_file> <css_output_file>", file=sys.stderr)
        sys.exit(1)

    site_dir = sys.argv[1]
    css_input = sys.argv[2]
    css_output = sys.argv[3]

    # Load safelist patterns
    safelist_patterns = [
        r'^is-.*',
        r'^has-.*',
        r'^active$',
        r'^nav-.*',
        r'^menu-.*',
        r'^ui-.*',
        r'^semantic-.*',
    ]

    print("=" * 60)
    print("PurgeCSS Pruning")
    print("=" * 60)

    # Collect used selectors
    print(f"Scanning site: {site_dir}")
    used_classes, used_ids = collect_used_selectors(site_dir)
    print(f"Found {len(used_classes)} used classes and {len(used_ids)} used IDs")

    # Read CSS
    print(f"Reading CSS: {css_input}")
    css_content = Path(css_input).read_text(encoding='utf-8')
    print(f"Original size: {len(css_content):,} bytes ({len(css_content)/1024:.1f} KB)")

    # Prune CSS
    print("Pruning unused CSS...")
    pruned_css, stats = prune_css(css_content, used_classes, used_ids, safelist_patterns)

    # Write output
    print(f"Writing pruned CSS: {css_output}")
    Path(css_output).write_text(pruned_css, encoding='utf-8')

    print("\n📊 Results:")
    print(f"  Original size: {stats['original_size']:,} bytes ({stats['original_size']/1024:.1f} KB)")
    print(f"  Pruned size: {stats['pruned_size']:,} bytes ({stats['pruned_size']/1024:.1f} KB)")
    print(f"  Reduction: {stats['reduction_bytes']:,} bytes ({stats['reduction_percentage']:.1f}%)")
    print(f"  Rules kept: {stats['rules_kept']}")
    print(f"  Rules removed: {stats['rules_removed']}")

    print(f"\n✅ Pruned CSS saved to: {css_output}")


if __name__ == '__main__':
    main()
