$dirs = @(
  "apps\crm-integration\app",
  "apps\crm-integration\app\adapters",
  "apps\crm-integration\app\api",
  "apps\crm-integration\app\core",
  "apps\crm-integration\app\models",
  "apps\crm-integration\app\schemas",
  "apps\crm-integration\app\services",
  "infrastructure\database"
)
foreach ($d in $dirs) {
  New-Item -ItemType Directory -Force -Path $d | Out-Null
  $f = "$d\__init__.py"
  if ($d -notlike "*infrastructure*") {
    if (-not (Test-Path $f)) {
      New-Item -ItemType File -Force -Path $f | Out-Null
    }
  }
}
Write-Host "CRM integration dirs created."
