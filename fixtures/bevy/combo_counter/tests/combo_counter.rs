use combo_counter::combo::{hit, tick, Combo};

#[test]
fn consecutive_hits_grow_combo() {
    let mut c = Combo::new(1.0);
    hit(&mut c);
    hit(&mut c);
    hit(&mut c);
    assert_eq!(c.count, 3);
}

#[test]
fn lapse_resets_combo_to_zero() {
    let mut c = Combo::new(1.0);
    hit(&mut c);
    hit(&mut c);
    tick(&mut c, 1.5);
    assert_eq!(c.count, 0);
    assert_eq!(c.timer, 0.0);
}
