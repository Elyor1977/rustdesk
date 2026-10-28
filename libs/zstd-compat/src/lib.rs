pub use zstd_upstream::*;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn compression_round_trip_keeps_existing_apis() {
        let input = b"RustDesk compressed transfer";
        let mut compressor = bulk::Compressor::new(3).unwrap();
        let compressed = compressor.compress(input).unwrap();
        assert_eq!(decode_all(compressed.as_slice()).unwrap(), input);
        assert_eq!(bulk::decompress(&compressed, input.len()).unwrap(), input);
    }

    #[cfg(feature = "legacy")]
    #[test]
    fn corrupt_legacy_frame_does_not_expose_unwritten_output() {
        use zstd_safe::{DCtx, InBuffer, OutBuffer};

        // RUSTSEC-2026-0403: v0.7 magic followed by an invalid frame descriptor.
        let frame = [0x27, 0xb5, 0x2f, 0xfd, 0x08, 0x00];
        let mut decoder = DCtx::create();
        let mut bytes = Vec::with_capacity(1024);
        let mut input = InBuffer::around(&frame);
        let mut output = OutBuffer::around(&mut bytes);
        assert!(decoder.decompress_stream(&mut output, &mut input).is_err());
        assert_eq!(output.pos(), 0);
        assert_eq!(input.pos(), 0);
        assert!(bytes.is_empty());
    }
}
