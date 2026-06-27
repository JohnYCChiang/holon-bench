use animal_trait::animal::{Animal, Dog, Spider};

#[test]
fn default_describe_uses_name_and_legs() {
    let d = Dog { name: "Rex".to_string() };
    assert_eq!(d.describe(), "Rex has 4 legs");
}

#[test]
fn override_is_preserved() {
    let s = Spider { name: "Webster".to_string() };
    assert_eq!(s.describe(), "Webster is a spooky spider with 8 legs");
}
