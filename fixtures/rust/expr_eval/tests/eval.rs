use expr_eval::eval::{eval, EvalError, Expr};

fn n(v: i64) -> Box<Expr> {
    Box::new(Expr::Num(v))
}

#[test]
fn evaluates_arithmetic_tree() {
    // (2 + 3) * 4 = 20
    let e = Expr::Mul(Box::new(Expr::Add(n(2), n(3))), n(4));
    assert_eq!(eval(&e), Ok(20));
}

#[test]
fn divide_by_zero_is_error() {
    let e = Expr::Div(n(10), n(0));
    assert_eq!(eval(&e), Err(EvalError::DivideByZero));
}
