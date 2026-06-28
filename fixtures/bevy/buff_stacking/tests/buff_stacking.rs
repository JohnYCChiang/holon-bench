use buff_stacking::buffs::{apply, ActiveBuff, BuffDef, BuffKind};

#[test]
fn refresh_buff_does_not_duplicate() {
    let def = BuffDef { id: 1, kind: BuffKind::Refresh, max_stacks: 1 };
    let mut active: Vec<ActiveBuff> = Vec::new();
    apply(&mut active, &def, 5.0);
    apply(&mut active, &def, 8.0);
    assert_eq!(active.len(), 1);
    assert_eq!(active[0].stacks, 1);
    assert_eq!(active[0].duration, 8.0);
}

#[test]
fn stack_buff_accumulates_stacks() {
    let def = BuffDef { id: 2, kind: BuffKind::Stack, max_stacks: 3 };
    let mut active: Vec<ActiveBuff> = Vec::new();
    apply(&mut active, &def, 4.0);
    apply(&mut active, &def, 4.0);
    assert_eq!(active.len(), 1);
    assert_eq!(active[0].stacks, 2);
}
