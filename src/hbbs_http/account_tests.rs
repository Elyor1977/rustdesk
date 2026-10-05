use super::*;
use std::{io::Read, net::TcpListener, sync::mpsc, thread};

#[test]
fn stalled_tls_probe_does_not_block_auth_cancel_or_result() {
    assert!(
        hbb_common::config::Config::get_socks().is_none(),
        "Run account tests with a clean RustDesk configuration (no configured proxy)"
    );
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    let api_server = format!("https://{}", listener.local_addr().unwrap());
    let (ready_tx, ready_rx) = mpsc::channel();
    let (release_tx, release_rx) = mpsc::channel();
    let server = thread::spawn(move || {
        let (mut stream, _) = listener.accept().unwrap();
        stream
            .set_read_timeout(Some(Duration::from_secs(10)))
            .unwrap();
        assert!(stream.read(&mut [0; 1024]).unwrap() > 0);
        ready_tx.send(()).unwrap();
        let _ = release_rx.recv_timeout(Duration::from_secs(10));
    });
    let probe = thread::spawn(move || OidcSession::ensure_client(&api_server));
    ready_rx.recv_timeout(Duration::from_secs(10)).unwrap();
    let (result_tx, result_rx) = mpsc::channel();
    let cancel = thread::spawn(move || {
        OidcSession::auth_cancel();
        result_tx.send(OidcSession::get_result()).unwrap();
    });
    let result = result_rx.recv_timeout(Duration::from_secs(1));
    release_tx.send(()).unwrap();
    server.join().unwrap();
    probe.join().unwrap().unwrap();
    cancel.join().unwrap();
    assert!(
        result.is_ok(),
        "Account cancellation/result must remain available during the HTTP probe"
    );
}
