use martial_buff::{sweep, Buff};

fn b(id: u32, mag: i32, exp: u64) -> Buff {
    Buff { id, magnitude: mag, expires_at: exp }
}

#[test]
fn drops_buffs_expiring_at_now() {
    let got = sweep(&[b(1, 5, 10), b(2, 3, 20)], 10);
    assert_eq!(got, vec![b(2, 3, 20)]);
}

#[test]
fn sorted_by_expiry_then_id() {
    let got = sweep(&[b(3, 1, 30), b(1, 1, 30), b(2, 1, 15)], 5);
    assert_eq!(got, vec![b(2, 1, 15), b(1, 1, 30), b(3, 1, 30)]);
}

#[test]
fn order_independent() {
    let a = sweep(&[b(1, 1, 100), b(2, 2, 50)], 0);
    let c = sweep(&[b(2, 2, 50), b(1, 1, 100)], 0);
    assert_eq!(a, c);
}
