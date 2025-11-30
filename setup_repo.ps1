Write-Host "=== EVSE-Security-Lab AUTO STRUCTURE SCRIPT BASLIYOR ===" -ForegroundColor Cyan

# 1) Branch switch to dev
git checkout dev

Write-Host "`n>>> Mevcut src klasoru siliniyor (varsa)..." -ForegroundColor Yellow
if (Test-Path "src") { Remove-Item -Recurse -Force "src" }

# 2) Create clean src structure
Write-Host ">>> Yeni src klasörü oluşturuluyor..." -ForegroundColor Yellow
mkdir src
mkdir src\attacks
mkdir src\defense
mkdir src\defense\core
mkdir src\canbus
mkdir src\core

# 3) Add empty __init__.py files
Write-Host ">>> __init__.py dosyalari ekleniyor..." -ForegroundColor Yellow
ni src\__init__.py
ni src\attacks\__init__.py
ni src\defense\__init__.py
ni src\defense\core\__init__.py
ni src\canbus\__init__.py
ni src\core\__init__.py

# 4) Commit changes
Write-Host ">>> DEV branch'teki src yapısı commitleniyor..." -ForegroundColor Yellow
git add .
git commit -m "Rebuild clean src structure (auto-script)"
git push

# 5) Merge dev → main
Write-Host "`n>>> MAIN branch'e geciliyor..." -ForegroundColor Yellow
git checkout main

Write-Host ">>> DEV → MAIN merge ediliyor..." -ForegroundColor Yellow
git merge dev --no-edit

Write-Host ">>> MAIN push ediliyor..." -ForegroundColor Yellow
git push --force

# 6) Delete local feature branches
Write-Host "`n>>> Feature branch'leri lokalde siliniyor..." -ForegroundColor Yellow
$branches = @(
    "feature/ai-anomaly",
    "feature/blueteam-defense",
    "feature/canbus-module",
    "feature/dashboard-ui",
    "feature/docs",
    "feature/redteam-attacks"
)

foreach ($b in $branches) {
    git branch -D $b
}

# 7) Delete remote feature branches
Write-Host "`n>>> Feature branch'leri uzak repodan siliniyor..." -ForegroundColor Yellow
foreach ($b in $branches) {
    git push origin --delete $b
}

Write-Host "`n=== TAMAMLANDI! Repository artık C-modeline göre profesyonel şekilde temizlendi! ===" -ForegroundColor Green
