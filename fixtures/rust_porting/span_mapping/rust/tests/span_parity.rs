use span_mapping::span::byte_offset_to_line_col;
use std::process::Command;

fn python(text: &str, offset: usize) -> String {
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let output = Command::new("python3").args([script, text, &offset.to_string()]).output().unwrap();
    assert!(output.status.success());
    String::from_utf8(output.stdout).unwrap().trim().to_string()
}

fn rust(text: &str, offset: usize) -> String {
    let (line, col) = byte_offset_to_line_col(text, offset);
    format!("{line}:{col}")
}

#[test]
fn maps_offsets_like_python_reference() {
    let text = "a\néx\nz";
    for offset in [0, 1, 2, 4, 5, 99] {
        assert_eq!(rust(text, offset), python(text, offset), "offset={offset}");
    }
}
