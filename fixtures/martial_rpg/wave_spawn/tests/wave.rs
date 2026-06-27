use martial_wave::WaveSpawner;

fn total_cost(plan: &[usize], costs: &[u32]) -> u32 {
    plan.iter().map(|&i| costs[i]).sum()
}

#[test]
fn plan_respects_budget() {
    let costs = [3u32, 5, 7];
    let mut s = WaveSpawner::new(1);
    let plan = s.plan(10, &costs);
    assert!(total_cost(&plan, &costs) <= 10, "over budget: {:?}", plan);
    assert!(!plan.is_empty(), "nothing spawned within budget");
}

#[test]
fn plan_is_deterministic_and_stateless() {
    let costs = [4u32, 6];
    let mut a = WaveSpawner::new(7);
    let p1 = a.plan(20, &costs);
    let p2 = a.plan(20, &costs);
    assert_eq!(p1, p2, "plan changed across calls (order-dependent state)");
}

#[test]
fn empty_when_nothing_affordable() {
    let mut s = WaveSpawner::new(3);
    assert!(s.plan(2, &[5, 9]).is_empty());
    assert!(s.plan(0, &[1, 2]).is_empty());
    assert!(s.plan(50, &[]).is_empty());
}
