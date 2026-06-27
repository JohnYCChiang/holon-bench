# Bug report: `escape` double-escapes the ampersands it just introduced

`htmlesc.escape` escapes the five HTML special characters. A user reports that
escaping a `<` produces a mangled, double-escaped entity:

```
>>> from src.htmlesc import escape
>>> escape("a < b")
'a &amp;lt; b'      # expected 'a &lt; b'
```

The ampersand replacement runs **last**, so it rewrites the `&` in the `&lt;`
(and `&gt;`, `&quot;`, `&#39;`) entities that the earlier replacements just
inserted, yielding `&amp;lt;`. Any input containing `<`, `>`, `"`, or `'` comes
back double-escaped.

Expected: `&` is escaped **first** (or the replacements are otherwise ordered so
nothing is escaped twice), so each special character maps to exactly one entity.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`escape(s)` API), and **leave behind a regression test** that pins the
no-double-escape contract.
