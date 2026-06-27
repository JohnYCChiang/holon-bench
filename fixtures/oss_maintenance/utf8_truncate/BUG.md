# Bug report: `truncate_utf8` crashes on multi-byte characters

`truncate_utf8(text, max_bytes)` is documented to return the longest prefix of
`text` whose UTF-8 encoding fits in `max_bytes` bytes, **without splitting a
multi-byte character**. A user hit a crash when the byte limit lands in the
middle of an accented letter:

```
Traceback (most recent call last):
  File "app.py", line 17, in label
    return truncate_utf8(name, 2)
  File "src/textutil.py", line 8, in truncate_utf8
    return text.encode("utf-8")[:max_bytes].decode("utf-8")
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc3 in position 1:
unexpected end of data
```

Their input was `"héllo"` with `max_bytes=2`. The `é` is two bytes, so slicing
at 2 bytes cuts it in half and decoding explodes.

Expected: `truncate_utf8("héllo", 2) == "h"` — a character that does not fully
fit is dropped, never split, and the function never raises on valid text.

You are the maintainer. Reproduce, fix the root cause minimally, and **leave
behind a regression test** that pins the multi-byte boundary behavior.
