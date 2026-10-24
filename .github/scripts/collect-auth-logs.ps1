param(
    [string]$OutputPath = (Join-Path ([Environment]::GetFolderPath('Desktop')) ("RustDesk-auth-{0}.txt" -f (Get-Date -Format 'yyyyMMdd-HHmmss-fff')))
)

$ErrorActionPreference = 'Stop'
$roots = @(
    (Join-Path $env:APPDATA 'RustDesk/log'),
    (Join-Path $env:WINDIR 'ServiceProfiles/LocalService/AppData/Roaming/RustDesk/log'),
    (Join-Path $env:WINDIR 'System32/config/systemprofile/AppData/Roaming/RustDesk/log')
)
$outputStream = [IO.FileStream]::new($OutputPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write)
$writer = [IO.StreamWriter]::new($outputStream, [Text.UTF8Encoding]::new($false))
try {
    foreach ($root in $roots) {
        foreach ($relative in @('RustDesk_rCURRENT.log', 'server/RustDesk_rCURRENT.log', 'cm/RustDesk_rCURRENT.log')) {
            $path = Join-Path $root $relative
            if (-not (Test-Path -LiteralPath $path)) { continue }
            $stream = [IO.FileStream]::new($path, [IO.FileMode]::Open, [IO.FileAccess]::Read, ([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete))
            $reader = [IO.StreamReader]::new($stream)
            try {
                $writer.WriteLine("FILE: $path")
                while ($null -ne ($line = $reader.ReadLine())) {
                    if ($line -match '\[auth-diag\]|Connection closed:|Reset by the peer') {
                        $writer.WriteLine($line)
                    }
                }
            } finally {
                $reader.Dispose()
            }
        }
    }
} finally {
    $writer.Dispose()
}
Write-Output $OutputPath
