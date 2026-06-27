use martial_shuffle::{shuffle, Deck};

#[test]
fn result_is_a_permutation() {
    let mut out = shuffle(&Deck { size: 8 }, 12345);
    out.sort_unstable();
    assert_eq!(out, vec![0, 1, 2, 3, 4, 5, 6, 7]);
}

#[test]
fn same_seed_reproduces_order() {
    let a = shuffle(&Deck { size: 8 }, 12345);
    let b = shuffle(&Deck { size: 8 }, 12345);
    assert_eq!(a, b);
}
