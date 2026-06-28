const ALPHABET: &[u8; 32] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";

pub fn b32encode(input: &str) -> String {
    let data = input.as_bytes();
    let mut out = String::new();
    for chunk in data.chunks(5) {
        let n = chunk.len();
        let out_chars = match n {
            1 => 2,
            2 => 4,
            3 => 5,
            4 => 7,
            _ => 8,
        };
        let mut bits: u64 = 0;
        for i in 0..5 {
            let b = if i < n { chunk[i] } else { 0 };
            bits = (bits << 8) | b as u64;
        }
        let mut group = [0u8; 8];
        for (i, slot) in group.iter_mut().enumerate() {
            let shift = 35 - i * 5;
            let idx = ((bits >> shift) & 0x1f) as usize;
            *slot = ALPHABET[idx];
        }
        for &g in group.iter().take(out_chars) {
            out.push(g as char);
        }
    }
    out
}
