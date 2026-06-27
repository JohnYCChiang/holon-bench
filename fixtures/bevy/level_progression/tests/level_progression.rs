use level_progression::progression::level_for_xp;

const T: [u32; 3] = [100, 250, 500];

#[test]
fn reaching_threshold_exactly_levels_up() {
    assert_eq!(level_for_xp(100, &T), 2);
    assert_eq!(level_for_xp(500, &T), 4);
}

#[test]
fn between_thresholds_holds_level() {
    assert_eq!(level_for_xp(0, &T), 1);
    assert_eq!(level_for_xp(99, &T), 1);
    assert_eq!(level_for_xp(499, &T), 3);
}
