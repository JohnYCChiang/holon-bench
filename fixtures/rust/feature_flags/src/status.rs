pub fn format_status(ok: bool, detail: &str) -> String {
    format!("ok={ok};detail={detail}")
}
