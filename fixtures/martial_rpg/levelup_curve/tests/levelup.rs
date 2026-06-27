use martial_levelup::{award, Progress};

#[test]
fn one_level_carries_remainder() {
    // 150 xp at level 1 (needs 100) -> level 2 with 50 carried.
    let p = award(Progress { level: 1, xp: 0 }, 150, 10);
    assert_eq!(p, Progress { level: 2, xp: 50 });
}

#[test]
fn not_enough_xp_stays() {
    let p = award(Progress { level: 1, xp: 0 }, 50, 10);
    assert_eq!(p, Progress { level: 1, xp: 50 });
}
