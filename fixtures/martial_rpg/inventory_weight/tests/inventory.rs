use martial_inventory::{try_add, Inventory};

#[test]
fn item_within_capacity_is_added() {
    let mut inv = Inventory { weight: 0, capacity: 100 };
    assert!(try_add(&mut inv, 40));
    assert_eq!(inv.weight, 40);
}

#[test]
fn exact_capacity_fits() {
    let mut inv = Inventory { weight: 60, capacity: 100 };
    assert!(try_add(&mut inv, 40));
    assert_eq!(inv.weight, 100);
}

#[test]
fn overflow_is_rejected() {
    let mut inv = Inventory { weight: 90, capacity: 100 };
    assert!(!try_add(&mut inv, 20));
    assert_eq!(inv.weight, 90);
}
