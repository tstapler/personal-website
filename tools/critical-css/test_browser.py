#!/usr/bin/env python3
"""Test script to verify Playwright headless Chromium setup."""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def configure_playwright_browsers():
    """
    Configure PLAYWRIGHT_BROWSERS_PATH to point to the browser in runfiles.
    """
    import os
    if "PLAYWRIGHT_BROWSERS_PATH" in os.environ:
        return

    runfiles_dir = Path(sys.argv[0] + ".runfiles")
    if not runfiles_dir.exists():
        runfiles_dir = Path(".")

    # Search for chromium directory in runfiles
    # The structure is usually: external/rules_playwright++playwright+playwright/browsers/...
    found_browsers = list(runfiles_dir.glob("**/browsers/*/chromium-*"))
    
    if found_browsers:
        browser_dir = found_browsers[0]
        browsers_path = browser_dir.parent
        print(f"Configuring PLAYWRIGHT_BROWSERS_PATH to: {browsers_path}")
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers_path)


def test_browser_launch():
    """Test launching headless Chromium and capturing a screenshot."""
    configure_playwright_browsers()
    print("Testing Playwright headless Chromium setup...")

    try:
        with sync_playwright() as p:
            # Launch headless Chromium
            print("Launching headless Chromium...")
            browser = p.chromium.launch(headless=True)

            # Create a new page
            print("Creating new page...")
            page = browser.new_page()

            # Navigate to a simple test page
            print("Navigating to example.com...")
            page.goto("https://example.com")

            # Get page title to verify navigation worked
            title = page.title()
            print(f"Page title: {title}")

            # Take a screenshot
            screenshot_path = Path("/tmp/playwright-test.png")
            print(f"Taking screenshot: {screenshot_path}")
            page.screenshot(path=str(screenshot_path))

            # Verify screenshot was created
            if screenshot_path.exists():
                print(f"✅ Screenshot saved successfully ({screenshot_path.stat().st_size} bytes)")
            else:
                print("❌ Screenshot file not created")
                return 1

            # Close browser
            browser.close()
            print("✅ Browser test completed successfully!")
            return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(test_browser_launch())
