use martial_stacking::{merge_stacks, Stack};

#[test]
fn merge_is_independent_of_submission_order() {
    let a = vec![
        Stack { id: 3, magnitude: 5 },
        Stack { id: 1, magnitude: 2 },
        Stack { id: 2, magnitude: 4 },
    ];
    let b = vec![
        Stack { id: 1, magnitude: 2 },
        Stack { id: 2, magnitude: 4 },
        Stack { id: 3, magnitude: 5 },
    ];
    let ra = merge_stacks(&a, 100);
    let rb = merge_stacks(&b, 100);
    let ids_a: Vec<u32> = ra.iter().map(|s| s.id).collect();
    let ids_b: Vec<u32> = rb.iter().map(|s| s.id).collect();
    assert_eq!(ids_a, vec![1, 2, 3]);
    assert_eq!(ids_a, ids_b);
}

#[test]
fn duplicate_ids_sum_then_clamp() {
    let stacks = vec![
        Stack { id: 7, magnitude: 60 },
        Stack { id: 7, magnitude: 60 },
    ];
    let r = merge_stacks(&stacks, 100);
    assert_eq!(r.len(), 1);
    assert_eq!(r[0].id, 7);
    assert_eq!(r[0].magnitude, 100); // 120 clamped to cap
}
