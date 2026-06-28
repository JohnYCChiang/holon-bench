import unittest

from src.cursor_tool.cursor import decode_cursor, encode_cursor


class PaginationCursorTest(unittest.TestCase):
    def test_round_trip(self):
        token = encode_cursor(5, "abc")
        r = decode_cursor(token)
        self.assertTrue(r["ok"])
        self.assertEqual(r["offset"], 5)
        self.assertEqual(r["key"], "abc")

    def test_token_is_opaque(self):
        token = encode_cursor(5, "abc")
        self.assertNotEqual(token, "5:abc")
        self.assertNotIn(":", token)

    def test_garbage_token_is_structured_error(self):
        r = decode_cursor("not!base64@@")
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "invalid_cursor")


if __name__ == "__main__":
    unittest.main()
