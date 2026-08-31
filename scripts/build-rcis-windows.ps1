[CmdletBinding()]
param(
    [string]$RepositoryPath = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepositoryPath = (Resolve-Path -LiteralPath $RepositoryPath).Path
$PythonPath = Join-Path $RepositoryPath '.venv\Scripts\python.exe'
$SpecPath = Join-Path $RepositoryPath 'packaging\windows\rcis.spec'
$InstallerScript = Join-Path $RepositoryPath 'packaging\windows\RCIS.iss'
$DistRoot = Join-Path $RepositoryPath 'dist'
$WorkRoot = Join-Path $RepositoryPath 'build\pyinstaller'
$BootstrapRoot = Join-Path $WorkRoot 'bootstrap'
$BootstrapPath = Join-Path $BootstrapRoot 'rcis_pyinstaller_bootstrap.py'
$AppDist = Join-Path $DistRoot 'RCIS'
$AppExe = Join-Path $AppDist 'RCIS.exe'
$InstallerOutputDir = Join-Path $DistRoot 'installer'
$InstallerExe = Join-Path $InstallerOutputDir 'RCIS-Setup.exe'
$SmokeMarker = Join-Path $WorkRoot 'rcis-packaging-smoke.txt'

function Resolve-Iscc {
    $Command = Get-Command 'ISCC.exe' -ErrorAction SilentlyContinue
    if ($null -ne $Command) { return $Command.Source }

    $Candidates = @(
        (Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 6\ISCC.exe'),
        (Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'),
        (Join-Path $env:ProgramFiles 'Inno Setup 6\ISCC.exe')
    )
    foreach ($Candidate in $Candidates) {
        if ($Candidate -and (Test-Path -LiteralPath $Candidate -PathType Leaf)) {
            return $Candidate
        }
    }
    throw 'Inno Setup 6 compiler ISCC.exe was not found. Install the approved build toolchain before running this build.'
}

if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
    throw "Repository build Python missing: $PythonPath"
}
foreach ($Required in @($SpecPath, $InstallerScript)) {
    if (-not (Test-Path -LiteralPath $Required -PathType Leaf)) {
        throw "Required packaging artifact missing: $Required"
    }
}

foreach ($OutputPath in @($AppDist, $WorkRoot, $InstallerOutputDir)) {
    if (Test-Path -LiteralPath $OutputPath) {
        throw "Refusing to overwrite existing build output: $OutputPath"
    }
}

& $PythonPath -m PyInstaller --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw 'PyInstaller is not available in the repository build environment. This script never installs dependencies or uses the network.'
}

$IsccPath = Resolve-Iscc

& $PythonPath -m pytest -q -p no:cacheprovider tests/packaging/test_windows_packaging_contract.py
if ($LASTEXITCODE -ne 0) { throw 'Packaging contract tests failed.' }

New-Item -ItemType Directory -Path $BootstrapRoot -Force | Out-Null
$BootstrapSource = @'
from rie.ui.windows_gui_entrypoint import main

if __name__ == "__main__":
    main()
'@
[System.IO.File]::WriteAllText(
    $BootstrapPath,
    ($BootstrapSource.Trim() + "`n"),
    [System.Text.UTF8Encoding]::new($false)
)

$PreviousBootstrap = $env:RCIS_PYINSTALLER_BOOTSTRAP_PATH
try {
    $env:RCIS_PYINSTALLER_BOOTSTRAP_PATH = $BootstrapPath
    & $PythonPath -m PyInstaller --noconfirm --distpath $DistRoot --workpath $WorkRoot $SpecPath
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed.' }
}
finally {
    if ($null -eq $PreviousBootstrap) {
        Remove-Item Env:RCIS_PYINSTALLER_BOOTSTRAP_PATH -ErrorAction SilentlyContinue
    } else {
        $env:RCIS_PYINSTALLER_BOOTSTRAP_PATH = $PreviousBootstrap
    }
}

if (-not (Test-Path -LiteralPath $AppExe -PathType Leaf)) { throw "RCIS.exe missing after build: $AppExe" }
if (Test-Path -LiteralPath $SmokeMarker) { throw "Unexpected pre-existing smoke marker: $SmokeMarker" }

$PreviousSmoke = $env:RCIS_PACKAGING_SMOKE_TEST
$PreviousSmokeMarker = $env:RCIS_PACKAGING_SMOKE_MARKER_PATH
try {
    $env:RCIS_PACKAGING_SMOKE_TEST = '1'
    $env:RCIS_PACKAGING_SMOKE_MARKER_PATH = $SmokeMarker
    $SmokeProcess = Start-Process -FilePath $AppExe -Wait -PassThru
    if ($SmokeProcess.ExitCode -ne 0) { throw "Bundled RCIS.exe smoke test failed with exit code $($SmokeProcess.ExitCode)." }
    if (-not (Test-Path -LiteralPath $SmokeMarker -PathType Leaf)) { throw "Bundled RCIS.exe smoke marker missing: $SmokeMarker" }
    $SmokeValue = (Get-Content -LiteralPath $SmokeMarker -Raw).Trim()
    if ($SmokeValue -ne 'RCIS_PACKAGING_SMOKE_OK') { throw "Unexpected RCIS.exe smoke marker: $SmokeValue" }
}
finally {
    if ($null -eq $PreviousSmoke) {
        Remove-Item Env:RCIS_PACKAGING_SMOKE_TEST -ErrorAction SilentlyContinue
    } else {
        $env:RCIS_PACKAGING_SMOKE_TEST = $PreviousSmoke
    }
    if ($null -eq $PreviousSmokeMarker) {
        Remove-Item Env:RCIS_PACKAGING_SMOKE_MARKER_PATH -ErrorAction SilentlyContinue
    } else {
        $env:RCIS_PACKAGING_SMOKE_MARKER_PATH = $PreviousSmokeMarker
    }
}

& $IsccPath $InstallerScript
if ($LASTEXITCODE -ne 0) { throw 'Inno Setup compilation failed.' }
if (-not (Test-Path -LiteralPath $InstallerExe -PathType Leaf)) { throw "Installer missing after build: $InstallerExe" }

Write-Host "RCIS_EXE=$AppExe"
Write-Host "RCIS_INSTALLER=$InstallerExe"
