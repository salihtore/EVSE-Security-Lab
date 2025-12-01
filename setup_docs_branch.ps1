# PowerShell Script – docs branch oluşturur ve doküman klasörlerini taşır
# Silme işlemi YOK. main ve dev'e DOKUNMAZ.

$ErrorActionPreference = "Stop"

$docFolders = @("Dokumantasyon", "Anomaliler")

Write-Host "----------------------------------------"
Write-Host "[INFO] docs branch kurulumu başlıyor..."
Write-Host "----------------------------------------"

# 1) docs branch kontrol & checkout
$docsExists = git branch --list docs

if ($docsExists) {
    Write-Host "[INFO] 'docs' branch zaten var. Checkout ediliyor..."
    git checkout docs
} else {
    Write-Host "[INFO] 'docs' branch oluşturuluyor..."
    git checkout -b docs
    git push -u origin docs
}

# 2) docs dizini oluştur
if (!(Test-Path -Path "docs")) {
    New-Item -ItemType Directory -Path "docs" | Out-Null
}

# 3) Klasörleri docs altına taşı
foreach ($folder in $docFolders) {
    if (Test-Path -Path $folder) {
        Write-Host "[MOVE] $folder → docs/"
        git mv $folder docs/
    }
    else {
        Write-Host "[SKIP] '$folder' klasörü bulunamadı, atlanıyor."
    }
}

# 4) Commit & push
git add .
git commit -m "docs branch: Dokumantasyon ve Anomaliler docs klasörüne taşındı" 2>$null
git push

Write-Host "----------------------------------------"
Write-Host "[SUCCESS] İşlem tamamlandı!"
Write-Host "Simulasyon/ ve src/ → main & dev içinde KALDI (hiçbir işlem yapılmadı)"
Write-Host "Dokumantasyon/ ve Anomaliler/ → sadece docs branch içinde"
Write-Host "----------------------------------------"
