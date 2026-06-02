use dry_run_delete::delete::{delete_paths, DeleteReport};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

fn format_report(report: DeleteReport) -> String {
    format!(
        "deleted={};would={};skipped={}",
        report.deleted,
        report.would_delete.join(","),
        report.skipped.join(",")
    )
}

fn python(root: &Path, dry_run: bool, names: &[&str]) -> String {
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../python/reference.py");
    let mut command = Command::new("python3");
    command.arg(script).arg(if dry_run { "true" } else { "false" });
    for name in names {
        command.arg(root.join(name));
    }
    let output = command.output().unwrap();
    assert!(output.status.success());
    String::from_utf8(output.stdout).unwrap().trim().to_string()
}

#[test]
fn dry_run_does_not_delete_and_matches_python_report() {
    let root = std::env::temp_dir().join(format!("holon-delete-{}", std::process::id()));
    let _ = fs::remove_dir_all(&root);
    fs::create_dir_all(&root).unwrap();
    fs::write(root.join("b.txt"), "b").unwrap();
    fs::write(root.join("a.txt"), "a").unwrap();
    let paths: Vec<PathBuf> = ["b.txt", "missing.txt", "a.txt"].iter().map(|p| root.join(p)).collect();
    assert_eq!(format_report(delete_paths(&paths, true)), python(&root, true, &["b.txt", "missing.txt", "a.txt"]));
    assert!(root.join("a.txt").exists());
    assert!(root.join("b.txt").exists());
    let _ = fs::remove_dir_all(root);
}
