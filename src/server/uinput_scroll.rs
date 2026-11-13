pub(super) fn horizontal_scroll_steps(length: i32) -> Option<u32> {
    let steps = length.unsigned_abs();
    // Each tick writes to uinput; bound the work from one peer-controlled event.
    (steps <= 1_000).then_some(steps)
}

#[cfg(test)]
mod tests {
    use super::horizontal_scroll_steps;

    #[test]
    fn preserves_normal_horizontal_scroll_magnitude() {
        for length in [0_i32, -1, 1, -120, 120, -1_000, 1_000] {
            assert_eq!(horizontal_scroll_steps(length), Some(length.unsigned_abs()));
        }
    }

    #[test]
    fn rejects_excessive_horizontal_scroll() {
        for length in [-1_001, 1_001, i32::MIN, i32::MAX] {
            assert_eq!(horizontal_scroll_steps(length), None, "length={length}");
        }
    }
}
