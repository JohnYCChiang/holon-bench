use plugin_ordering::plugin::{register_game_plugin, AppSchedule};

#[test]
fn startup_systems_are_registered_once_in_dependency_order() {
    let mut schedule = AppSchedule::default();
    register_game_plugin(&mut schedule);

    assert_eq!(schedule.startup, vec!["init_assets", "spawn_gameplay", "setup_ui"]);
}
