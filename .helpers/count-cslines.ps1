<#
.SYNOPSIS
  Count aggregate lines across all .cs files under a path.

.DESCRIPTION
  Recursively finds .cs files (skips bin and obj folders), counts total lines,
  and optionally excludes blank lines and/or comment lines (// and /* */ block comments).

.PARAMETER Path
  Root folder to search. Default is current directory.

.PARAMETER ExcludeBlank
  If set, blank lines are not counted.

.PARAMETER ExcludeComments
  If set, single-line comments (//) and block comments (/* ... */) are excluded.

.EXAMPLE
  .\Count-CsLines.ps1 -Path . -ExcludeBlank -ExcludeComments
#>

param(
  [string]$Path = '.',
  [switch]$ExcludeBlank,
  [switch]$ExcludeComments
)

# Find .cs files, ignore bin and obj directories
$files = Get-ChildItem -Path $Path -Recurse -Include *.cs -File -ErrorAction SilentlyContinue |
         Where-Object { $_.FullName -notmatch '\\(bin|obj)\\' }

$totalFiles = $files.Count
$totalLines = 0
$totalCounted = 0

foreach ($file in $files) {
  # Read file as raw text and split into lines (handles CRLF and LF)
  $content = Get-Content -Raw -Encoding UTF8 -ErrorAction SilentlyContinue -LiteralPath $file.FullName
  if ($null -eq $content) { continue }
  $lines = $content -split "`r?`n"
  $totalLines += $lines.Count

  # If no exclusions requested, just add all lines
  if (-not $ExcludeBlank -and -not $ExcludeComments) {
    $totalCounted += $lines.Count
    continue
  }

  # Filter lines according to options
  $countedThisFile = 0
  $inBlock = $false

  foreach ($line in $lines) {
    $trim = $line.Trim()

    # Skip blank lines if requested
    if ($ExcludeBlank -and $trim -eq '') { continue }

    if ($ExcludeComments) {
      # If currently inside a block comment, look for end
      if ($inBlock) {
        if ($trim -match '\*/') {
          # End of block comment found; keep any code after the closing */
          $after = $trim -replace '.*\*/', ''
          $inBlock = $false
          if ($after.Trim() -ne '') {
            # If remainder is not blank and not a comment, count it
            if (-not ($after.Trim() -match '^//')) { $countedThisFile++ }
          }
        }
        continue
      }

      # Detect start of block comment
      if ($trim -match '/\*') {
        # If block comment ends on same line, remove the comment portion and check remainder
        if ($trim -match '\*/') {
          $before = $trim -replace '/\*.*\*/', ''
          if ($before.Trim() -ne '') {
            if (-not ($before.Trim() -match '^//')) { $countedThisFile++ }
          }
        } else {
          # Block comment starts and continues; keep any code before it
          $before = $trim -replace '/\*.*$', ''
          if ($before.Trim() -ne '') {
            if (-not ($before.Trim() -match '^//')) { $countedThisFile++ }
          }
          $inBlock = $true
        }
        continue
      }

      # Single-line comment
      if ($trim -match '^\s*//') { continue }
    }

    # If we reach here, the line counts
    $countedThisFile++
  }

  $totalCounted += $countedThisFile
}

# Output summary
Write-Host "Files scanned:" $totalFiles
Write-Host "Total lines (all .cs files):" $totalLines
if ($ExcludeBlank -or $ExcludeComments) {
  Write-Host "Total lines after exclusions:" $totalCounted
} else {
  Write-Host "Total lines counted:" $totalCounted
}