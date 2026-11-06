$ErrorActionPreference = "Stop"

# This isolated smoke service always targets the explicitly named project.
$ProjectId = "gen-lang-client-0527696821"
$Region = "asia-south1"
$Service = "mnemosyne-api-smoke"
$ApiSource = (Resolve-Path (Join-Path $PSScriptRoot "..\apps\api")).Path

gcloud run deploy $Service `
  --source=$ApiSource `
  --project=$ProjectId `
  --region=$Region `
  --port=8000 `
  --cpu=1 `
  --memory=512Mi `
  --min=0 `
  --max=1 `
  --concurrency=10 `
  --no-allow-unauthenticated `
  --invoker-iam-check `
  --set-env-vars="DATABASE_URL=sqlite+pysqlite:////tmp/mnemosyne.db" `
  --quiet

if ($LASTEXITCODE -ne 0) {
  throw "Cloud Run deployment failed with exit code $LASTEXITCODE."
}

$ServiceUrl = gcloud run services describe $Service `
  --project=$ProjectId `
  --region=$Region `
  --format="value(status.url)"

if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($ServiceUrl)) {
  throw "Could not read the deployed Cloud Run service URL."
}

Write-Output "Deployed $Service to $ServiceUrl in project $ProjectId ($Region)."
Write-Output "The service is IAM-protected and uses ephemeral SQLite for this smoke deployment."
