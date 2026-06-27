# Bug report: `parse_csv` splits inside quoted fields

`parse_csv(text)` parses CSV text into a list of rows (each a list of string
fields). Quoted fields are supposed to protect embedded commas and newlines. A
user reports a quoted field being torn apart:

```
parse_csv('a,"b,c",d')
# got:  [['a', '"b', 'c"', 'd']]
# want: [['a', 'b,c', 'd']]
```

The implementation just splits on every newline and then every comma, so it
never enters "quoted" mode: commas and newlines inside quotes act as separators
and the surrounding quote characters are left in place.

Expected: a double-quoted field may contain commas and newlines literally; a
doubled quote `""` inside such a field is a single literal `"`; the wrapping
quotes are stripped. An empty string parses to `[]`; a trailing newline does not
add an empty row.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`parse_csv(text)` signature and list-of-rows return shape), and **leave behind a
regression test** so this defect cannot come back.
