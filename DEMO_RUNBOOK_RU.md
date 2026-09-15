# Forkly — ранбук демо-стенда (вариант Б1: VPS + Caddy + домен)

Пошаговая инструкция, как поднять демо для заказчика на собственном сервере:
бэкенд с HTTPS, админ-панель, сайт и Android-APK, который на всё это смотрит.

Время: ~1.5–2 часа. Стоимость: ~500–900 ₽/мес (VPS) + ~200–1000 ₽/год (домен).

> Заменяйте плейсхолдеры: `forkly.example.com` — ваш домен, `203.0.113.10` — IP сервера.

---

## 0. Что получится в итоге

```
                      ┌──────────────────────────────┐
   api.forkly.example │  Caddy (:80/:443, Let's Encrypt)
        .com  ───────▶│   ├── /graphql  → app:8000   │
                      │   ├── /health   → app:8000   │
   admin.forkly...    │   ├── admin.*   → /srv/admin │  (статика)
        .com  ───────▶│   └── www.*     → /srv/www   │  (статика)
   forkly.example     └──────────────────────────────┘
        .com  ───────▶        ▲          ▲        ▲
                              │          │        │
                          mongo:7    redis:7   backup
```

| Что | Где живёт | Кто смотрит |
|-----|-----------|-------------|
| Бэкенд (FastAPI + Strawberry) | Docker на VPS | все |
| MongoDB + Redis | Docker на VPS (порты наружу **не** открыты) | только бэкенд |
| Admin Dashboard (Vite-сборка) | статика на VPS | владелец ресторана |
| Website (Vite-сборка) | статика на VPS | заказчик демо |
| CustomerApp (APK) | телефон/эмулятор | заказчик демо |

Почему Б1: один сервер, один Caddy, автоматический HTTPS. Никаких внешних
PaaS — данные и код под вашим контролем, а на демо это ещё и аргумент в продаже.

---

## 1. Что нужно завести

### 1.1. Домен

Регистратор (любой, оплата картой РФ):

| Регистратор | Зона | Цена/год (ориентир) |
|-------------|------|---------------------|
| [reg.ru](https://reg.ru) | `.ru` | ~200–400 ₽ |
| [Timeweb](https://timeweb.com/ru/services/domains/) | `.ru` / `.com` | ~200 / ~1200 ₽ |
| Cloudflare Registrar | `.com` | $10 (по себестоимости, но нужна зарубежная карта) |

Возьмите один короткий домен — поддомены (`api.`, `admin.`, `www.`) выдаются
бесплатно. Домен **обязателен**: без него Caddy не получит TLS-сертификат, а
Android-приложение не сможет работать с бэкендом (см. шаг 8).

### 1.2. VPS — рекомендация

Нужно минимум **2 vCPU / 4 GB RAM / 40 GB SSD**, Ubuntu 24.04 LTS.

| Провайдер | Конфигурация | Цена/мес (ориентир) | Кому подходит |
|-----------|--------------|---------------------|----------------|
| **[Timeweb Cloud](https://timeweb.cloud/services/vds-vps)** | 2 vCPU / 4 GB / 50 GB | ~500–700 ₽ | ✅ **рекомендую** — оплата картой РФ, панель на русском, дата-центры в РФ |
| [Selectel](https://selectel.ru/services/cloud/servers/) | 2 vCPU / 4 GB / 40 GB | ~600–900 ₽ | крупный провайдер, чуть дороже, хорошая поддержка |
| [Hetzner](https://www.hetzner.com/cloud/) (CX22) | 2 vCPU / 4 GB / 40 GB | ~€4.5 | самый дешёвый, но **нужна зарубежная карта** и оплата в EUR |
| [VDSina](https://vdsina.ru/) | 2 vCPU / 4 GB | ~400–600 ₽ | бюджетно, оплата РФ |

Если есть зарубежная карта — берите Hetzner CX22: дешевле в 2–3 раза при том же
железе. Если нет — Timeweb Cloud, он предсказуемее всего для российского
заказчика.

При заказе выберите образ **Ubuntu 24.04 LTS** и сразу добавьте свой SSH-ключ
(парольный вход потом отключим).

---

## 2. DNS

В панели регистратора добавьте A-записи на IP сервера:

| Тип | Имя | Значение | TTL |
|-----|-----|----------|-----|
| A | `api` | `203.0.113.10` | 300 |
| A | `admin` | `203.0.113.10` | 300 |
| A | `www` | `203.0.113.10` | 300 |
| A | `@` (корень) | `203.0.113.10` | 300 |

Проверка (подождите 5–15 минут):

```bash
nslookup api.forkly.example.com
```

Должен вернуться IP сервера. **Не идите дальше, пока DNS не разрешается** —
Caddy выдаёт сертификаты через ACME, и при неверном DNS упрётся в лимит попыток.
Также убедитесь, что у регистратора не включён «парковочный» сайт на эти имена.

---

## 3. Подготовка сервера

```bash
ssh root@203.0.113.10
```

### 3.1. Обновления и Docker

```bash
apt update && apt upgrade -y
apt install -y git curl ufw

# Docker Engine + Compose plugin (официальный установщик)
curl -fsSL https://get.docker.com | sh
docker --version
docker compose version
```

### 3.2. Файрвол

Наружу нужны только SSH и Caddy (80/443). MongoDB и Redis остаются внутри
docker-сети.

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
ufw status
```

### 3.3. Swap (страховка при сборке)

На 4 GB сборка Python-образа проходит и так, но swap убирает риск OOM:

```bash
fallocate -l 2G /swapfile && chmod 600 /swapfile
mkswap /swapfile && swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 3.4. Отключить вход по паролю

```bash
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart ssh
```

> ⚠️ Перед этим убедитесь, что вход по ключу работает — иначе потеряете доступ.

---

## 4. Бэкенд

```bash
cd /opt
git clone <URL-вашего-репозитория> forkly
cd forkly/backend
cp .env.example .env
nano .env
```

### 4.1. Продовые значения `.env`

| Переменная | Значение | Почему |
|------------|----------|--------|
| `ENV` | `production` | включает fail-fast проверки |
| `DEBUG` | `false` | не отдавать трейсбэки наружу |
| `JWT_SECRET` | `openssl rand -hex 32` | **обязательно**, иначе деплой не стартует |
| `ADMIN_EMAIL` | рабочий e-mail | логин владельца |
| `ADMIN_PASSWORD` | сильный пароль | **не** `change-me` |
| `MONGO_INITDB_ROOT_USERNAME` | `forkly` | |
| `MONGO_INITDB_ROOT_PASSWORD` | `openssl rand -hex 24` | уникальный |
| `REDIS_PASSWORD` | `openssl rand -hex 24` | уникальный |
| `CORS_ORIGINS` | `https://admin.forkly.example.com,https://forkly.example.com,https://www.forkly.example.com` | иначе браузер заблокирует запросы |
| `SITE_ADDRESS` | `api.forkly.example.com` | включает HTTPS |
| `LOG_LEVEL` | `INFO` | |

Сгенерировать секреты пачкой:

```bash
echo "JWT_SECRET=$(openssl rand -hex 32)"
echo "MONGO_INITDB_ROOT_PASSWORD=$(openssl rand -hex 24)"
echo "REDIS_PASSWORD=$(openssl rand -hex 24)"
```

### 4.2. Закрыть порт 8000 (важно)

В `docker-compose.yml` сервис `app` по умолчанию **публикует порт 8000 на хост**:

```yaml
    ports:
      - "8000:8000"
```

На демо-стенде это лишняя экспозиция API в обход HTTPS. Закомментируйте этот
блок — Caddy ходит в контейнер по внутренней docker-сети, ему публикация не
нужна:

```yaml
    # ports:
    #   - "8000:8000"
```

### 4.3. Запуск

```bash
docker compose up -d --build
docker compose ps          # все сервисы healthy
```

Проверка:

```bash
curl -fsS https://api.forkly.example.com/health   # {"status":"ok"}
curl -fsS https://api.forkly.example.com/ready    # {"status":"ready"}
```

Если `/health` не отвечает:

```bash
docker compose logs -f caddy   # обычно проблема с DNS/сертификатом
docker compose logs -f app     # или с конфигом
```

---

## 5. Frontend: сборка статики

Admin Dashboard и Website — чистые SPA, серверу нужен только результат
`npm run build`. Собирать можно прямо на VPS (проще — не надо тащить файлы).

### 5.1. Node.js

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
node --version   # v20.x
```

### 5.2. Admin Dashboard

```bash
cd /opt/forkly/"Admin Dashboard"
cp .env.example .env.production
nano .env.production
```

Заполните (обратите внимание — обязателен trailing slash и `wss://` для WS):

```dotenv
VITE_SERVER_URL=https://api.forkly.example.com/
VITE_WS_SERVER_URL=wss://api.forkly.example.com/

VITE_CLOUDINARY_UPLOAD_URL=
VITE_CLOUDINARY_CATEGORY=
VITE_CLOUDINARY_FOOD=

# Firebase опционален — пусто = пуши в браузере отключены, панель работает
VITE_FIREBASE_API_KEY=
# ... остальные VITE_FIREBASE_* пустыми
```

> Cloudinary нужен только чтобы загружать картинки блюд из панели. Для демо
> можно оставить пустым — картинки в сид-данных придут из уже залитых URL.
> Если планируете показывать загрузку фото, заведите бесплатный аккаунт
> Cloudinary и впишите три значения.

```bash
npm ci
npm run build:prod
mkdir -p /srv/admin
cp -r dist/* /srv/admin/
```

### 5.3. Website

```bash
cd /opt/forkly/Website
cat .env.example > .env.production
nano .env.production
```

```dotenv
VITE_DEMO_URL=https://forkly.example.com/#contact
VITE_ADMIN_URL=https://admin.forkly.example.com
```

```bash
npm ci
npm run build
mkdir -p /srv/www
cp -r dist/* /srv/www/
```

---

## 6. Caddy: раздать всё с одного сервера

Сейчас `backend/Caddyfile` проксирует только API. Расширим его, чтобы тот же
Caddy отдавал статику и держал сертификаты для всех поддоменов.

Замените `backend/Caddyfile` на:

```caddyfile
# API: HTTPS-terminated reverse proxy в контейнер app.
api.forkly.example.com {
	encode gzip
	reverse_proxy app:8000
}

# Админ-панель: статика из /srv/admin (смонтировано в контейнер).
admin.forkly.example.com {
	encode gzip
	root * /srv/admin
	try_files {path} /index.html
	file_server
}

# Маркетинговый сайт.
forkly.example.com, www.forkly.example.com {
	encode gzip
	root * /srv/www
	try_files {path} /index.html
	file_server
}
```

Смонтируйте статику в контейнер Caddy — добавьте в сервис `caddy` в
`docker-compose.yml`:

```yaml
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
      - /srv/admin:/srv/admin:ro      # ← добавить
      - /srv/www:/srv/www:ro          # ← добавить
```

Перезапуск и проверка:

```bash
docker compose up -d --force-recreate caddy
docker compose logs --tail=30 caddy
```

Caddy сам получит и будет продлевать сертификаты для всех четырёх имён.
Откройте в браузере:

- `https://api.forkly.example.com/health`
- `https://admin.forkly.example.com`
- `https://forkly.example.com`

---

## 7. Демо-данные

Сидеры идемпотентны: `seed_demo.py` пересоздаёт каталог, поэтому запускать их
нужно именно в этом порядке.

```bash
cd /opt/forkly/backend
pip install httpx python-dotenv   # если не установлены
```

```bash
# 1. Каталог: 4 категории, 8 блюд с вариациями, опции, аддоны, купон,
#    тестовый покупатель customer@example.com / password123
python scripts/seed_demo.py --url https://api.forkly.example.com/graphql

# 2. Пять заказов с разными статусами (PENDING/ACCEPTED/READY/COMPLETED)
#    и разными статусами оплаты — чтобы дашборд и история заказов выглядели живыми
python scripts/seed_demo_orders.py --url https://api.forkly.example.com/graphql

# 3. Один COMPLETED-заказ для демонстрации «Оставить отзыв»
python scripts/seed_completed_order.py --url https://api.forkly.example.com/graphql
```

> `seed_demo_orders.py --clear` удалит все существующие заказы перед созданием
> новых. Флаг работает через `docker compose exec mongo mongosh`, поэтому
> запускайте его **на сервере**, из каталога `backend`.

Учётные данные берутся из `backend/.env` (`ADMIN_EMAIL` / `ADMIN_PASSWORD`),
так что ничего дописывать в скрипты не нужно.

---

## 8. CustomerApp: APK на продовый бэкенд

### 8.1. Указать продовые адреса

```bash
cd /opt/forkly/CustomerApp
cp .env.example .env
nano .env
```

```dotenv
GRAPHQL_URL=https://api.forkly.example.com/graphql
WS_GRAPHQL_URL=wss://api.forkly.example.com/graphql
SERVER_URL=https://api.forkly.example.com/
```

Остальное (Google OAuth, Amplitude, Stripe) — по мере необходимости, см. шаг 9.

> `wss://` обязателен: на `ws://` браузер/Android заблокирует WebSocket, и
> живые обновления статуса заказа работать не будут.

### 8.2. Сборка

```bash
cd CustomerApp/android
./gradlew assembleRelease      # на Windows: .\gradlew.bat assembleRelease
```

APK: `CustomerApp/android/app/build/outputs/apk/release/app-release.apk`.

Для демо APK подписывается debug-ключом (Gradle подставит его автоматически).
Этого достаточно, чтобы поставить приложение на телефон заказчика вручную.

> Долгие сборки на слабом VPS могут упасть по памяти. Если Gradle падает с
> `OutOfMemoryError`, поднимите лимиты в `android/gradle.properties`
> (`org.gradle.jvmargs=-Xmx3072m -XX:MaxMetaspaceSize=1024m`) и добавьте swap.
> Проще собирать APK на локальной машине — адреса в `.env` те же.

### 8.3. Про cleartext HTTP

`CustomerApp/android/app/src/main/res/xml/network_security_config.xml`
разрешает незашифрованный HTTP **только** для локальных адресов
(`10.0.2.2`, `localhost`, `127.0.0.1`). На демо-стенде бэкенд работает по
HTTPS, поэтому это ограничение не мешает — и не ослабляет безопасность
продовой сборки.

---

## 9. Приём оплаты (Stripe в тестовом режиме)

Оплата работает так: приложение открывает Stripe Checkout с **публикуемым**
ключом, получает токен карты и отправляет его на бэкенд (`POST /stripe/charge`),
который списывает деньги **секретным** ключом. Ключи хранятся в разных местах —
это важно не перепутать.

### 9.1. Публикуемый ключ → в приложение

1. Аккаунт [Stripe](https://dashboard.stripe.com) → переключитесь в **Test mode**.
2. Developers → API keys → скопируйте **Publishable key** (`pk_test_...`).
3. В `CustomerApp/.env`:

```dotenv
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_STORE_NAME=Forkly
STRIPE_IMAGE_URL=https://forkly.example.com/og-image.png
```

4. Пересобрать APK (шаг 8.2) — ключ вшивается в бандл при сборке.

### 9.2. Секретный ключ → в панель админа

Секретный ключ **не** хранится в `.env`: он пишется в конфигурацию через мутацию
`saveStripeConfiguration` (раздел **Configuration** в админ-панели) и уже оттуда
используется бэкендом при списании.

1. Скопируйте **Secret key** (`sk_test_...`).
2. В админке: `https://admin.forkly.example.com` → **Configuration**.
3. Заполните **Publishable key** и **Secret key** тестовыми значениями, сохраните.

> ⚠️ Секретный ключ (`sk_test_...`) — это доступ к вашему Stripe-аккаунту.
> Никогда не кладите его в `CustomerApp/.env`, в код или в git: только в панель
> администратора (см. `.cursor/rules/security-secrets.mdc`).

### 9.3. Проверка

- Валюта заказа должна поддерживаться Stripe. Для демо выставьте USD:
  `seed_demo.py` уже ставит `USD` / `$`.
- Тестовая карта: `4242 4242 4242 4242`, любой будущий срок, любой CVC.
- В приложении при оформлении выберите способ оплаты картой.

Если показывать оплату не планируете — оставьте Stripe пустым: заказ пройдёт как
COD (`Cash on pickup`), а весь остальной флоу работает.

---

## 10. Финальная проверка перед демо

```bash
# Здоровье сервисов
curl -fsS https://api.forkly.example.com/health
curl -fsS https://api.forkly.example.com/ready

# Сквозной сценарий на бэкенде: заказ → принят → готов → выдан + WebSocket
cd /opt/forkly/backend
python scripts/e2e_pickup_smoke.py \
  --url https://api.forkly.example.com/graphql \
  --ws wss://api.forkly.example.com/graphql
```

> `--ws` обязателен отдельно — скрипт не выводит его из `--url`. Учётные данные
> админа берутся из `backend/.env`. Скрипт регистрирует собственного покупателя
> и создаёт **новые заказы**, поэтому после его прогона перезалейте демо-данные:
> `python scripts/seed_demo_orders.py --clear`.

Чек-лист вручную:

- [ ] `https://forkly.example.com` — сайт открывается, HTTPS-замок, переключатель языков работает
- [ ] `https://admin.forkly.example.com` — логин `ADMIN_EMAIL`/`ADMIN_PASSWORD`
- [ ] Дашборд показывает ненулевые **Total Orders** и **Total Sales**
- [ ] Раздел **Orders** открывается и показывает 5 заказов со статусами (не белый экран!)
- [ ] Раздел **Food** — 8 блюд, **Category** — 4 категории
- [ ] APK установлен на телефон, каталог грузится, заказ оформляется
- [ ] Новый заказ **сразу** появляется в админке (проверка WebSocket)
- [ ] Смена статуса в админке → покупатель видит обновление без перезагрузки
- [ ] История заказов в приложении открывается (раздел с заказами, не падает)
- [ ] Оплата тестовой картой (если показываете)

---

## 11. Обслуживание

```bash
cd /opt/forkly/backend

# Обновление кода
git pull
docker compose up -d --build --remove-orphans

# Обновление статики после правок фронтенда
cd "/opt/forkly/Admin Dashboard" && npm ci && npm run build:prod && cp -r dist/* /srv/admin/
cd /opt/forkly/Website && npm ci && npm run build && cp -r dist/* /srv/www/

# Логи
docker compose logs -f app
```

Бэкапы: сервис `backup` раз в сутки складывает дамп в
`backend/backups/forkly_<timestamp>.archive.gz` и хранит 14 последних. Настройте
выгрузку этой папки за пределы сервера (rsync/S3) — подробности в
`backend/DEPLOY.md`.

---

## 12. Смета

| Статья | Стоимость |
|--------|-----------|
| VPS 2 vCPU / 4 GB | ~500–700 ₽/мес (Timeweb) или ~€4.5/мес (Hetzner) |
| Домен `.ru` | ~200–400 ₽/год |
| Wildcard-сертификат TLS | 0 ₽ (Let's Encrypt через Caddy, автоматически) |
| MongoDB, Redis, бэкапы | 0 ₽ (на том же VPS) |
| **Итого** | **~700–900 ₽/мес** |

---

## 13. Что может пойти не так

| Симптом | Причина | Что делать |
|---------|---------|------------|
| `/health` не отвечает, Caddy пишет про ACME | DNS ещё не разрешается или закрыт порт 80 | Проверьте A-записи и `ufw status` |
| Caddy отдаёт 502 | Контейнер `app` не поднялся | `docker compose logs app` |
| Админка грузится, но данных нет | `CORS_ORIGINS` не содержит домен админки | Дописать origin, `docker compose up -d app` |
| Дашборд пустой, в консоли ошибки Apollo | Неверный `VITE_SERVER_URL` при сборке | Проверьте trailing slash, пересоберите статику |
| Заказы не обновляются в реальном времени | `VITE_WS_SERVER_URL` / `WS_GRAPHQL_URL` не `wss://` | Исправить и пересобрать |
| APK не ставится на телефон | Старая версия с другим package id | Удалите прежнее приложение, поставьте APK заново |
| Gradle падает с `OutOfMemoryError` | Мало памяти на VPS | Соберите APK локально или поднимите `org.gradle.jvmargs` |
| Заказы в админке показывают «Unknown item» | Заказ ссылается на удалённое блюдо | Пересоздайте заказы: `seed_demo_orders.py --clear` |

---

## 14. Чек-лист демо-дня

1. За час до показа: `docker compose ps` — все `healthy`.
2. Прогнать `e2e_pickup_smoke.py` — убедиться, что бэкенд живой.
3. Проверить, что в админке есть заказы и они открываются.
4. Установить свежий APK на телефон и **залогиниться заранее**.
5. Открыть вкладки: сайт, админка (залогинена), приложение.
6. Держать под рукой: логин/пароль админа, тестовую карту `4242 4242 4242 4242`.
7. Демо-сценарий: сайт → админка (заказы) → приложение (заказ) → заказ появляется
   в админке → смена статуса → приложение обновляется → выдача заказа → отзыв.
