#!/bin/bash

echo "🚀 Branch Finalizer Başladı..."

# Branch - Klasör eşleştirmeleri
declare -A BRANCH_DIR_MAP=(
    ["feature/redteam-attacks"]="src/attacks"
    ["feature/blueteam-defense"]="src/defense"
    ["feature/ai-anomaly"]="src/defense/ai"
    ["feature/canbus-module"]="src/canbus"
    ["feature/dashboard-ui"]="Dashboard"
    ["feature/docs"]="docs"
)

# Temizlenecek kök klasörler
ROOT_DIRS=("src" "docs" "Dashboard" "tests")

CURRENT=$(git rev-parse --abbrev-ref HEAD)

for BRANCH in "${!BRANCH_DIR_MAP[@]}"; do
    echo "---------------------------------------"
    echo "🔄 Geçiş yapılıyor: $BRANCH"
    git checkout $BRANCH

    TARGET="${BRANCH_DIR_MAP[$BRANCH]}"
    echo "📁 Bu branch'te tutulacak klasör: $TARGET"

    # 1) Tüm kök klasörlerde dolaş
    for DIR in "${ROOT_DIRS[@]}"; do
        if [ "$DIR" != "$TARGET" ]; then
            echo "🧹 $DIR temizleniyor..."
            find "$DIR" -mindepth 1 -maxdepth 1 ! -path "$TARGET*" -exec rm -rf {} +
        fi
    done

    # Eğer AI için alt klasör yoksa oluştur
    if [ "$BRANCH" = "feature/ai-anomaly" ]; then
        mkdir -p src/defense/ai
    fi

    echo "💾 Değişiklikler commit ediliyor..."
    git add .
    git commit -m "Finalize structure for $BRANCH" 2>/dev/null

    echo "⬆️ Push ediliyor..."
    git push

done

echo "🔁 Son olarak dev branch'e dönülüyor..."
git checkout dev

echo "🎉 Tüm branchlerin final halleri oluşturuldu!"
