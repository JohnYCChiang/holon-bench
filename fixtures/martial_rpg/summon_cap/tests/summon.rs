use martial_summon::Summoner;

#[test]
fn rejects_beyond_cap() {
    let mut s = Summoner::new(2);
    assert!(s.summon(1));
    assert!(s.summon(2));
    assert!(!s.summon(3));
    assert_eq!(s.count(), 2);
}

#[test]
fn rejects_duplicate() {
    let mut s = Summoner::new(3);
    assert!(s.summon(5));
    assert!(!s.summon(5));
    assert_eq!(s.count(), 1);
}

#[test]
fn active_is_sorted() {
    let mut s = Summoner::new(5);
    s.summon(3);
    s.summon(1);
    s.summon(2);
    assert_eq!(s.active(), vec![1, 2, 3]);
}
