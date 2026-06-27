use martial_carddraw::draw_hand;

#[test]
fn hand_has_no_duplicates() {
    let hand = draw_hand(42, 20, 5);
    assert_eq!(hand.len(), 5);
    let mut sorted = hand.clone();
    sorted.sort();
    sorted.dedup();
    assert_eq!(sorted.len(), 5, "hand had duplicates: {:?}", hand);
    assert!(hand.iter().all(|&c| c < 20));
}

#[test]
fn reproducible_for_same_seed() {
    assert_eq!(draw_hand(7, 30, 6), draw_hand(7, 30, 6));
}

#[test]
fn hand_size_capped_to_deck_is_a_permutation() {
    let mut hand = draw_hand(1, 3, 10);
    assert_eq!(hand.len(), 3);
    hand.sort();
    assert_eq!(hand, vec![0, 1, 2]);
}
