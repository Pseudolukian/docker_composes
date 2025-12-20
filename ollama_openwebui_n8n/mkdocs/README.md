# MkDocs для Obsidian Notes

## Описание

Автоматическая система сборки документации из заметок Obsidian с использованием MkDocs Material.

## Как работает

1. **Динамический TOC**: Скрипт `generate_nav.py` сканирует том `obsidian_vaults` и автоматически создаёт навигацию:
   - **Горизонтальный бар** = название vault (папка в Obsidian)
   - **Вертикальный бар** = названия файлов заметок (из .md файлов)

2. **Автоматическая пересборка**: Контейнер отслеживает изменения в vaults через `inotifywait` и автоматически пересобирает документацию при добавлении/изменении заметок.

3. **Публикация**: Собранная HTML документация помещается в том `html_notes`, откуда Caddy отдаёт её по адресу `notes.sweetsweep.online`.

## Структура

```
mkdocs/
├── Dockerfile              # Кастомный образ с плагинами
├── entrypoint.sh          # Скрипт автоматической пересборки
├── generate_nav.py        # Генерация навигации из vaults
├── mkdocs.yml            # Конфигурация MkDocs
└── stylesheets/
    └── extra.css         # Дополнительные стили
```

## Использование

### Запуск

```bash
cd /root/docker_composes/ollama_openwebui_n8n
docker compose up -d mkdocs
```

### Пересборка образа

Если изменили Dockerfile или скрипты:

```bash
docker compose build mkdocs
docker compose up -d mkdocs
```

### Просмотр логов

```bash
docker compose logs -f mkdocs
```

## Особенности

- **Material theme** с поддержкой тёмной/светлой темы
- **Поиск** на русском и английском
- **Подсветка синтаксиса** для кода
- **Mermaid диаграммы**
- **Lightbox** для изображений
- **Responsive дизайн**

## Переменные окружения

```env
OBSIDIAN_VAULTS_PATH=/obsidian_vaults    # Путь к vaults Obsidian
MKDOCS_DOCS_PATH=/docs/docs              # Путь к docs для mkdocs
MKDOCS_CONFIG_PATH=/docs/mkdocs.yml      # Путь к конфигу
```

## Тома Docker

- `obsidian_vaults` → `/obsidian_vaults` (read-only) - исходные заметки
- `html_notes` → `/html_output` (write) - собранная документация
- `./mkdocs` → `/docs` - конфигурация и скрипты

## Настройка темы

Отредактируйте `mkdocs.yml` для изменения цветов, функций навигации и плагинов.

## Troubleshooting

### Документация не обновляется

```bash
# Перезапустите контейнер
docker compose restart mkdocs

# Проверьте логи
docker compose logs mkdocs
```

### Заметки не отображаются

1. Проверьте, что в Obsidian есть .md файлы
2. Проверьте права доступа к тому `obsidian_vaults`
3. Проверьте логи для ошибок парсинга

### Caddy не отдаёт страницы

```bash
# Проверьте, что том html_notes смонтирован в Caddy
docker compose exec caddy ls -la /html_notes

# Перезапустите Caddy
docker compose restart caddy
```
