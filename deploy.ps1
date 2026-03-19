# Deployment script for Streamlit Cloud
Write-Host "========================================" -ForegroundColor Green
Write-Host "🚀 Deploying Deforestation Monitoring System" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if git is installed
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git is not installed" -ForegroundColor Red
    exit 1
}

# Show current status
Write-Host "📊 Current git status:" -ForegroundColor Yellow
git status --short

Write-Host ""
 = Read-Host "Do you want to commit all changes? (y/n)"
if ( -ne 'y') {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 0
}

# Add all changes
Write-Host ""
Write-Host "📦 Adding changes..." -ForegroundColor Yellow
git add .

# Get commit message
 = Read-Host "
Enter commit message"
if ([string]::IsNullOrWhiteSpace()) {
     = "Update deployment for Streamlit Cloud"
}

# Commit
Write-Host ""
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
git commit -m ""

# Push to GitHub
Write-Host ""
Write-Host "☁️ Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

if (0 -eq 0) {
    Write-Host ""
    Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Go to https://streamlit.io/cloud" -ForegroundColor White
    Write-Host "   2. Sign in with GitHub" -ForegroundColor White
    Write-Host "   3. Click 'New app'" -ForegroundColor White
    Write-Host "   4. Select: Kelvin-Njagi/Deforestation.io" -ForegroundColor White
    Write-Host "   5. Set main file path: app.py" -ForegroundColor White
    Write-Host "   6. Click 'Deploy'" -ForegroundColor White
    Write-Host ""
    Write-Host "📱 Your app will be available at: https://deforestation-io.streamlit.app" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ Failed to push to GitHub" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
