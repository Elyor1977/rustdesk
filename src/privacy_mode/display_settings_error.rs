pub(crate) fn describe(rc: i32) -> String {
    // ChangeDisplaySettingsEx reports DISP_CHANGE_* directly, not GetLastError.
    let name = match rc {
        0 => "DISP_CHANGE_SUCCESSFUL",
        1 => "DISP_CHANGE_RESTART",
        -1 => "DISP_CHANGE_FAILED",
        -2 => "DISP_CHANGE_BADMODE",
        -3 => "DISP_CHANGE_NOTUPDATED",
        -4 => "DISP_CHANGE_BADFLAGS",
        -5 => "DISP_CHANGE_BADPARAM",
        -6 => "DISP_CHANGE_BADDUALVIEW",
        _ => "unknown display change result",
    };
    format!("ret: {} ({})", rc, name)
}

#[cfg(test)]
mod tests {
    use super::describe;

    #[test]
    fn failed_display_change_reports_its_own_result() {
        assert_eq!(describe(-1), "ret: -1 (DISP_CHANGE_FAILED)");
    }

    #[test]
    fn unsupported_display_mode_is_identified() {
        assert_eq!(describe(-2), "ret: -2 (DISP_CHANGE_BADMODE)");
    }
}
