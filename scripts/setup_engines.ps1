$dirs = @(
  "apps\ai-engine\app",
  "apps\ai-engine\app\api",
  "apps\ai-engine\app\agents",
  "apps\ai-engine\app\chains",
  "apps\ai-engine\app\prompts",
  "apps\ai-engine\app\embeddings",
  "apps\ai-engine\app\memory",
  "apps\ai-engine\app\tools",
  "apps\ai-engine\app\core",
  "apps\ai-engine\models",
  "apps\ml-engine\app",
  "apps\ml-engine\app\api",
  "apps\ml-engine\app\models",
  "apps\ml-engine\app\features",
  "apps\ml-engine\app\pipelines",
  "apps\ml-engine\app\preprocessing",
  "apps\ml-engine\app\explainability",
  "apps\ml-engine\app\core",
  "apps\ml-engine\models",
  "apps\ml-engine\models\saved",
  "apps\security-engine\app",
  "apps\security-engine\app\api",
  "apps\security-engine\app\core",
  "apps\security-engine\app\governance",
  "apps\security-engine\models",
  "apps\workflow-engine\app",
  "apps\workflow-engine\app\api",
  "apps\workflow-engine\app\core",
  "apps\workflow-engine\app\executors",
  "apps\workflow-engine\app\triggers"
)

foreach ($d in $dirs) {
  New-Item -ItemType Directory -Force -Path $d | Out-Null
  $init = "$d\__init__.py"
  if (-not (Test-Path $init)) {
    New-Item -ItemType File -Force -Path $init | Out-Null
  }
}

Write-Host "Created $($dirs.Count) directories with __init__.py files."
