$ErrorActionPreference = "Stop"
$env:PATH = "C:\Users\ganes\.gemini\antigravity\bin\cmd;" + $env:PATH

Write-Host "Creating GitHub repository 'Enamel website'..." -ForegroundColor Cyan
gh repo create "Enamel website" --public --source="." --remote=origin --push

Write-Host "`nSuccessfully created repository and pushed all files!" -ForegroundColor Green
gh repo view --web
