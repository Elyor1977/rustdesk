# Release signing

Store signing material only in repository Actions secrets under **Settings → Secrets and variables → Actions**.

## Windows

Use a code-signing certificate exported as a password-protected PFX with its private key.

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes('certificate.pfx')) | Set-Clipboard
```

Create these secrets:

- `WINDOWS_CERTIFICATE_BASE64`: clipboard value from the command above.
- `WINDOWS_CERTIFICATE_PASSWORD`: PFX export password.
- `WINDOWS_CERTIFICATE_THUMBPRINT`: expected 40-character certificate thumbprint.

Read the thumbprint before uploading the certificate:

```powershell
$password = Read-Host -AsSecureString
(Get-PfxData -FilePath 'certificate.pfx' -Password $password).EndEntityCertificates.Thumbprint
```

The Windows workflow signs EXE, DLL, and MSI files with SHA-256 and a trusted timestamp.

## Android

Create the release keystore once and keep it backed up securely:

```powershell
keytool -genkeypair -v -keystore rustdesk-release.jks -alias rustdesk -keyalg RSA -keysize 4096 -validity 10000
[Convert]::ToBase64String([IO.File]::ReadAllBytes('rustdesk-release.jks')) | Set-Clipboard
```

Create these secrets:

- `ANDROID_SIGNING_KEY`: clipboard value from the command above.
- `ANDROID_ALIAS`: keystore alias, for example `rustdesk`.
- `ANDROID_KEY_STORE_PASSWORD`: keystore password.
- `ANDROID_KEY_PASSWORD`: key password.
- `ANDROID_CERT_SHA256`: SHA-256 certificate fingerprint shown by the command below.

```powershell
keytool -list -v -keystore rustdesk-release.jks -alias rustdesk
```

Copy only the 64 hexadecimal characters after `SHA256:`. Colons and the
`SHA256:` prefix are also accepted by the workflow. Do not use the SHA-1
fingerprint or the SHA-256 hash of the `.jks` file.

Never replace or lose the Android keystore after publishing an application. Updates must use the same signing key.

## Protected release

Create a GitHub Environment named `release` under **Settings → Environments** and require manual approval. Protect tags matching `v*` with a repository ruleset. A version tag waits for approval before any signing or publication starts.

## Manual builds

Run workflows independently under **Actions**:

- `Windows unsigned` or `Windows signed`.
- `Android unsigned` or `Android signed`.
- `Linux unsigned`, `macOS unsigned`, or `iOS unsigned`.
- `All platforms unsigned` only when every unsigned platform is needed.

Signed workflows wait for approval from the `release` environment. Unsigned workflows do not receive signing secrets and never publish a GitHub release.
