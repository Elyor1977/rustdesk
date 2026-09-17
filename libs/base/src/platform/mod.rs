#[cfg(target_os = "linux")]
pub mod linux;

#[cfg(target_os = "macos")]
pub mod macos;

#[cfg(target_os = "windows")]
pub mod windows;

// Exit code conventionally used for a SIGSEGV-terminated process (128 + 11).
#[cfg(all(unix, not(debug_assertions)))]
const BREAKDOWN_EXIT_CODE: libc::c_int = 139;

#[cfg(not(debug_assertions))]
const BREAKDOWN_MESSAGE: &[u8] = b"RustDesk: got SIGSEGV, exiting.\n";

// SAFETY: this function runs in signal context, so it must be
// async-signal-safe: no allocations, no locks, no logging, no config access,
// no backtrace walking and no user callbacks. Only `write(2)` to stderr with a
// fixed buffer and `_exit(2)` are used here.
#[cfg(not(debug_assertions))]
extern "C" fn breakdown_signal_handler(_sig: i32) {
    unsafe {
        // fd 2 == stderr on every supported platform.
        libc::write(
            2,
            BREAKDOWN_MESSAGE.as_ptr() as *const libc::c_void,
            BREAKDOWN_MESSAGE.len() as _,
        );
        #[cfg(unix)]
        libc::_exit(BREAKDOWN_EXIT_CODE);
        // `_exit` is not exposed by the libc crate on Windows; abort() does
        // not run atexit handlers either and yields a non-zero exit status.
        #[cfg(not(unix))]
        std::process::abort();
    }
}

/// Register a SIGSEGV handler that terminates the process with a fixed
/// message and a non-zero exit code.
///
/// The `callback` is accepted for API compatibility only: it is intentionally
/// not invoked from the signal handler, because arbitrary Rust code is not
/// async-signal-safe (it may allocate, take locks or re-enter the crashed
/// code). Cleanup that must happen after a crash should be done on the next
/// start-up instead.
#[cfg(not(debug_assertions))]
pub fn register_breakdown_handler<T>(_callback: T)
where
    T: Fn() + 'static,
{
    unsafe {
        libc::signal(
            libc::SIGSEGV,
            breakdown_signal_handler as libc::sighandler_t,
        );
    }
}
