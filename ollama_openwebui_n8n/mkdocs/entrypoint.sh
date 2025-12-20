#!/bin/sh
set -e

echo "Starting MkDocs auto-build service..."

# Устанавливаем необходимые пакеты
echo "Installing required packages..."
apk add --no-cache inotify-tools python3 py3-pip
pip install --no-cache-dir pyyaml

# Копируем скрипт генерации навигации
cp /docs/generate_nav.py /tmp/generate_nav.py
chmod +x /tmp/generate_nav.py

# Функция для генерации и сборки документации
build_docs() {
    echo "Generating navigation from Obsidian vaults..."
    python3 /tmp/generate_nav.py
    
    echo "Cleaning old HTML output..."
    rm -rf /html_output/*
    
    echo "Building MkDocs site..."
    cd /docs
    mkdocs build --clean --site-dir /html_output
    
    echo "Documentation built successfully at $(date)"
}

# Первая сборка при старте
build_docs

# Мониторинг изменений в vaults и автоматическая пересборка
echo "Watching for changes in Obsidian vaults..."
inotifywait -m -r -e modify,create,delete,move /obsidian_vaults --format '%w%f' | while read file
do
    # Игнорируем служебные файлы Obsidian и корзину
    if echo "$file" | grep -qE '\.(obsidian|trash)/'; then
        continue
    fi
    
    echo "Detected change in: $file"
    # Даём немного времени на завершение записи файла
    sleep 2
    build_docs
done
