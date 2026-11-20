import unittest
from tools.purgecss.analyze import extract_html_classes_and_ids, extract_css_selectors

class TestAnalyze(unittest.TestCase):
    def test_extract_html_classes_and_ids_basic(self):
        html = '<div class="foo" id="bar"></div>'
        classes, ids = extract_html_classes_and_ids(html)
        self.assertEqual(classes, {"foo"})
        self.assertEqual(ids, {"bar"})

    def test_extract_html_classes_multiple(self):
        html = '<div class="foo bar baz"></div>'
        classes, ids = extract_html_classes_and_ids(html)
        self.assertEqual(classes, {"foo", "bar", "baz"})
        self.assertEqual(ids, set())

    def test_extract_html_multiple_elements(self):
        html = '''
        <div class="header" id="main-header">
            <p class="text_content">Hello</p>
            <span id="footer"></span>
        </div>
        '''
        classes, ids = extract_html_classes_and_ids(html)
        self.assertEqual(classes, {"header", "text_content"})
        self.assertEqual(ids, {"main-header", "footer"})

    def test_extract_html_quotes(self):
        html = "<div class='single' id='quote'></div>"
        classes, ids = extract_html_classes_and_ids(html)
        self.assertEqual(classes, {"single"})
        self.assertEqual(ids, {"quote"})

    def test_extract_html_hyphens_underscores(self):
        html = '<div class="my-class_name" id="my-id_name"></div>'
        classes, ids = extract_html_classes_and_ids(html)
        self.assertEqual(classes, {"my-class_name"})
        self.assertEqual(ids, {"my-id_name"})

    def test_extract_html_edge_cases(self):
        # Empty attributes
        html = '<div class="" id=""></div>'
        classes, ids = extract_html_classes_and_ids(html)
        self.assertEqual(classes, set())
        self.assertEqual(ids, set())

        # No classes or IDs
        html = '<div><p>No attributes here</p></div>'
        classes, ids = extract_html_classes_and_ids(html)
        self.assertEqual(classes, set())
        self.assertEqual(ids, set())

        # Extra spaces
        html = '<div class="  foo   bar  "></div>'
        classes, ids = extract_html_classes_and_ids(html)
        self.assertEqual(classes, {"foo", "bar"})

    def test_extract_css_selectors_basic(self):
        css = '.my-class { color: red; } #my-id { color: blue; } div { color: green; }'
        selectors = extract_css_selectors(css)
        self.assertIn(".my-class", selectors)
        self.assertIn("#my-id", selectors)
        self.assertIn("div", selectors)

    def test_extract_css_selectors_complex(self):
        css = '''
        .btn:hover { opacity: 0.8; }
        input[type="text"] { border: 1px solid; }
        .nav, .footer { margin: 0; }
        '''
        selectors = extract_css_selectors(css)
        self.assertIn(".btn:hover", selectors)
        self.assertIn('input[type="text"]', selectors)
        self.assertIn(".nav", selectors)
        self.assertIn(".footer", selectors)

    def test_extract_css_selectors_comments_and_at_rules(self):
        css = '''
        /* This is a comment */
        .visible { display: block; }
        @media (max-width: 600px) {
            .mobile-only { display: block; }
        }
        '''
        selectors = extract_css_selectors(css)
        self.assertIn(".visible", selectors)
        self.assertIn(".mobile-only", selectors)

        # Ensure @media itself is not picked up as a selector
        for s in selectors:
            self.assertFalse(s.startswith('@'))

if __name__ == '__main__':
    unittest.main()
