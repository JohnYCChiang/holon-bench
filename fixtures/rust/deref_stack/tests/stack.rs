use deref_stack::stack::Stack;

#[test]
fn len_and_ends() {
    let mut s = Stack::new();
    s.push("a");
    s.push("b");
    s.push("c");
    assert_eq!(s.len(), 3);
    assert_eq!(s.first(), Some(&"a"));
    assert_eq!(s.last(), Some(&"c"));
}

#[test]
fn iterates_all() {
    let mut s = Stack::new();
    s.push(1);
    s.push(2);
    s.push(3);
    assert_eq!(s.iter().sum::<i32>(), 6);
}
