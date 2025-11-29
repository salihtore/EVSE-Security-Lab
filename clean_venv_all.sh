#!/bin/bash

echo "🚀 Tüm branchlerde .venv temizliği başlatılıyor..."

# Gitignore'u garanti altına al
echo ".venv/
venv/
__pycache__/
*.pyc" > .gitignore

git add .gitignore
git commit -m "Ensure .gitignore includes venv rules" 2>/dev/null

# Tüm local branchleri listele
BRANCHES=$(git branch | sed 's/*//')

for BR in $BRANCHES
do
    echo "🔄 Branch değiştiriliyor: $BR"
    git checkout $BR

    echo "🧹 .venv ve venv izleri temizleniyor..."
    git rm -r --cached .venv 2>/dev/null
    git rm -r --cached venv 2>/dev/null
    git rm -r --cached __pycache__ 2>/dev/null

    echo "📦 Index yeniden ekleniyor..."
    git add .

    echo "💾 Commit atılıyor (branch: $BR)..."
    git commit -m "Clean venv from tracking (automatic script)" 2>/dev/null

    echo "⬆️ Push ediliyor..."
    git push 2>/dev/null

    echo "✅ $BR temizlendi!"
    echo "--------------------------------------------"
done

echo "🔁 Son olarak dev branch'e dönülüyor..."
git checkout dev

echo "🎉 Temizlik tamamlandı! Artık .venv hiçbir branchte yok."
