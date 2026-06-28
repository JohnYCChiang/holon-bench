pub fn render_table(input: &str) -> String {
    let rows: Vec<Vec<String>> = input
        .split('\n')
        .filter(|l| !l.trim().is_empty())
        .map(|l| l.split('|').map(|c| c.trim().to_string()).collect())
        .collect();
    let ncol = rows.iter().map(|r| r.len()).max().unwrap_or(0);
    let rows: Vec<Vec<String>> = rows
        .into_iter()
        .map(|mut r| {
            while r.len() < ncol {
                r.push(String::new());
            }
            r
        })
        .collect();
    let widths: Vec<usize> = (0..ncol)
        .map(|i| rows.iter().map(|r| r[i].chars().count()).max().unwrap_or(0))
        .collect();
    let fmt = |r: &Vec<String>| -> String { r.join(" | ") };
    let mut lines = vec![fmt(&rows[0])];
    lines.push(
        (0..ncol)
            .map(|i| "-".repeat(widths[i]))
            .collect::<Vec<_>>()
            .join("-+-"),
    );
    for r in &rows[1..] {
        lines.push(fmt(r));
    }
    lines
        .iter()
        .map(|l| l.trim_end().to_string())
        .collect::<Vec<_>>()
        .join("\n")
}
