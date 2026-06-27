use matrix_ops::transpose;

#[test]
fn tall_matrix_transposes_without_panic() {
    assert_eq!(
        transpose(&vec![vec![1, 2], vec![3, 4], vec![5, 6]]),
        Ok(vec![vec![1, 3, 5], vec![2, 4, 6]])
    );
}
