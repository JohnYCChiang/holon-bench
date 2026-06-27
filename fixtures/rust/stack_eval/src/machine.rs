#[derive(Debug, PartialEq, Eq)]
pub enum Op {
    Push(i64),
    Add,
    Sub,
    Mul,
    Dup,
}

#[derive(Debug, PartialEq, Eq)]
pub enum EvalError {
    Underflow,
    Empty,
}

/// Evaluate a tiny RPN program and return the value left on top of the stack.
pub fn eval(ops: &[Op]) -> Result<i64, EvalError> {
    let mut stack: Vec<i64> = Vec::new();
    for op in ops {
        match op {
            Op::Push(n) => stack.push(*n),
            Op::Add => {
                let b = stack.pop().unwrap();
                let a = stack.pop().unwrap();
                stack.push(a + b);
            }
            // BROKEN: operands subtracted in the wrong order.
            Op::Sub => {
                let b = stack.pop().unwrap();
                let a = stack.pop().unwrap();
                stack.push(b - a);
            }
            Op::Mul => {
                let b = stack.pop().unwrap();
                let a = stack.pop().unwrap();
                stack.push(a * b);
            }
            Op::Dup => {
                let t = *stack.last().unwrap();
                stack.push(t);
            }
        }
    }
    stack.last().copied().ok_or(EvalError::Empty)
}
