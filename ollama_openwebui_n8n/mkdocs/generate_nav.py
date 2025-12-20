#!/usr/bin/env python3
"""
Скрипт для динамической генерации navigation (TOC) из заметок Obsidian.
Горизонтальный бар = название vault (папка)
Вертикальный бар = названия файлов заметок
"""
import os
import yaml
from pathlib import Path
from collections import defaultdict


def scan_obsidian_vaults(vaults_path):
    """
    Сканирует папку с vaults Obsidian и создаёт структуру навигации.
    
    Args:
        vaults_path: Путь к папке с vaults
        
    Returns:
        list: Структура навигации для mkdocs
    """
    nav = []
    vaults_dir = Path(vaults_path)
    
    if not vaults_dir.exists():
        print(f"Warning: Vaults directory {vaults_path} not found")
        return nav
    
    # Проходим по всем vault'ам (папкам первого уровня)
    for vault_dir in sorted(vaults_dir.iterdir()):
        if not vault_dir.is_dir() or vault_dir.name.startswith('.'):
            continue
        
        vault_name = vault_dir.name
        vault_files = []
        
        # Рекурсивно находим все .md файлы в vault
        md_files = list(vault_dir.rglob('*.md'))
        
        if not md_files:
            continue
            
        # Группируем файлы по подпапкам
        files_by_folder = defaultdict(list)
        
        for md_file in sorted(md_files):
            # Пропускаем скрытые файлы
            if any(part.startswith('.') for part in md_file.parts):
                continue
                
            # Относительный путь от vault
            rel_path = md_file.relative_to(vault_dir)
            
            # Создаём путь для mkdocs (копируем в docs/)
            # Сохраняем структуру папок vault
            target_path = f"{vault_name}/{rel_path}"
            
            # Получаем название без расширения для отображения
            display_name = md_file.stem
            
            # Определяем подпапку (если есть)
            if len(rel_path.parts) > 1:
                subfolder = str(rel_path.parent)
                files_by_folder[subfolder].append({
                    'name': display_name,
                    'path': target_path
                })
            else:
                files_by_folder['_root'].append({
                    'name': display_name,
                    'path': target_path
                })
        
        # Формируем структуру для этого vault
        vault_structure = []
        
        # Сначала файлы из корня
        if '_root' in files_by_folder:
            for file_info in sorted(files_by_folder['_root'], key=lambda x: x['name']):
                vault_structure.append({file_info['name']: file_info['path']})
        
        # Затем подпапки
        for subfolder in sorted([f for f in files_by_folder.keys() if f != '_root']):
            subfolder_structure = []
            for file_info in sorted(files_by_folder[subfolder], key=lambda x: x['name']):
                subfolder_structure.append({file_info['name']: file_info['path']})
            
            if subfolder_structure:
                vault_structure.append({subfolder: subfolder_structure})
        
        # Добавляем vault в общую навигацию
        if vault_structure:
            nav.append({vault_name: vault_structure})
    
    return nav


def copy_obsidian_files(vaults_path, docs_path):
    """
    Копирует markdown файлы из vaults в структуру docs для mkdocs.
    
    Args:
        vaults_path: Путь к папке с vaults
        docs_path: Путь к папке docs для mkdocs
    """
    vaults_dir = Path(vaults_path)
    docs_dir = Path(docs_path)
    
    if not vaults_dir.exists():
        print(f"Warning: Vaults directory {vaults_path} not found")
        return
    
    # Очищаем старые файлы (кроме index.md)
    for item in docs_dir.iterdir():
        if item.is_dir():
            import shutil
            shutil.rmtree(item)
        elif item.name != 'index.md':
            item.unlink()
    
    # Копируем файлы из всех vaults
    for vault_dir in vaults_dir.iterdir():
        if not vault_dir.is_dir() or vault_dir.name.startswith('.'):
            continue
        
        vault_name = vault_dir.name
        target_vault_dir = docs_dir / vault_name
        target_vault_dir.mkdir(exist_ok=True)
        
        # Копируем все .md файлы с сохранением структуры
        for md_file in vault_dir.rglob('*.md'):
            # Пропускаем скрытые файлы
            if any(part.startswith('.') for part in md_file.parts):
                continue
            
            rel_path = md_file.relative_to(vault_dir)
            target_file = target_vault_dir / rel_path
            
            # Создаём папки если нужно
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Копируем файл
            import shutil
            shutil.copy2(md_file, target_file)


def update_mkdocs_config(config_path, nav):
    """
    Обновляет mkdocs.yml с новой навигацией.
    
    Args:
        config_path: Путь к mkdocs.yml
        nav: Структура навигации
    """
    config_file = Path(config_path)
    
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}
    
    # Обновляем навигацию
    config['nav'] = nav
    
    # Сохраняем конфиг
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)


def main():
    """Основная функция"""
    vaults_path = os.getenv('OBSIDIAN_VAULTS_PATH', '/obsidian_vaults')
    docs_path = os.getenv('MKDOCS_DOCS_PATH', '/docs/docs')
    config_path = os.getenv('MKDOCS_CONFIG_PATH', '/docs/mkdocs.yml')
    
    print(f"Scanning Obsidian vaults in: {vaults_path}")
    print(f"Copying files to: {docs_path}")
    print(f"Updating config: {config_path}")
    
    # Создаём docs папку если не существует
    Path(docs_path).mkdir(parents=True, exist_ok=True)
    
    # Создаём index.md если не существует
    index_file = Path(docs_path) / 'index.md'
    if not index_file.exists():
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write('# Заметки Obsidian\n\n')
            f.write('Добро пожаловать в мою базу знаний!\n\n')
            f.write('Используйте навигацию для просмотра заметок.\n')
    
    # Копируем файлы из vaults
    copy_obsidian_files(vaults_path, docs_path)
    
    # Генерируем навигацию
    nav = scan_obsidian_vaults(vaults_path)
    
    # Добавляем главную страницу в начало
    nav.insert(0, {'Главная': 'index.md'})
    
    # Обновляем конфиг
    update_mkdocs_config(config_path, nav)
    
    print(f"Navigation generated with {len(nav)-1} vaults")
    print("Done!")


if __name__ == '__main__':
    main()
