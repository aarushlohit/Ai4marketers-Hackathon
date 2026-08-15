Write-Host "=== Dockerfile.dev check ==="
$services = @(
  "apps\backend",
  "apps\frontend",
  "apps\ai-engine",
  "apps\ml-engine",
  "apps\crm-integration",
  "apps\security-engine",
  "apps\workflow-engine"
)
foreach ($s in $services) {
  $exists = Test-Path "$s\Dockerfile.dev"
  $status = if ($exists) { "OK" } else { "MISSING" }
  Write-Host "  $s\Dockerfile.dev -> $status"
}

Write-Host ""
Write-Host "=== File count per service ==="
foreach ($s in $services) {
  $count = (Get-ChildItem -Path $s -Recurse -File |
    Where-Object { $_.FullName -notlike "*__pycache__*" }).Count
  Write-Host "  $s : $count files"
}

Write-Host ""
Write-Host "=== Total project files ==="
$total = (Get-ChildItem -Path . -Recurse -File |
  Where-Object {
    $_.FullName -notlike "*\.git\*" -and
    $_.FullName -notlike "*node_modules*" -and
    $_.FullName -notlike "*__pycache__*"
  }).Count
Write-Host "  Total: $total files"

Write-Host ""
Write-Host "=== Key infrastructure files ==="
$keyFiles = @(
  "infrastructure\database\init.sql",
  "infrastructure\kubernetes\base\backend-deployment.yaml",
  "infrastructure\terraform\main.tf",
  "infrastructure\monitoring\prometheus\prometheus.yml",
  ".github\workflows\ci-cd.yaml",
  "docker-compose.yml",
  ".env.example",
  "README.md",
  "FOLDER_STRUCTURE.md",
  "docs\SRS.md",
  "docs\SDD.md",
  "docs\TECHNICAL_BLUEPRINT.md",
  "docs\api\openapi.yaml"
)
foreach ($f in $keyFiles) {
  $status = if (Test-Path $f) { "OK" } else { "MISSING" }
  Write-Host "  $f -> $status"
}
