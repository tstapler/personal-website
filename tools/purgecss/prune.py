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


def extract_tokens(content):
    """Extract all potential class/id tokens from content using broad regex."""
    # Broad match for any potential selector name (User provided nuanced regex)
    # Matches tokens that don't end in a colon (to avoid CSS properties/JS keys)
    pattern = r'[^<>"\'`\s]*[^<>"\'`\s:]'
    return set(re.findall(pattern, content))


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

            # Algorithm:
            # 1. Clean selector of pseudos/attributes
            # 2. Regex find all classes and IDs
            # 3. Check if ALL found classes/IDs are used or safelisted
            
            # Remove attributes [type="..."] to avoid matching inside them
            clean_selector = re.sub(r'\[.*?\]', '', selector)
            # Remove pseudo-classes/elements :hover, ::before
            clean_selector = clean_selector.split(':')[0]

            # Find all classes and IDs
            found_classes = re.findall(r'\.([a-zA-Z0-9_-]+)', clean_selector)
            found_ids = re.findall(r'#([a-zA-Z0-9_-]+)', clean_selector)

            # Verify classes
            classes_ok = True
            for cls in found_classes:
                if cls not in used_classes and not is_safelisted(cls, safelist_patterns):
                    classes_ok = False
                    break
            
            # Verify IDs
            ids_ok = True
            for id_val in found_ids:
                if id_val not in used_ids and not is_safelisted(id_val, safelist_patterns):
                    ids_ok = False
                    break

            # If all parts of the selector are valid, keep the rule
            # Note: If no classes/IDs found (e.g. "div", "body"), both flags remain True
            if classes_ok and ids_ok:
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
    """Scan site HTML and JS to collect all used classes and IDs."""
    site_path = Path(site_dir)

    all_classes = set()
    all_ids = set()

    # Scan both HTML and JS files
    extensions = ['*.html', '*.js']
    
    for ext in extensions:
        for file_path in site_path.rglob(ext):
            try:
                content = file_path.read_text(encoding='utf-8')
                tokens = extract_tokens(content)
                
                # Add all tokens to both classes and IDs sets
                # This is the "nuanced" approach: treat every token as potentially both
                all_classes.update(tokens)
                all_ids.update(tokens)
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)

    return all_classes, all_ids


def main():
    if len(sys.argv) < 4:
        print("Usage: prune.py <site_directory> <css_input_file> <css_output_file>", file=sys.stderr)
        sys.exit(1)

    site_dir = sys.argv[1]
    css_input = sys.argv[2]
    css_output = sys.argv[3]

    # Load safelist patterns - comprehensive Semantic UI support
    safelist_patterns = [
        # Generic state classes
        r'^is-.*',
        r'^has-.*',
        r'^active$',
        r'^disabled$',
        r'^nav-.*',

        # Semantic UI base components
        r'^ui$',
        r'^button$',
        r'^buttons$',
        r'^menu$',
        r'^dropdown$',
        r'^modal$',
        r'^segment$',
        r'^segments$',
        r'^card$',
        r'^cards$',
        r'^form$',
        r'^input$',
        r'^label$',
        r'^labels$',
        r'^labeled$',
        r'^message$',
        r'^messages$',
        r'^icon$',
        r'^icons$',
        r'^image$',
        r'^images$',
        r'^container$',
        r'^grid$',
        r'^column$',
        r'^row$',
        r'^header$',
        r'^divider$',
        r'^list$',
        r'^item$',
        r'^items$',
        r'^content$',
        r'^description$',
        r'^meta$',
        r'^extra$',
        r'^field$',
        r'^fields$',
        r'^accordion$',
        r'^checkbox$',
        r'^dimmer$',
        r'^embed$',
        r'^progress$',
        r'^rating$',
        r'^search$',
        r'^sidebar$',
        r'^pushable$',
        r'^pusher$',
        r'^dimmed$',
        r'^blurring$',
        r'^scrolling$',
        r'^sticky$',
        r'^tab$',
        r'^transition$',
        r'^popup$',
        r'^toast$',

        # Semantic UI size modifiers
        r'^mini$',
        r'^tiny$',
        r'^small$',
        r'^medium$',
        r'^large$',
        r'^big$',
        r'^huge$',
        r'^massive$',

        # Semantic UI color modifiers
        r'^red$',
        r'^orange$',
        r'^yellow$',
        r'^olive$',
        r'^green$',
        r'^teal$',
        r'^blue$',
        r'^violet$',
        r'^purple$',
        r'^pink$',
        r'^brown$',
        r'^grey$',
        r'^gray$',
        r'^black$',
        r'^white$',
        r'^primary$',
        r'^secondary$',
        r'^positive$',
        r'^negative$',

        # Semantic UI state modifiers
        r'^loading$',
        r'^hidden$',
        r'^visible$',
        r'^error$',
        r'^warning$',
        r'^success$',
        r'^info$',
        r'^animating$',
        r'^transition$',
        r'^hoverable$',
        r'^selected$',
        r'^read$',
        r'^unread$',

        # Semantic UI alignment & positioning
        r'^left$',
        r'^center$',
        r'^right$',
        r'^justified$',
        r'^top$',
        r'^middle$',
        r'^bottom$',
        r'^floated$',
        r'^aligned$',
        r'^attached$',

        # Semantic UI layout modifiers
        r'^fluid$',
        r'^fitted$',
        r'^padded$',
        r'^compact$',
        r'^relaxed$',
        r'^divided$',
        r'^celled$',
        r'^inverted$',
        r'^basic$',
        r'^clearing$',
        r'^stackable$',
        r'^doubling$',
        r'^stretched$',
        r'^equal$',

        # Semantic UI width classes (grid system)
        r'^wide$',
        r'^one$',
        r'^two$',
        r'^three$',
        r'^four$',
        r'^five$',
        r'^six$',
        r'^seven$',
        r'^eight$',
        r'^nine$',
        r'^ten$',
        r'^eleven$',
        r'^twelve$',
        r'^thirteen$',
        r'^fourteen$',
        r'^fifteen$',
        r'^sixteen$',

        # Semantic UI orientation & direction
        r'^vertical$',
        r'^horizontal$',
        r'^pointing$',
        r'^inline$',
        r'^block$',

        # Semantic UI image modifiers
        r'^avatar$',
        r'^bordered$',
        r'^circular$',
        r'^rounded$',
        r'^spaced$',

        # Semantic UI text modifiers
        r'^truncate$',
        r'^fitted$',

        # Semantic UI responsive classes
        r'^mobile$',
        r'^tablet$',
        r'^computer$',
        r'^largescreen$',
        r'^widescreen$',
        r'^only$',

        # Semantic UI utility patterns (prefix-based)
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
