use martial_channel::Channel;

#[test]
fn interrupt_on_threshold_hit() {
    let mut c = Channel::new(5, 10);
    c.hit(10);
    assert!(c.interrupted);
    assert!(!c.is_active());
}

#[test]
fn small_hit_does_not_interrupt() {
    let mut c = Channel::new(5, 10);
    c.hit(9);
    assert!(!c.interrupted);
    assert!(c.is_active());
}

#[test]
fn ignores_client_interrupt_flag() {
    let mut c = Channel::new(5, 10);
    c.client_interrupted = true;
    c.hit(1);
    assert!(!c.interrupted);
}
