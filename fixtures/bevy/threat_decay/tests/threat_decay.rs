use threat_decay::threat::{decay, top_target, ThreatTable};

#[test]
fn highest_threat_is_targeted() {
    let mut t = ThreatTable::new();
    t.add(1, 10.0);
    t.add(2, 25.0);
    t.add(3, 5.0);
    assert_eq!(top_target(&t), Some(2));
}

#[test]
fn decay_floors_threat_at_zero() {
    let mut t = ThreatTable::new();
    t.add(7, 3.0);
    decay(&mut t, 10.0);
    assert_eq!(t.entries[0].1, 0.0);
    assert_eq!(top_target(&t), None);
}
