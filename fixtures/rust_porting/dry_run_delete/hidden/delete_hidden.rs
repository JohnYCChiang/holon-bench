use dry_run_delete::delete::{delete_paths, DeleteReport};
use std::fs;
use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};

fn temp_root(name: &str) -> PathBuf {
    let nonce = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos();
    std::env::temp_dir().join(format!("holon-delete-hidden-{name}-{nonce}"))
}

#[test]
fn hidden_repeated_dry_run_has_no_side_effects_then_real_delete_removes_files() {
    let root = temp_root("repeat");
    fs::create_dir_all(&root).unwrap();
    fs::write(root.join("z.txt"), "z").unwrap();
    fs::write(root.join("a.txt"), "a").unwrap();

    let paths = vec![root.join("z.txt"), root.join("missing.txt"), root.join("a.txt")];
    let expected_dry = DeleteReport {
        deleted: 0,
        would_delete: vec!["a.txt".to_string(), "z.txt".to_string()],
        skipped: vec!["missing.txt".to_string()],
    };

    assert_eq!(delete_paths(&paths, true), expected_dry);
    assert_eq!(delete_paths(&paths, true), expected_dry);
    assert!(root.join("a.txt").exists());
    assert!(root.join("z.txt").exists());

    let expected_real = DeleteReport {
        deleted: 2,
        would_delete: Vec::new(),
        skipped: vec!["missing.txt".to_string()],
    };
    assert_eq!(delete_paths(&paths, false), expected_real);
    assert!(!root.join("a.txt").exists());
    assert!(!root.join("z.txt").exists());

    let _ = fs::remove_dir_all(root);
}
