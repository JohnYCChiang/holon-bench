use module_visibility::{parse_command, Command};

#[test]
fn parse_command_is_public_facade() {
    assert_eq!(
        parse_command("run alpha beta"),
        Command {
            name: "run".to_string(),
            args: vec!["alpha".to_string(), "beta".to_string()]
        }
    );
}
