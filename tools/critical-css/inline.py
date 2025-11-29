#!/usr/bin/env python3
"""
Inline critical CSS into HTML <head> and defer original stylesheets.

This script takes an HTML file and critical CSS, then:
1. Injects critical CSS as <style> in <head>
2. Converts <link rel="stylesheet"> to async loading
3. Moves stylesheet loading to end of <body> for better performance
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
from bs4 import BeautifulSoup


def inline_critical_css(
    html_path: Path,
    critical_css: str,
    output_path: Optional[Path] = None
) -> str:
    """
    Inline critical CSS into an HTML file.

    Args:
        html_path: Path to HTML file to process
        critical_css: Critical CSS string to inline
        output_path: Optional path to save modified HTML

    Returns:
        Modified HTML as string
    """
    print(f"Processing HTML: {html_path}")

    # Read HTML file
    html_content = html_path.read_text()

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find or create <head>
    head = soup.find('head')
    if not head:
        print("Warning: No <head> tag found, creating one")
        head = soup.new_tag('head')
        if soup.html:
            soup.html.insert(0, head)
        else:
            # Create html tag if needed
            html_tag = soup.new_tag('html')
            soup.insert(0, html_tag)
            html_tag.insert(0, head)

    # Find all stylesheet links
    stylesheet_links = soup.find_all('link', rel='stylesheet')
    print(f"Found {len(stylesheet_links)} stylesheet links")

    if stylesheet_links:
        # Create critical CSS style tag
        critical_style = soup.new_tag('style')
        critical_style['id'] = 'critical-css'
        critical_style.string = f"\n{critical_css}\n"

        # Insert critical CSS at the beginning of <head>
        # (after charset/viewport but before other content)
        charset_meta = head.find('meta', charset=True)
        viewport_meta = head.find('meta', attrs={'name': 'viewport'})

        if viewport_meta:
            viewport_meta.insert_after(critical_style)
        elif charset_meta:
            charset_meta.insert_after(critical_style)
        else:
            head.insert(0, critical_style)

        print("✅ Injected critical CSS into <head>")

        # Find or create <body>
        body = soup.find('body')
        if not body:
            print("Warning: No <body> tag found, stylesheet deferral skipped")
        else:
            # Convert stylesheet links to async loading
            # and move to end of body
            for link in stylesheet_links:
                href = link.get('href', '')

                # Create async loading script
                # Using media="print" trick for async CSS loading
                async_link = soup.new_tag('link')
                async_link['rel'] = 'stylesheet'
                async_link['href'] = href
                async_link['media'] = 'print'
                async_link['onload'] = "this.media='all'"

                # Add noscript fallback
                noscript = soup.new_tag('noscript')
                fallback_link = soup.new_tag('link')
                fallback_link['rel'] = 'stylesheet'
                fallback_link['href'] = href
                noscript.append(fallback_link)

                # Remove original link from head
                link.decompose()

                # Append async link and fallback to end of body
                body.append(async_link)
                body.append(noscript)

            print(f"✅ Moved {len(stylesheet_links)} stylesheets to async load at end of <body>")

    else:
        print("⚠️  No stylesheet links found in HTML")

    # Convert back to string
    # Use formatter=None to preserve original formatting as much as possible
    modified_html = str(soup)

    # Calculate size stats
    original_size = len(html_content.encode('utf-8'))
    modified_size = len(modified_html.encode('utf-8'))
    size_increase = modified_size - original_size

    print(f"Original size: {original_size} bytes")
    print(f"Modified size: {modified_size} bytes")
    print(f"Size increase: {size_increase} bytes (+{size_increase/original_size*100:.1f}%)")

    # Save to file if output path specified
    if output_path:
        output_path.write_text(modified_html)
        print(f"✅ Saved to: {output_path}")
    else:
        print("⚠️  No output path specified, not saving")

    return modified_html


def process_directory(
    html_dir: Path,
    critical_css: str,
    output_dir: Path,
    pattern: str = "**/*.html"
) -> int:
    """
    Process all HTML files in a directory.

    Args:
        html_dir: Directory containing HTML files
        critical_css: Critical CSS to inline
        output_dir: Directory to save modified HTML files
        pattern: Glob pattern for HTML files (default: **/*.html)

    Returns:
        Number of files processed
    """
    print("=" * 60)
    print(f"Processing directory: {html_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Pattern: {pattern}")
    print("=" * 60)

    # Find all HTML files
    html_files = list(html_dir.glob(pattern))
    print(f"\nFound {len(html_files)} HTML files")

    if not html_files:
        print("⚠️  No HTML files found")
        return 0

    # Create output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each file
    processed = 0
    for html_file in html_files:
        print(f"\n[{processed + 1}/{len(html_files)}] Processing: {html_file.name}")
        print("-" * 60)

        # Calculate relative path and output path
        rel_path = html_file.relative_to(html_dir)
        output_file = output_dir / rel_path

        # Create parent directory if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            inline_critical_css(html_file, critical_css, output_file)
            processed += 1
        except Exception as e:
            print(f"❌ Error processing {html_file}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"✅ Processed {processed}/{len(html_files)} files")
    print("=" * 60)

    return processed


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Inline critical CSS into HTML files"
    )
    parser.add_argument(
        "html_input",
        type=Path,
        help="HTML file or directory to process"
    )
    parser.add_argument(
        "critical_css",
        type=Path,
        help="File containing critical CSS to inline"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        required=True,
        help="Output file or directory"
    )
    parser.add_argument(
        "--pattern",
        default="**/*.html",
        help="Glob pattern for HTML files when processing directory (default: **/*.html)"
    )

    args = parser.parse_args()

    try:
        # Read critical CSS
        critical_css = args.critical_css.read_text()
        print(f"Loaded critical CSS: {len(critical_css)} bytes")
        print()

        # Check if input is a directory or file
        if args.html_input.is_dir():
            # Process directory
            processed = process_directory(
                args.html_input,
                critical_css,
                args.output,
                args.pattern
            )
            return 0 if processed > 0 else 1
        else:
            # Process single file
            inline_critical_css(
                args.html_input,
                critical_css,
                args.output
            )
            return 0

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
