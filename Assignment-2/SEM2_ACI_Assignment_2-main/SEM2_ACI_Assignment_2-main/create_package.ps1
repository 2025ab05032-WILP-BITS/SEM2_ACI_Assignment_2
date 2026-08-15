# create_package.ps1
# Creates a zip archive of the project directory excluding the .git folder and any existing .zip files.
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $root

# Files/folders to exclude
$excludeNames = @('.git')

# Collect paths to include
$items = Get-ChildItem -Force | Where-Object { $excludeNames -notcontains $_.Name -and $_.Name -notlike '*.zip' }
$paths = $items | ForEach-Object { $_.FullName }

$destination = Join-Path $root 'improve-minimax-readme-tests.zip'

if (Test-Path $destination) {
    Remove-Item $destination -Force
}

Compress-Archive -Path $paths -DestinationPath $destination -Force

Write-Output "Created package: $destination"
Pop-Location
