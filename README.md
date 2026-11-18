# Task Manager — практическое занятие №18

Учебный проект для репетиции деплоя на Windows 10/11. Архитектура: браузер → Nginx (HTTPS, единственная точка входа) → статический frontend и Flask API → SQLite в Docker volume.

## Состав сервисов

| Сервис | Технология | Внутренний порт | Назначение |
|---|---|---:|---|
| nginx | Nginx 1.27 | 80, 443 | HTTP→HTTPS, TLS, reverse proxy |
| frontend | Nginx 1.27 Alpine | 80 | Статические HTML/CSS/JS |
| backend | Python 3.12, Flask, Gunicorn | 5000 | REST API |
| task_data | Docker volume | — | Постоянное хранение SQLite |

## Переменные окружения и секреты

- `DB_PATH` — путь к файлу SQLite (значение по умолчанию `/data/tasks.db`).
- Закрытый ключ TLS находится в `deploy/certs/` и не должен попадать в Git.

В учебном проекте нет паролей и внешних API-ключей. Локальный TLS-ключ создаётся отдельно на компьютере.

## Требования

- Docker Desktop с включённым Linux containers/WSL2 backend.
- Git.
- PowerShell.
- mkcert.

## Установка и запуск на Windows

1. Установить и запустить Docker Desktop.
2. Открыть PowerShell и проверить:
   ```powershell
   docker --version
   docker compose version
   ```
3. Установить mkcert:
   ```powershell
   winget install FiloSottile.mkcert
   ```
   Закрыть и заново открыть PowerShell.
4. Установить локальный корневой сертификат (PowerShell от имени администратора):
   ```powershell
   mkcert -install
   ```
5. Перейти в папку сертификатов и выпустить сертификат:
   ```powershell
   cd deploy
   New-Item -ItemType Directory -Force certs
   cd certs
   mkcert -cert-file taskmanager.localhost.pem -key-file taskmanager.localhost-key.pem taskmanager.localhost
   cd ..
   ```
6. Запустить сервисы:
   ```powershell
   docker compose up --build -d
   ```
7. Проверить состояние и логи:
   ```powershell
   docker compose ps
   docker compose logs nginx
   docker compose logs backend
   ```
8. Открыть в Chrome или Edge: https://taskmanager.localhost

## Остановка

Из папки `deploy`:
```powershell
docker compose down
```
Данные SQLite сохраняются в Docker volume. Чтобы удалить и контейнеры, и данные:
```powershell
docker compose down -v
```

## Проверка API

Открой:
- `https://taskmanager.localhost/api/health`
- `https://taskmanager.localhost/api/tasks`

В DevTools (F12 → Network) выбери запрос `/api/tasks` и проверь статус ответа. Для API nginx добавляет `X-Robots-Tag: noindex, nofollow`.

## CI — GitHub Actions

Workflow `.github/workflows/docker-build.yml` запускается при `push`, `pull_request` и вручную через `workflow_dispatch`. Он собирает Docker-образы frontend и backend. Для учебной сборки секреты не требуются.

Чтобы проверить CI:
1. Создай GitHub-репозиторий.
2. Отправь файлы проекта в ветку `main`.
3. Открой вкладку Actions и дождись зелёного статуса workflow.
4. Сделай скриншот успешного запуска.

## Архитектура

```text
Браузер
   |
   | HTTPS :443 / HTTP :80
   v
Nginx (TLS + reverse proxy)
   |                    |
   | /                  | /api/
   v                    v
Frontend :80         Flask API :5000
                         |
                         v
                    SQLite /data
                    Docker volume
```

## Скриншоты для отчёта

Сохрани реальные скриншоты в `deploy/screenshots/`:
1. `docker-compose-ps.png` — вывод `docker compose ps`.
2. `browser-https.png` — сайт `https://taskmanager.localhost` с защищённым соединением.
3. `network-api.png` — вкладка Network с запросом `/api/tasks` и заголовками.
4. `docker-desktop.png` — контейнеры и опубликованные порты (порты наружу должны быть только у nginx).
5. `github-actions.png` — успешный workflow (дополнительное задание).

Не вставляй фиктивные скриншоты: сделай их после запуска на своём компьютере.

## Возможные ошибки

- `docker` не распознан — запусти Docker Desktop и перезапусти PowerShell.
- Порт 80 или 443 занят — закрой программу, которая его использует, затем повтори запуск.
- Nginx не запускается из-за сертификата — проверь имена файлов в `deploy/certs` и пути в `nginx.conf`.
- Браузер предупреждает о сертификате — выполни `mkcert -install` от имени администратора и перезапусти браузер.
- Сайт не открывается — проверь `docker compose ps` и `docker compose logs nginx backend frontend`.

## Что потребуется для публикации на реальном сервере

Арендовать сервер/облачный хостинг, зарегистрировать домен, настроить DNS, заменить локальный сертификат на сертификат публичного центра сертификации (например, Let's Encrypt), открыть необходимые сетевые порты и настроить доставку образов/обновлений. Перед публикацией отдельно проверить защиту данных и требования законодательства.

## Важно

Папка `deploy/certs/` и закрытый TLS-ключ исключены из Git. Не отправляй приватные ключи и реальные секреты в репозиторий.
