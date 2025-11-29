#!/usr/bin/env python3
"""
Extract critical (above-the-fold) CSS using Playwright.

This script loads a page in headless Chromium and extracts only the CSS
rules that apply to elements visible in the initial viewport.
"""

import sys
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright


def extract_critical_css(
    url: str,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    output_path: Path = None
) -> str:
    """
    Extract critical CSS for a given URL and viewport size.

    Args:
        url: URL to extract critical CSS from
        viewport_width: Viewport width in pixels
        viewport_height: Viewport height in pixels
        output_path: Optional path to save extracted CSS

    Returns:
        Extracted critical CSS as string
    """
    print(f"Extracting critical CSS for {url}")
    print(f"Viewport: {viewport_width}x{viewport_height}")

    with sync_playwright() as p:
        # Launch headless Chromium
        browser = p.chromium.launch(headless=True)

        # Create context with specified viewport
        context = browser.new_context(
            viewport={'width': viewport_width, 'height': viewport_height}
        )

        page = context.new_page()

        # Navigate to URL
        print(f"Navigating to {url}...")
        page.goto(url, wait_until='networkidle')

        # Wait for any dynamic content to settle
        page.wait_for_timeout(1000)

        # Extract critical CSS using JavaScript
        print("Extracting critical CSS rules...")
        critical_css = page.evaluate("""() => {
            // Get all stylesheets
            const getAllCSS = () => {
                let allCSS = [];

                // Process each stylesheet
                for (let i = 0; i < document.styleSheets.length; i++) {
                    try {
                        const sheet = document.styleSheets[i];
                        const rules = sheet.cssRules || sheet.rules;

                        if (rules) {
                            for (let j = 0; j < rules.length; j++) {
                                try {
                                    const rule = rules[j];
                                    if (rule.cssText) {
                                        allCSS.push({
                                            cssText: rule.cssText,
                                            selector: rule.selectorText,
                                            source: sheet.href || 'inline'
                                        });
                                    }
                                } catch (e) {
                                    // Skip inaccessible rules
                                }
                            }
                        }
                    } catch (e) {
                        // CORS or other access error - skip stylesheet
                    }
                }

                return allCSS;
            };

            // Check if an element is in viewport
            const isInViewport = (elem) => {
                const rect = elem.getBoundingClientRect();
                return (
                    rect.top < window.innerHeight &&
                    rect.bottom >= 0 &&
                    rect.left < window.innerWidth &&
                    rect.right >= 0
                );
            };

            // Get all elements in viewport
            const getVisibleElements = () => {
                const all = document.querySelectorAll('*');
                return Array.from(all).filter(el => {
                    // Must be visible
                    const style = window.getComputedStyle(el);
                    if (style.display === 'none' || style.visibility === 'hidden') {
                        return false;
                    }

                    // Must be in viewport
                    return isInViewport(el);
                });
            };

            // Check if a CSS rule applies to any visible element
            const ruleAppliesToVisibleElement = (rule, visibleElements) => {
                if (!rule.selector) {
                    // Non-selector rules (like @media, @keyframes, etc.)
                    return true;  // Keep all non-selector rules for now
                }

                try {
                    // Try to match selector against visible elements
                    for (const elem of visibleElements) {
                        try {
                            if (elem.matches && elem.matches(rule.selector)) {
                                return true;
                            }
                        } catch (e) {
                            // Invalid selector or matching error - keep the rule to be safe
                            return true;
                        }
                    }
                } catch (e) {
                    // If matching fails, include the rule to be safe
                    return true;
                }

                return false;
            };

            // Main extraction logic
            const allCSS = getAllCSS();
            const visibleElements = getVisibleElements();

            console.log(`Total CSS rules: ${allCSS.length}`);
            console.log(`Visible elements: ${visibleElements.length}`);

            // Filter to only rules that apply to visible elements
            const criticalRules = allCSS.filter(rule =>
                ruleAppliesToVisibleElement(rule, visibleElements)
            );

            console.log(`Critical CSS rules: ${criticalRules.length}`);

            // Group by source
            const bySource = {};
            for (const rule of criticalRules) {
                const source = rule.source;
                if (!bySource[source]) {
                    bySource[source] = [];
                }
                bySource[source].push(rule.cssText);
            }

            // Build final CSS output
            let output = '';
            for (const [source, rules] of Object.entries(bySource)) {
                output += `/* Source: ${source} */\\n`;
                output += rules.join('\\n');
                output += '\\n\\n';
            }

            return output;
        }""")

        browser.close()

    # Calculate stats
    css_size = len(critical_css.encode('utf-8'))
    css_size_kb = css_size / 1024

    print(f"✅ Critical CSS size: {css_size_kb:.2f} KB ({css_size} bytes)")

    # Check if under 10KB target
    if css_size_kb > 10:
        print(f"⚠️  Warning: Critical CSS exceeds 10KB target ({css_size_kb:.2f} KB)")
    else:
        print(f"✅ Critical CSS is under 10KB target")

    # Save to file if output path specified
    if output_path:
        output_path.write_text(critical_css)
        print(f"✅ Saved to: {output_path}")

    return critical_css


def extract_critical_css_multi_viewport(
    url: str,
    output_path: Path = None
) -> str:
    """
    Extract critical CSS for both desktop and mobile viewports, then merge.

    Args:
        url: URL to extract critical CSS from
        output_path: Optional path to save merged CSS

    Returns:
        Merged critical CSS for all viewports
    """
    print("=" * 60)
    print("Extracting critical CSS for multiple viewports")
    print("=" * 60)

    # Extract for desktop (1920x1080)
    print("\n[1/2] Desktop viewport (1920x1080)")
    print("-" * 60)
    desktop_css = extract_critical_css(url, 1920, 1080)

    # Extract for mobile (375x667)
    print("\n[2/2] Mobile viewport (375x667)")
    print("-" * 60)
    mobile_css = extract_critical_css(url, 375, 667)

    # Merge (simple approach: combine both)
    print("\n" + "=" * 60)
    print("Merging viewport CSS")
    print("=" * 60)

    merged_css = f"""/* Critical CSS - Generated for multiple viewports */
/* Desktop: 1920x1080, Mobile: 375x667 */

/* ===== Desktop Viewport ===== */
{desktop_css}

/* ===== Mobile Viewport ===== */
{mobile_css}
"""

    # Calculate final stats
    merged_size = len(merged_css.encode('utf-8'))
    merged_size_kb = merged_size / 1024

    print(f"✅ Merged critical CSS size: {merged_size_kb:.2f} KB ({merged_size} bytes)")

    # Check if under 10KB target
    if merged_size_kb > 10:
        print(f"⚠️  Warning: Critical CSS exceeds 10KB target ({merged_size_kb:.2f} KB)")
    else:
        print(f"✅ Critical CSS is under 10KB target")

    # Save to file if output path specified
    if output_path:
        output_path.write_text(merged_css)
        print(f"✅ Saved merged CSS to: {output_path}")

    return merged_css


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract critical CSS from a URL using Playwright"
    )
    parser.add_argument("url", help="URL to extract critical CSS from")
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path for critical CSS"
    )
    parser.add_argument(
        "--multi-viewport",
        action="store_true",
        help="Extract for both desktop and mobile viewports"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Viewport width (default: 1920)"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1080,
        help="Viewport height (default: 1080)"
    )

    args = parser.parse_args()

    try:
        if args.multi_viewport:
            extract_critical_css_multi_viewport(args.url, args.output)
        else:
            extract_critical_css(
                args.url,
                args.width,
                args.height,
                args.output
            )

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
