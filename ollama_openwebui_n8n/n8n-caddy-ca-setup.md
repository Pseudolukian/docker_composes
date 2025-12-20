# Настройка доверия n8n к самоподписанному CA Caddy

## В чём была проблема

1. Caddy хранит свой внутренний корневой сертификат (CA) в общем томе `caddy_data` по пути:
   - В контейнере Caddy: `/data/caddy/pki/authorities/local/root.crt`
   - В контейнере n8n (через тот же volume): `/caddy_data/caddy/pki/authorities/local/root.crt`
2. В `compose.yaml` для n8n уже было настроено:
   - Том: `caddy_data:/caddy_data:ro`
   - Переменная окружения: `NODE_EXTRA_CA_CERTS=/caddy_data/caddy/pki/authorities/local/root.crt`
3. Однако директории и файлы PKI от Caddy имели слишком жёсткие права:
   - Директории: `drwx------` (`700`), владелец `root:root`
   - Файлы сертификатов: `-rw-------` (`600`), владелец `root:root`
4. Пользователь процесса внутри `n8n` — `node` (`uid=1000`, `gid=1000`), поэтому он не мог читать файлы в томе, несмотря на корректный путь и монтирование.
5. В логах n8n это проявлялось так:
   - `Warning: Ignoring extra certs from '/caddy_data/caddy/pki/authorities/local/root.crt', load failed: error:8000000D:system library::Permission denied`

Итого: **том и путь были настроены правильно, но NodeJS/n8n не имел прав читать `root.crt`.**

## Как было решено

### 1. Проверка текущих прав

В контейнере Caddy:

```bash
docker exec caddy ls -ld \
  /data \
  /data/caddy \
  /data/caddy/pki \
  /data/caddy/pki/authorities \
  /data/caddy/pki/authorities/local

docker exec caddy ls -l /data/caddy/pki/authorities/local
```

В контейнере n8n:

```bash
docker exec n8n id
# uid=1000(node) gid=1000(node) ...

docker exec n8n ls -ld \
  /caddy_data \
  /caddy_data/caddy \
  /caddy_data/caddy/pki \
  /caddy_data/caddy/pki/authorities \
  /caddy_data/caddy/pki/authorities/local

docker exec n8n ls -l /caddy_data/caddy/pki/authorities/local
```

Эти команды показали, что *владелец — root*, а права `700/600`, поэтому n8n не может читать.

### 2. Ослабление прав только до необходимого минимума

В контейнере Caddy были изменены права на директории PKI и сам `root.crt`:

```bash
# Разрешить всем пользователям заходить в директории PKI
docker exec caddy chmod 755 /data/caddy/pki \
  /data/caddy/pki/authorities \
  /data/caddy/pki/authorities/local

# Разрешить всем пользователям читать сам корневой сертификат
docker exec caddy chmod 644 /data/caddy/pki/authorities/local/root.crt
```

После этого можно перепроверить права в n8n (через общий volume):

```bash
docker exec n8n ls -ld \
  /caddy_data/caddy/pki \
  /caddy_data/caddy/pki/authorities \
  /caddy_data/caddy/pki/authorities/local

docker exec n8n ls -l /caddy_data/caddy/pki/authorities/local
```

Ожидаемый результат:

- Директории: `drwxr-xr-x` (`755`)
- Файл `root.crt`: `-rw-r--r--` (`644`)

И проверка фактического чтения файла из n8n:

```bash
docker exec n8n cat /caddy_data/caddy/pki/authorities/local/root.crt >/dev/null && \
  echo 'n8n can read root.crt'
```

### 3. Перезапуск n8n

Чтобы n8n подхватил изменения и заново попробовал загрузить CA из `NODE_EXTRA_CA_CERTS`:

```bash
cd /root/docker_composes/ollama_openwebui_n8n

docker compose restart n8n
```

Затем можно посмотреть логи:

```bash
docker logs --tail=100 n8n
```

Если прав доступа достаточно, n8n продолжит работу без критических TLS-ошибок, а `NODE_EXTRA_CA_CERTS` будет учитываться.

## Краткий вывод

- Основная загвоздка: **n8n не имел прав читать `root.crt` из общего тома `caddy_data`, потому что Caddy создавал PKI-файлы с правами `700/600` и владельцем `root:root`.**
- Решение: **ослабить права на PKI-директории до `755` и на `root.crt` до `644` в контейнере Caddy**, после чего n8n (пользователь `node`) смог прочитать сертификат через примонтированный том.
