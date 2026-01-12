import unittest
import os
import threading
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer
from playwright.sync_api import sync_playwright

class TestSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Locate the built site directory provided by Bazel
        # Bazel runfiles usually provide the path relative to the workspace
        # But for this test, we expect //:site to provide the directory
        # The 'data' attribute in BUILD.bazel puts the directory in the runfiles.
        
        # Simple heuristic to find the site directory
        cls.site_dir = "personal-website" # This might need adjustment based on Bazel layout
        
        # Walk up to find the 'personal-website' directory (the output of //:site)
        # In Bazel runfiles, it's usually under <workspace_name>/...
        # Let's try to find index.html to confirm root
        
        # Assuming the test is run with bazel test //tests/e2e:site_test
        # The working directory is the runfiles root.
        
        # We need to find where the 'site' filegroup contents are mapped.
        # Since //:site creates a directory, we need to find it.
        # Let's check common locations.
        possible_roots = [
            "personal-website",
            "../personal-website",
            "site", # if mapped as site
        ]
        
        cls.server_dir = None
        for path in possible_roots:
            if os.path.exists(os.path.join(path, "index.html")):
                cls.server_dir = path
                break
        
        # If running locally without Bazel (debug), fallback or fail
        if not cls.server_dir:
            # Fallback for exploration: try to find any index.html
            for root, dirs, files in os.walk("."):
                if "index.html" in files:
                    cls.server_dir = root
                    break
                    
        if not cls.server_dir:
             raise RuntimeError(f"Could not find site root containing index.html. Searched: {possible_roots}")

        print(f"Serving site from: {os.path.abspath(cls.server_dir)}")

        # Start HTTP server in a thread
        cls.port = 8000
        cls.httpd = HTTPServer(('localhost', cls.port), 
                               lambda *args: SimpleHTTPRequestHandler(*args, directory=cls.server_dir))
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # Give server a moment to start
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'httpd'):
            cls.httpd.shutdown()
            cls.httpd.server_close()

    def test_sidebar_and_navigation(self):
        with sync_playwright() as p:
            # Launch browser (headless by default)
            # We use chromium for general compatibility
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # 1. Navigate to home
            page.goto(f"http://localhost:{self.port}/")
            
            # 2. Check Title
            title = page.title()
            print(f"Page Title: {title}")
            self.assertIn("Tyler Stapler", title) # Adjust based on actual title
            
            # 3. Check Sidebar Existence
            # The sidebar typically has class 'ui sidebar' or similar
            sidebar = page.locator(".ui.sidebar")
            self.assertTrue(sidebar.count() > 0, "Sidebar element not found")
            
            # 4. Check Sidebar Items
            # User snippet: <a class="item" href="/">... Home ...</a>
            home_link = sidebar.locator("a[href='/']:has-text('Home')")
            blog_link = sidebar.locator("a[href='/blog/']:has-text('Blog')")
            
            self.assertTrue(home_link.count() > 0, "Home link in sidebar not found")
            self.assertTrue(blog_link.count() > 0, "Blog link in sidebar not found")
            
            # 5. Check Sidebar Visibility (Logic might vary based on viewport)
            # Usually hidden on desktop until toggled, or visible on mobile?
            # Let's just verify it's in the DOM for now to catch "stripping" issues.
            # If PurgeCSS removed it, it wouldn't be in the DOM (if styled out) OR classes would be missing.
            
            # Check classes
            class_attr = sidebar.get_attribute("class")
            print(f"Sidebar classes: {class_attr}")
            self.assertIn("ui", class_attr)
            self.assertIn("sidebar", class_attr)
            
            # 6. Check Masthead overlap issue (Particles)
            # Verify #particles-js exists
            particles = page.locator("#particles-js")
            self.assertTrue(particles.count() > 0, "Particles container not found")
            
            # Check if canvas exists
            canvas = particles.locator("canvas")
            self.assertTrue(canvas.count() > 0, "Particles canvas not found")

            # Basic layout check: Masthead should be visible
            masthead = page.locator("#intro-masthead")
            self.assertTrue(masthead.is_visible(), "Masthead is not visible")

            browser.close()

if __name__ == '__main__':
    unittest.main()
