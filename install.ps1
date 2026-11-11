<#
.SYNOPSIS
  Link the matchcut skills into your agents' skill folders (Windows). Links, not copies:
  a `git pull` here updates every installed skill in place. Junctions need no admin rights.

.EXAMPLE
  ./install.ps1                         # Claude Code, Codex and Hermes (the ones that exist)
  ./install.ps1 -Targets claude         # only Claude Code
  ./install.ps1 -Targets agents         # the shared ~/.agents/skills folder
  ./install.ps1 -Only matchcut,ui-reel
  ./install.ps1 -List
  ./install.ps1 -Uninstall
  ./install.ps1 -Dest D:\tmp\skills     # any folder (for testing)
#>
param(
  [string[]]$Targets = @('claude', 'codex', 'hermes'),
  [string[]]$Only = @(),
  [string]$Dest = '',
  [switch]$List,
  [switch]$Uninstall
)
$ErrorActionPreference = 'Stop'
# "a,b" arrives as one string when the script is run with pwsh -File
$Targets = @($Targets | ForEach-Object { $_ -split ',' } | Where-Object { $_ })
$Only = @($Only | ForEach-Object { $_ -split ',' } | Where-Object { $_ })
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillsDir = Join-Path $repo 'skills'
$homeDir = $env:USERPROFILE
$known = @{
  claude = Join-Path $homeDir '.claude\skills'
  codex  = Join-Path $homeDir '.codex\skills'
  hermes = Join-Path $homeDir '.hermes\skills'
  agents = Join-Path $homeDir '.agents\skills'
}
$folders = if ($Dest) { @($Dest) } else {
  $Targets | ForEach-Object {
    if (-not $known.ContainsKey($_)) { throw "Unknown target '$_'. Use: $($known.Keys -join ', ')" }
    $known[$_]
  }
}

$skills = Get-ChildItem $skillsDir -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') }
if ($Only.Count) { $skills = $skills | Where-Object { $Only -contains $_.Name } }

if ($List) {
  foreach ($s in $skills) {
    $desc = (Select-String -Path (Join-Path $s.FullName 'SKILL.md') -Pattern '^description:' | Select-Object -First 1).Line -replace '^description:\s*', ''
    '{0,-18} {1}' -f $s.Name, ($desc.Substring(0, [Math]::Min(90, $desc.Length)))
  }
  return
}

function Get-LinkTarget($path) {
  $item = Get-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
  if ($item -and $item.LinkType) { return [string]($item.Target | Select-Object -First 1) }
  return $null
}

foreach ($folder in $folders) {
  $parent = Split-Path -Parent $folder
  if (-not $Dest -and -not (Test-Path $parent)) { Write-Host "skip     $folder (that agent is not installed)"; continue }
  if (-not (Test-Path $folder)) { New-Item -ItemType Directory -Path $folder -Force | Out-Null }
  foreach ($s in $skills) {
    $link = Join-Path $folder $s.Name
    $target = Get-LinkTarget $link
    if ($Uninstall) {
      if ($target -and ($target -like "$skillsDir*")) {
        (Get-Item -LiteralPath $link -Force).Delete()
        Write-Host "removed  $link"
      }
      continue
    }
    if ($target) {
      if ($target -like "$skillsDir*") { (Get-Item -LiteralPath $link -Force).Delete() }
      else { Write-Host "skip     $link (links somewhere else; remove it first)"; continue }
    } elseif (Test-Path -LiteralPath $link) {
      Write-Host "skip     $link (a real folder is there; move it aside first)"; continue
    }
    New-Item -ItemType Junction -Path $link -Target $s.FullName | Out-Null
    Write-Host "linked   $link"
  }
}
if (-not $Uninstall) { Write-Host "`nDone. Start a new agent session to load the skills." }
