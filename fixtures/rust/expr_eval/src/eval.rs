#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Expr {
    Num(i64),
    Add(Box<Expr>, Box<Expr>),
    Sub(Box<Expr>, Box<Expr>),
    Mul(Box<Expr>, Box<Expr>),
    Div(Box<Expr>, Box<Expr>),
}

#[derive(Debug, PartialEq, Eq)]
pub enum EvalError {
    DivideByZero,
}

pub fn eval(expr: &Expr) -> Result<i64, EvalError> {
    // BROKEN: only handles literals, everything else collapses to zero.
    match expr {
        Expr::Num(n) => Ok(*n),
        _ => Ok(0),
    }
}
