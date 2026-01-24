#!/usr/bin/env python3
"""Test script to verify Playwright headless Chromium setup."""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def configure_playwright_browsers():
    """
    Configure PLAYWRIGHT_BROWSERS_PATH using Bazel runfiles.
    """
    import os
    import sys
    from python.runfiles import runfiles
    
    try:
        if "RUNFILES_DIR" in os.environ:
            runfiles_dir = os.environ["RUNFILES_DIR"]
        elif "RUNFILES_MANIFEST_FILE" in os.environ:
            runfiles_dir = os.environ["RUNFILES_MANIFEST_FILE"][:-9]
        else:
             runfiles_dir = sys.argv[0] + ".runfiles"
             
        found_browsers = []
        for name in os.listdir(runfiles_dir):
            if "playwright" in name.lower():
                candidate_repo = os.path.join(runfiles_dir, name)
                if not os.path.isdir(candidate_repo):
                    continue
                browsers_dir = os.path.join(candidate_repo, "browsers")
                if os.path.isdir(browsers_dir):
                    search_path = os.path.join(browsers_dir, "*", "chromium*")
                    import glob
                    found = glob.glob(search_path)
                    if found:
                        found_browsers = found
                        break
        
        if found_browsers:
            browser_path = found_browsers[0]
            # browser_path is .../chromium_headless_shell-1155
            # We want the parent directory
            browsers_path = os.path.dirname(browser_path)
            print(f"Configuring PLAYWRIGHT_BROWSERS_PATH to: {browsers_path}")
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path
        else:
            print(f"WARNING: Could not find Playwright browsers in runfiles. Runfiles dir: {runfiles_dir}")
            
    except Exception as e:
        print(f"WARNING: Error configuring Playwright browsers: {e}")


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
