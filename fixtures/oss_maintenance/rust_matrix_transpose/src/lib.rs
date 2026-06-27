//! Transpose a dense matrix of `i64`. An `R x C` matrix becomes `C x R`. Ragged
//! input (rows of unequal length) is reported as an error; the function must
//! never panic.

#[derive(Debug, PartialEq, Eq)]
pub enum MatrixError {
    /// The matrix has rows of unequal length.
    Ragged,
}

/// Transpose `m`, returning a new matrix.
pub fn transpose(m: &Vec<Vec<i64>>) -> Result<Vec<Vec<i64>>, MatrixError> {
    let n = m.len();
    // BUG: assumes the matrix is square (n x n). For a non-square matrix this
    // both allocates the wrong shape and indexes out of bounds below.
    let mut out = vec![vec![0i64; n]; n];
    for i in 0..n {
        for j in 0..n {
            out[j][i] = m[i][j];
        }
    }
    Ok(out)
}
