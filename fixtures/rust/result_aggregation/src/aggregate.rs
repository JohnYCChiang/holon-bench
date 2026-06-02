#[derive(Debug, PartialEq, Eq)]
pub struct Summary {
    pub ok: bool,
    pub values: Vec<i32>,
    pub errors: Vec<String>,
}

pub fn aggregate(results: Vec<Result<i32, String>>) -> Summary {
    let values = results.into_iter().map(Result::unwrap).collect();
    Summary { ok: true, values, errors: Vec::new() }
}
