function Remove-GitPaths {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
        [string[]]$Paths,

        [switch]$FromIndex,   # use git rm --cached (remove from index only)
        [switch]$Force,       # remove from working tree + index
        [switch]$DryRun       # show what would be done
    )

    process {
        foreach ($p in $Paths) {
            # normalize path relative to repo root (current directory)
            $rel = $p
            $abs = Resolve-Path -LiteralPath $rel -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path -ErrorAction SilentlyContinue

            if ($DryRun) {
                if ($FromIndex) {
                    Write-Host "[DryRun] git rm --cached --ignore-unmatch -- `"$rel`""
                } elseif ($Force) {
                    Write-Host "[DryRun] Remove-Item -Recurse -Force `"$rel`""
                    Write-Host "[DryRun] git rm --ignore-unmatch -- `"$rel`""
                } else {
                    Write-Host "[DryRun] Remove-Item -Recurse -Force `"$rel`" (and git rm if tracked)"
                }
                continue
            }

            if ($FromIndex) {
                git rm --cached --ignore-unmatch -- "$rel" 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "Removed from index: $rel"
                } else {
                    Write-Warning "git rm --cached did not remove (or not tracked): $rel"
                }
                continue
            }

            if ($Force) {
                if (Test-Path -LiteralPath $rel) {
                    try {
                        Remove-Item -LiteralPath $rel -Recurse -Force -ErrorAction Stop
                        Write-Host "Deleted from working tree: $rel"
                    } catch {
                        Write-Warning "Failed to delete from working tree: $rel — $_"
                    }
                } else {
                    Write-Host "Not found locally (skipping delete): $rel"
                }

                git rm --ignore-unmatch -- "$rel" 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "Also removed from git index: $rel"
                } else {
                    Write-Host "Not tracked in git index: $rel"
                }
                continue
            }

            # default: remove from working tree if exists, and try to remove from git index if tracked
            if (Test-Path -LiteralPath $rel) {
                try {
                    Remove-Item -LiteralPath $rel -Recurse -Force -ErrorAction Stop
                    Write-Host "Deleted: $rel"
                } catch {
                    Write-Warning "Failed to delete: $rel — $_"
                }
            } else {
                Write-Host "Not found locally: $rel"
            }

            git rm --ignore-unmatch -- "$rel" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Removed from git index: $rel"
            } else {
                Write-Host "Not tracked in git index (or already removed): $rel"
            }
        }
    }
}