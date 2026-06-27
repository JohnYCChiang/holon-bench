# Bug report: `transpose` panics on any non-square matrix

`transpose(m) -> Result<Vec<Vec<i64>>, MatrixError>` should transpose an
`R x C` matrix into a `C x R` one. The contract says ragged input is reported
as `Err(MatrixError::Ragged)` and the function **must never panic**. A user
reports a crash on a 3x2 matrix:

```
thread 'main' panicked at 'index out of bounds: the len is 2 but the index is 2'
// transpose(&vec![vec![1,2], vec![3,4], vec![5,6]])
//   -> expected Ok(vec![vec![1,3,5], vec![2,4,6]])
```

The output is allocated as an `R x R` square (using the row count for both
dimensions), so a matrix with more rows than columns indexes past the end of a
row, and a wider matrix is silently truncated.

Expected: an `R x C` matrix transposes to `C x R`; rows of unequal length
return `Err(MatrixError::Ragged)`; an empty matrix returns `Ok(vec![])`; values
are preserved (`transpose(transpose(m)) == m`). Never panic.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`transpose` signature and the `MatrixError` variants), and **leave behind a
regression test**.
