Set-StrictMode -Version Latest

function ConvertTo-RcisWindowsCommandLineArgument {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$Value
    )

    if ($Value.Length -eq 0) {
        return '""'
    }

    if ($Value -notmatch '[\s"]') {
        return $Value
    }

    $Builder = New-Object System.Text.StringBuilder
    [void]$Builder.Append('"')
    $BackslashCount = 0

    foreach ($Character in $Value.ToCharArray()) {
        if ([int][char]$Character -eq 92) {
            $BackslashCount += 1
            continue
        }

        if ($Character -eq '"') {
            if ($BackslashCount -gt 0) {
                [void]$Builder.Append(('\' * ($BackslashCount * 2)))
            }
            [void]$Builder.Append('\')
            [void]$Builder.Append('"')
            $BackslashCount = 0
            continue
        }

        if ($BackslashCount -gt 0) {
            [void]$Builder.Append(('\' * $BackslashCount))
            $BackslashCount = 0
        }

        [void]$Builder.Append($Character)
    }

    if ($BackslashCount -gt 0) {
        [void]$Builder.Append(('\' * ($BackslashCount * 2)))
    }

    [void]$Builder.Append('"')
    return $Builder.ToString()
}

function ConvertTo-RcisArgumentArray {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [object]$Values
    )

    $Result = @()

    if ($Values -is [string]) {
        return ,([string]$Values)
    }

    foreach ($Value in $Values) {
        $Result += [string]$Value
    }

    return ,$Result
}

function Join-RcisWindowsCommandLine {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [object]$Values
    )

    $Parts = @()
    foreach ($Value in (ConvertTo-RcisArgumentArray -Values $Values)) {
        $Parts += ConvertTo-RcisWindowsCommandLineArgument -Value $Value
    }

    return [string]::Join(' ', $Parts)
}

function Invoke-RcisGitText {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepositoryRoot,

        [Parameter(Mandatory = $true)]
        [object]$GitArguments
    )

    if (-not (Test-Path -LiteralPath $RepositoryRoot -PathType Container)) {
        throw "Repository root does not exist: $RepositoryRoot"
    }

    $AllArguments = @('-C', $RepositoryRoot)
    foreach ($Argument in (ConvertTo-RcisArgumentArray -Values $GitArguments)) {
        $AllArguments += $Argument
    }

    $StartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $StartInfo.FileName = 'git.exe'
    $StartInfo.Arguments = Join-RcisWindowsCommandLine -Values $AllArguments
    $StartInfo.WorkingDirectory = $RepositoryRoot
    $StartInfo.UseShellExecute = $false
    $StartInfo.CreateNoWindow = $true
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true

    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $StartInfo

    try {
        if (-not $Process.Start()) {
            throw 'Failed to start git.exe.'
        }

        $Stdout = $Process.StandardOutput.ReadToEnd()
        $Stderr = $Process.StandardError.ReadToEnd()
        $Process.WaitForExit()
        $ExitCode = $Process.ExitCode
    }
    finally {
        $Process.Dispose()
    }

    return [pscustomobject]@{
        ExitCode = $ExitCode
        Stdout   = $Stdout
        Stderr   = $Stderr
    }
}

function Invoke-RcisGitQuiet {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepositoryRoot,

        [Parameter(Mandatory = $true)]
        [object]$GitArguments
    )

    $Result = Invoke-RcisGitText -RepositoryRoot $RepositoryRoot -GitArguments $GitArguments
    if ($Result.ExitCode -eq 0) {
        return $true
    }
    if ($Result.ExitCode -eq 1) {
        return $false
    }

    throw "git.exe failed with exit code $($Result.ExitCode): $($Result.Stderr)"
}

function Get-RcisFileIdentity {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$LiteralPath
    )

    $Item = Get-Item -LiteralPath $LiteralPath -ErrorAction Stop
    if ($Item.PSIsContainer) {
        throw "Expected a file, found a directory: $LiteralPath"
    }

    $Stream = [System.IO.File]::Open(
        $Item.FullName,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::Read
    )
    $Sha = [System.Security.Cryptography.SHA256]::Create()

    try {
        $Digest = $Sha.ComputeHash($Stream)
    }
    finally {
        $Sha.Dispose()
        $Stream.Dispose()
    }

    $Hex = ([System.BitConverter]::ToString($Digest)).Replace('-', '').ToLowerInvariant()

    return [pscustomobject]@{
        Path   = $Item.FullName
        Bytes  = [int64]$Item.Length
        SHA256 = $Hex
    }
}

function Get-RcisGitOneLine {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepositoryRoot,

        [Parameter(Mandatory = $true)]
        [object]$GitArguments
    )

    $Result = Invoke-RcisGitText -RepositoryRoot $RepositoryRoot -GitArguments $GitArguments
    if ($Result.ExitCode -ne 0) {
        throw "git.exe failed with exit code $($Result.ExitCode): $($Result.Stderr)"
    }

    $Normalized = $Result.Stdout.Replace("`r`n", "`n").Replace("`r", "`n")
    $Lines = @(
        $Normalized.Split([char]10) |
            Where-Object { $_.Length -gt 0 }
    )

    if ($Lines.Count -ne 1) {
        throw "Expected exactly one non-empty git output line; observed $($Lines.Count)."
    }

    return [string]$Lines[0]
}

function Export-RcisGitBlobExact {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepositoryRoot,

        [Parameter(Mandatory = $true)]
        [string]$ObjectId,

        [Parameter(Mandatory = $true)]
        [string]$DestinationPath
    )

    $ObjectType = Get-RcisGitOneLine `
        -RepositoryRoot $RepositoryRoot `
        -GitArguments @('cat-file', '-t', $ObjectId)

    if ($ObjectType -cne 'blob') {
        throw "Git object is not a blob: $ObjectId"
    }

    $Destination = [System.IO.Path]::GetFullPath($DestinationPath)
    $Parent = [System.IO.Path]::GetDirectoryName($Destination)
    if (-not (Test-Path -LiteralPath $Parent -PathType Container)) {
        throw "Destination parent does not exist: $Parent"
    }

    $AllArguments = @('-C', $RepositoryRoot, 'cat-file', 'blob', $ObjectId)

    $StartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $StartInfo.FileName = 'git.exe'
    $StartInfo.Arguments = Join-RcisWindowsCommandLine -Values $AllArguments
    $StartInfo.WorkingDirectory = $RepositoryRoot
    $StartInfo.UseShellExecute = $false
    $StartInfo.CreateNoWindow = $true
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true

    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $StartInfo
    $FileStream = $null

    try {
        if (-not $Process.Start()) {
            throw 'Failed to start git.exe.'
        }

        $FileStream = [System.IO.File]::Open(
            $Destination,
            [System.IO.FileMode]::Create,
            [System.IO.FileAccess]::Write,
            [System.IO.FileShare]::None
        )

        $Process.StandardOutput.BaseStream.CopyTo($FileStream)
        $FileStream.Flush()
        $FileStream.Dispose()
        $FileStream = $null

        $Stderr = $Process.StandardError.ReadToEnd()
        $Process.WaitForExit()
        $ExitCode = $Process.ExitCode

        if ($ExitCode -ne 0) {
            if (Test-Path -LiteralPath $Destination -PathType Leaf) {
                Remove-Item -LiteralPath $Destination -Force
            }
            throw "git.exe cat-file failed with exit code ${ExitCode}: $Stderr"
        }
    }
    finally {
        if ($null -ne $FileStream) {
            $FileStream.Dispose()
        }
        $Process.Dispose()
    }

    return Get-RcisFileIdentity -LiteralPath $Destination
}

function Test-RcisTrackedWorktreeAndIndexClean {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepositoryRoot
    )

    $TrackedStateMatchesHead = Invoke-RcisGitQuiet `
        -RepositoryRoot $RepositoryRoot `
        -GitArguments @('diff', '--quiet', '--exit-code', 'HEAD', '--')

    $IndexMatchesHead = Invoke-RcisGitQuiet `
        -RepositoryRoot $RepositoryRoot `
        -GitArguments @('diff', '--cached', '--quiet', '--exit-code', 'HEAD', '--')

    return ($TrackedStateMatchesHead -and $IndexMatchesHead)
}

function Test-RcisIndexMatchesWorktree {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepositoryRoot
    )

    return Invoke-RcisGitQuiet `
        -RepositoryRoot $RepositoryRoot `
        -GitArguments @('diff', '--quiet', '--exit-code', '--')
}

Export-ModuleMember -Function @(
    'Get-RcisFileIdentity',
    'Get-RcisGitOneLine',
    'Export-RcisGitBlobExact',
    'Test-RcisTrackedWorktreeAndIndexClean',
    'Test-RcisIndexMatchesWorktree'
)
