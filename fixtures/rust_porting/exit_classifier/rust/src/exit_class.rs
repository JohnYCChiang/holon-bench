pub fn classify_exit(code: i32) -> (&'static str, bool) {
    if code == 0 {
        ("success", false)
    } else {
        ("failed", false)
    }
}
