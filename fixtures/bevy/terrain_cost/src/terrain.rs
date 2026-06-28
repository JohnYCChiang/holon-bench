/// Count how many steps along a path a unit can take given a movement `budget`.
/// Each entry in `costs` is the cost of entering the next tile; a step is taken
/// only if the cumulative cost after entering does not exceed `budget` (the
/// boundary is inclusive -- spending exactly the budget is allowed). Counting
/// stops at the first tile that would exceed the budget.
pub fn reachable_steps(costs: &[i32], budget: i32) -> usize {
    let mut total = 0;
    let mut steps = 0;
    for &c in costs {
        total += c;
        // BUG: counts the step before checking, so the over-budget tile is entered.
        steps += 1;
        if total > budget {
            break;
        }
    }
    steps
}
