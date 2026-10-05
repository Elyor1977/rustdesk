use super::*;

#[test]
fn unconfigured_proxy_allows_sync_client() {
    let client = configure_http_client!(
        SyncClient::builder(),
        TlsType::Rustls,
        false,
        SyncClient,
        None::<Socks5Server>
    );
    assert!(client.is_ok());
}

#[test]
fn invalid_configured_proxy_rejects_sync_client() {
    let proxy = Socks5Server {
        proxy: "socks5://[invalid".to_owned(),
        ..Default::default()
    };
    let client = configure_http_client!(
        SyncClient::builder(),
        TlsType::Rustls,
        false,
        SyncClient,
        Some(proxy)
    );
    assert!(
        client.is_err(),
        "Invalid proxy must not create a direct client"
    );
}

#[tokio::test]
async fn invalid_configured_proxy_rejects_async_client() {
    let proxy = Socks5Server {
        proxy: "socks5://[invalid".to_owned(),
        ..Default::default()
    };
    let client = configure_http_client!(
        AsyncClient::builder(),
        TlsType::Rustls,
        false,
        AsyncClient,
        Some(proxy)
    );
    assert!(
        client.is_err(),
        "Invalid proxy must not create a direct client"
    );
}
