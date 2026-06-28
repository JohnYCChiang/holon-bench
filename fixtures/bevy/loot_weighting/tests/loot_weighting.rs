use loot_weighting::loot::{pick, LootEntry};

#[test]
fn roll_maps_to_weight_bands() {
    let table = [
        LootEntry { id: 1, weight: 2 },
        LootEntry { id: 2, weight: 3 },
    ];
    assert_eq!(pick(&table, 0), Some(1));
    assert_eq!(pick(&table, 1), Some(1));
    assert_eq!(pick(&table, 2), Some(2));
    assert_eq!(pick(&table, 4), Some(2));
}

#[test]
fn empty_table_returns_none() {
    let table: [LootEntry; 0] = [];
    assert_eq!(pick(&table, 0), None);
}
