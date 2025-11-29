#!/usr/bin/env python3
"""Install Playwright browsers."""

import sys
import subprocess


def main():
    """Install Playwright Chromium browser."""
    print("Installing Playwright Chromium browser...")

    try:
        # Run playwright install chromium via the module
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True,
            text=True
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        print("✅ Chromium browser installed successfully!")
        return 0

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running playwright install: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
