use stack_eval::machine::{eval, EvalError, Op};

#[test]
fn add_and_sub_order() {
    assert_eq!(eval(&[Op::Push(5), Op::Push(3), Op::Add]), Ok(8));
    assert_eq!(eval(&[Op::Push(5), Op::Push(3), Op::Sub]), Ok(2));
}

#[test]
fn underflow_and_empty() {
    assert_eq!(eval(&[Op::Add]), Err(EvalError::Underflow));
    assert_eq!(eval(&[]), Err(EvalError::Empty));
}
