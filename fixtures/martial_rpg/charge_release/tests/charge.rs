use martial_charge::release;

#[test]
fn below_min_charge_is_base_only() {
    assert_eq!(release(100, 2, 5, 25, 200), 100);
}

#[test]
fn full_charge_grants_full_bonus() {
    assert_eq!(release(100, 25, 5, 25, 200), 300);
}

#[test]
fn overcharge_caps_at_full_bonus() {
    assert_eq!(release(100, 999, 5, 25, 200), 300);
}
