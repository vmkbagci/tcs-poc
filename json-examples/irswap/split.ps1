#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Split a single "TRADE N — Name" document into one JSON file per trade.

.USAGE
  pwsh ./split-trades.ps1 -Path ./trades.txt

.NOTES
  - Output files are created in the same folder as the input file (unless -OutputDir is provided).
  - Filenames are slugified from the trade name (text after the dash), with parentheses stripped.
  - Code fences ``` are ignored if present.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string] $Path,

  [Parameter(Mandatory = $false)]
  [string] $OutputDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $Path)) {
  throw "Input file not found: $Path"
}

$resolvedPath = (Resolve-Path -LiteralPath $Path).Path
if (-not $OutputDir -or [string]::IsNullOrWhiteSpace($OutputDir)) {
  $OutputDir = Split-Path -Parent $resolvedPath
}
if (-not (Test-Path -LiteralPath $OutputDir)) {
  New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# Header supports both Unicode em dash (—) and plain hyphen (-)
$headerRegex   = '^\s*TRADE\s+\d+\s+[—-]\s+(?<name>.+?)\s*$'
$codeFenceRegex = '^\s*```'

function Get-Slug([string] $s) {
  $t = $s.ToLowerInvariant()
  # Replace non-alphanumeric with hyphen
  $t = [regex]::Replace($t, '[^a-z0-9]+', '-')
  $t = $t.Trim('-')
  if ([string]::IsNullOrWhiteSpace($t)) { $t = "trade" }
  if ($t.Length -gt 60) { $t = $t.Substring(0, 60).Trim('-') }
  return $t
}

# Ensure UTF-8 without BOM
$Utf8NoBom = [System.Text.UTF8Encoding]::new($false)

$slugCounts = @{}
$currentName = $null
$currentSlug = $null
$capture = $false
$buffer = New-Object System.Collections.Generic.List[string]

function Flush-Trade {
  param([string] $name, [System.Collections.Generic.List[string]] $lines)

  if ([string]::IsNullOrWhiteSpace($name)) { return }
  if ($lines.Count -eq 0) { return }

  # Strip any trailing non-JSON junk (rare) by trimming empty lines at end
  while ($lines.Count -gt 0 -and [string]::IsNullOrWhiteSpace($lines[$lines.Count - 1])) {
    $lines.RemoveAt($lines.Count - 1)
  }

  $base = $name -replace '\s*\(.*$', ''   # drop parentheses suffix
  $base = $base.Trim()

  $slug = Get-Slug $base
  if (-not $slugCounts.ContainsKey($slug)) { $slugCounts[$slug] = 0 }
  $slugCounts[$slug]++
  $n = $slugCounts[$slug]

  $fileName = if ($n -gt 1) { "$slug-$n.json" } else { "$slug.json" }
  $outPath = Join-Path $OutputDir $fileName

  $content = ($lines -join "`n") + "`n"
  [System.IO.File]::WriteAllText($outPath, $content, $Utf8NoBom)

  Write-Host "Wrote $outPath"
}

# Read input line-by-line
foreach ($line in Get-Content -LiteralPath $resolvedPath) {

  if ($line -match $codeFenceRegex) {
    continue
  }

  if ($line -match $headerRegex) {
    # flush previous trade
    Flush-Trade -name $currentName -lines $buffer

    # start new trade
    $currentName = $Matches["name"]
    $buffer = New-Object System.Collections.Generic.List[string]
    $capture = $false
    continue
  }

  if (-not $currentName) {
    continue
  }

  if (-not $capture) {
    if ($line -match '^\s*\{') {
      $capture = $true
      $buffer.Add($line)
    }
    continue
  }

  $buffer.Add($line)
}

# flush last
Flush-Trade -name $currentName -lines $buffer

