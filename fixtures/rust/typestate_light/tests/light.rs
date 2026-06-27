use typestate_light::light::Light;

#[test]
fn cycles_through_phases() {
    let red = Light::new();
    assert_eq!(red.color(), "red");
    let green = red.next();
    assert_eq!(green.color(), "green");
    let yellow = green.next();
    assert_eq!(yellow.color(), "yellow");
}

#[test]
fn returns_to_red() {
    let red = Light::new().next().next().next();
    assert_eq!(red.color(), "red");
}
