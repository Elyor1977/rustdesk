param(
    [Parameter(Mandatory = $true)]
    [string]$Path
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($env:WINDOWS_CERTIFICATE_BASE64)) {
    throw "WINDOWS_CERTIFICATE_BASE64 is required"
}
if ([string]::IsNullOrWhiteSpace($env:WINDOWS_CERTIFICATE_PASSWORD)) {
    throw "WINDOWS_CERTIFICATE_PASSWORD is required"
}

$target = (Resolve-Path -LiteralPath $Path).Path
$files = if ((Get-Item -LiteralPath $target).PSIsContainer) {
    @(Get-ChildItem -LiteralPath $target -Recurse -File | Where-Object {
        $_.Extension -in '.exe', '.dll', '.msi' -and
        ($_.Extension -eq '.exe' -or $_.FullName -notmatch '\\(RustDeskPrinterDriver|usbmmidd_v2)\\')
    })
} else {
    @(Get-Item -LiteralPath $target)
}
if ($files.Count -eq 0) {
    throw "No Windows binaries found in $Path"
}

$signTool = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin" -Filter signtool.exe -Recurse |
    Where-Object FullName -Match '\\x64\\signtool\.exe$' |
    Sort-Object FullName -Descending |
    Select-Object -First 1
if (-not $signTool) {
    throw "signtool.exe was not found"
}

$pfxPath = Join-Path $env:RUNNER_TEMP "windows-signing.pfx"
$importedCertificates = @()
try {
    [IO.File]::WriteAllBytes($pfxPath, [Convert]::FromBase64String($env:WINDOWS_CERTIFICATE_BASE64))
    $password = ConvertTo-SecureString $env:WINDOWS_CERTIFICATE_PASSWORD -AsPlainText -Force
    $importedCertificates = @(Import-PfxCertificate -FilePath $pfxPath -CertStoreLocation Cert:\CurrentUser\My -Password $password)
    $certificate = $importedCertificates | Where-Object HasPrivateKey | Select-Object -First 1
    if (-not $certificate) {
        throw "The Windows signing certificate has no private key"
    }

    foreach ($file in $files) {
        & $signTool.FullName sign /sha1 $certificate.Thumbprint /s My /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 $file.FullName
        if ($LASTEXITCODE -ne 0) {
            throw "Signing failed: $($file.Name)"
        }
    }
} finally {
    foreach ($importedCertificate in $importedCertificates) {
        Remove-Item -LiteralPath "Cert:\CurrentUser\My\$($importedCertificate.Thumbprint)" -Force -ErrorAction SilentlyContinue
    }
    Remove-Item -LiteralPath $pfxPath -Force -ErrorAction SilentlyContinue
}
