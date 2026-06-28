import unittest

from src.frontmatter_tool.split import split


class FrontmatterTest(unittest.TestCase):
    def test_basic(self):
        r = split("---\ntitle: x\n---\nbody")
        self.assertEqual(r["frontmatter"], "title: x")
        self.assertEqual(r["body"], "body")

    def test_no_frontmatter(self):
        text = "just body\nline2\n"
        r = split(text)
        self.assertEqual(r["frontmatter"], "")
        self.assertEqual(r["body"], text)


if __name__ == "__main__":
    unittest.main()
