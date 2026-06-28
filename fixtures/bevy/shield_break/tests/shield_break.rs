use shield_break::shield::{absorb, Shield};

#[test]
fn shield_breaks_when_depleted() {
    let mut s = Shield::new(30);
    let overflow = absorb(&mut s, 30);
    assert_eq!(overflow, 0);
    assert!(s.broken);
}

#[test]
fn overflow_passes_through() {
    let mut s = Shield::new(20);
    let overflow = absorb(&mut s, 50);
    assert_eq!(overflow, 30);
    assert!(s.broken);
}
