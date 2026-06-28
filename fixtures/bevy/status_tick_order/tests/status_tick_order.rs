use status_tick_order::status::{tick, Kind, Status};

#[test]
fn poison_resolves_before_heal() {
    let hp = 100;
    let a = [
        Status::new(1, Kind::Poison, 20),
        Status::new(2, Kind::Heal, 10),
    ];
    let b = [
        Status::new(2, Kind::Heal, 10),
        Status::new(1, Kind::Poison, 20),
    ];
    assert_eq!(tick(hp, &a), tick(hp, &b));
}

#[test]
fn known_result() {
    let hp = 100;
    let s = [
        Status::new(2, Kind::Heal, 10),
        Status::new(1, Kind::Poison, 20),
    ];
    // poison first: 100 - 20 = 80, then heal +10 = 90
    assert_eq!(tick(hp, &s), 90);
}
