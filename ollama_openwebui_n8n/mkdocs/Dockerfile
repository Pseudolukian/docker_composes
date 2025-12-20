FROM squidfunk/mkdocs-material:latest

# Устанавливаем дополнительные плагины
RUN pip install --no-cache-dir \
    mkdocs-awesome-pages-plugin \
    mkdocs-macros-plugin \
    mkdocs-glightbox \
    mkdocs-git-revision-date-localized-plugin \
    pymdown-extensions \
    pyyaml

# Копируем скрипт генерации навигации
COPY generate_nav.py /app/generate_nav.py
RUN chmod +x /app/generate_nav.py

# Копируем скрипт для автоматической сборки при изменениях
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

WORKDIR /docs

ENTRYPOINT ["/app/entrypoint.sh"]
