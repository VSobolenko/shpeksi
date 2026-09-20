# Pikupo — ранбук демо-стенда (вариант Б1: VPS + Caddy + HTTPS)

Пошаговая инструкция, как поднять демо для заказчика на собственном сервере:
бэкенд с HTTPS, админ-панель, сайт и Android-APK, который на всё это смотрит.

Время: ~1.5–2 часа. Стоимость: ~$25–40/мес (VPS), домен — по желанию (см. §1.1).

> Плейсхолдеры: `203.0.113.10` — IP сервера, `example.com` — ваш домен.
> `Pikupo` — рабочее имя: продукт ребрендится, поэтому домен под него пока **не
> покупается**. Вместо домена примеры используют `sslip.io` (§1.1) — он даёт
> настоящий HTTPS-сертификат без покупки домена.

---

## Стенд уже поднят: фактические адреса

Всё, что ниже, — инструкция «с нуля» на случай переезда. Актуальное состояние
развёрнутого стенда:

| Что | Значение |
|-----|----------|
| API (HTTP + WebSocket) | `https://api.78-111-89-46.sslip.io/graphql` |
| Админ-панель | `https://admin.78-111-89-46.sslip.io` |
| Сайт | `https://78-111-89-46.sslip.io` (+ `www.`) |
| APK для скачивания | `https://78-111-89-46.sslip.io/downloads/pikupo-demo-v1.0.23.apk` |
| Вход в админку | `admin@pikupo.com`, пароль — в `/opt/pikupo/backend/.env` (`ADMIN_PASSWORD`) |
| Клиент в приложении | `customer@example.com` / `password123` (сид-фикстура) |
| Сервер | Serverspace, Нью-Джерси; 2 vCPU / 3.3 ГБ / 49 ГБ; Ubuntu 26.04 |
| Код на сервере | `/opt/pikupo` (клон из `git bundle`, см. ниже) |
| Секреты | `/opt/pikupo/backend/.env`, права `600`, сгенерированы на сервере |

> Пароль админа намеренно **не** вписан в этот файл: ранбук лежит в git. Смотрите
> его на сервере: `grep ADMIN_PASSWORD /opt/pikupo/backend/.env`.

### Что с APK прямо сейчас

Опубликован `pikupo-demo-v1.0.23.apk` (Pikupo, API на `sslip.io`). Старый
`forkly-demo-v1.0.22.apk` может ещё лежать рядом — для демо используйте новую
ссылку. После покупки домена APK нужно будет пересобрать один раз под
`api.pikupo.com`.

### Что уже проверено

- `mongo` и `redis` — healthy; `app` — healthy, `/health` и `/ready` отвечают
  `{"status":"ok"}` / `{"status":"ready"}`.
- Caddy выпустил 4 сертификата Let's Encrypt (apex, `www`, `api`, `admin`).
- Все адреса отдают `200` снаружи, TLS валиден.
- `scripts/e2e_pickup_smoke.py` против **публичных** HTTPS/WSS-адресов —
  `ALL E2E CHECKS PASSED` (включая WebSocket-подписки на обоих протоколах).
- Сид: 4 категории, 8 блюд, купон `SAVE10`, 6 заказов в разных статусах,
  1 покупатель `customer@example.com` (состояние после сброса от 17.09.2026).
- После переименования в `Pikupo` стенд перепроверен целиком: вход в админку по
  HTTPS, дашборд (заказы, продажи, графики), страница `Orders` со списком
  заказов и сайт с брендом `Pikupo` — в консоли браузера ноль ошибок.
- Заказы нумеруются с префиксом `PKP-` (поле `Order ID Prefix` в Configuration).
- APK раздаётся по HTTPS с корректным типом
  `application/vnd.android.package-archive`, `Accept-Ranges: bytes` (докачка
  поддерживается, `206` на частичный запрос), md5 сходится с локальной сборкой.

### Как опубликован APK

Файл лежит в `backend/static/downloads/` и монтируется в Caddy как `/srv`
(тот же том, что и `static`), а отдаётся через отдельный маршрут в
`Caddyfile.prod`:

```caddyfile
	# Внутри блока {$SITE_ADDRESS}
	handle_path /downloads/* {
		root * /srv/downloads
		file_server
	}
```

Каталог намеренно **вне** `/srv/www`: пересборка сайта заменяет `/srv/www`
целиком, и APK, положенный туда, был бы удалён. `/srv/downloads` пересборка не
затрагивает. Маршрут изолирован — несуществующий файл отдаёт `404`, а не
подменяется `index.html` SPA-фолбэком.

Залить новую сборку и проверить:

```bash
# локально (PowerShell)
scp -i %USERPROFILE%\.ssh\id_ed25519 ^
  "CustomerApp\android\app\build\outputs\apk\release\app-release.apk" ^
  root@78.111.89.46:/opt/pikupo/backend/static/downloads/pikupo-demo-v1.0.23.apk

# сверить, что долетело без повреждений
Get-FileHash -Algorithm MD5 "CustomerApp\android\app\build\outputs\apk\release\app-release.apk"
ssh -i %USERPROFILE%\.ssh\id_ed25519 root@78.111.89.46 "md5sum /opt/pikupo/backend/static/downloads/pikupo-demo-v1.0.23.apk"
```

> В каталоге сейчас лежит `forkly-demo-v1.0.22.apk` (см. «Что с APK прямо
> сейчас» выше). Новую сборку кладите рядом со своим именем и удаляйте старую,
> только когда ссылка на новую уже проверена снаружи.

> При замене APK имя файла меняйте вместе с версией (`app.json` → `version`) —
> иначе у заказчика в кэше останется старая сборка под тем же URL.

После правки `Caddyfile.prod` перезагружать Caddy нужно **только** для конфига
(статика читается с диска):

```bash
cd /opt/pikupo/backend
docker compose exec -T caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile </dev/null
```

> `</dev/null` обязателен, если команда запускается по `ssh host "bash -s"` со
> скриптом на stdin: без него `docker compose exec` вычитывает остаток скрипта.

### Обновление кода на сервере

Репозиторий приватный, IPv4-адрес сервера блокуется GitHub для SSH. Поэтому код
заливается архивом, а не клоном с GitHub:

```bash
# на локальной машине
git bundle create %TEMP%\pikupo.bundle main
scp -i %USERPROFILE%\.ssh\id_ed25519 %TEMP%\pikupo.bundle root@78.111.89.46:/opt/pikupo.bundle

# на сервере
cd /opt/pikupo && git pull /opt/pikupo.bundle main
```

После обновления бэкенда — `docker compose up -d --build app`. После изменения
фронтендов — повторить §5 и перезапустить Caddy не нужно (статика отдаётся с
диска), достаточно пересобрать в `backend/static/`.

### Пересоздать демо-данные с нуля

```bash
cd /opt/pikupo/backend
docker compose exec -T app python /tmp/scripts/seed_demo.py          --url http://localhost:8000/graphql
docker compose exec -T app python /tmp/scripts/seed_demo_orders.py   --url http://localhost:8000/graphql
docker compose exec -T app python /tmp/scripts/seed_completed_order.py --url http://localhost:8000/graphql
```

Скрипты берут `ADMIN_EMAIL`/`ADMIN_PASSWORD` из окружения контейнера `app`, то
есть из `backend/.env` — дописывать ничего не нужно. Скриптов нет внутри образа
(в `Dockerfile` копируется только `app/`), поэтому их сначала копируют в
контейнер: `docker compose cp scripts/. app:/tmp/scripts/`.

`e2e_pickup_smoke.py` создаёт свою категорию, блюдо, пользователя и заказ, то
есть после прогона демо-каталог стоит пересобрать по шагам выше.

### Известные особенности `.env` на сервере

`SITE_ADDRESS` содержит запятую с пробелом (apex + `www`), поэтому значение
записано в кавычках — так файл можно подключать через `source` (именно это
делает `pikupo-reset-demo.sh`), иначе шелл падает на строке
`www...: command not found`. Docker Compose кавычки снимает и передаёт в Caddy
значение `78-111-89-46.sslip.io, www.78-111-89-46.sslip.io` как есть.

### Переименование в Pikupo: что именно менялось 17.09.2026

Код переехал в `/opt/pikupo`, база — в `pikupo`, префикс заказов — `PKP`,
админ — `admin@pikupo.com`. Хост-каталог переименован вместе с
`/opt/pikupo-ops`; имена контейнеров и томов не изменились (compose-проект
называется `backend`, он берётся из имени каталога `backend/`), поэтому
сертификаты и данные пережили переезд без вмешательства.

Урок, который стоил одной пересборки базы: **`backend/.env` нельзя возить в
архиве с кодом**. Архив, собранный из рабочей копии, тащит за собой локальный
дев-`.env`, и при распаковке поверх сервера он затирает продовый — вместе с
паролем Mongo, `SITE_ADDRESS`, `CADDYFILE=Caddyfile.prod` и `JWT_SECRET`.
Пароль Mongo восстановить нельзя (в томе лежит только хеш), поэтому том Mongo
был пересоздан, а демо-данные пересеяны. Штатный путь обновления кода —
`git bundle` (§«Обновление кода на сервере»), он `.env` не переносит. Если всё
же нужен архив, исключайте `backend/.env`, `*/.env`, `backend/backups` и
`backend/static`:

```bash
tar --exclude='.git' --exclude='*/.env' --exclude='backend/.env' \
    --exclude='node_modules' --exclude='dist' --exclude='build' \
    --exclude='backend/backups' --exclude='backend/static' \
    -czf pikupo-src.tgz .
```

Старые данные перед пересозданием тома сняты дампом
`backend/backups/pre-pikupo-rescue.archive` (mongodump, все БД) — поднять
обратно при необходимости:

```bash
docker compose exec -T backup mongorestore \
  --host mongo --username "$MONGO_INITDB_ROOT_USERNAME" \
  --password "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin \
  --drop --gzip --archive=/backups/pre-pikupo-rescue.archive </dev/null
```

Продовый `.env` после инцидента собран заново: секреты (`MONGO_INITDB_ROOT_PASSWORD`,
`REDIS_PASSWORD`, `JWT_SECRET`) сгенерированы на сервере заново, поэтому все
выданные ранее токены недействительны — приложение потребует войти снова.

---

## 0. Что получится в итоге

```
                        ┌──────────────────────────────────────┐
                        │  Caddy (:80/:443, Let's Encrypt)     │
   api.<ip>         ───▶│    ├── /graphql → app:8000           │
   admin.<ip>       ───▶│    ├── /health  → app:8000           │
   <ip>, www.<ip>   ───▶│    ├── admin.*  → /srv/admin         │  статика
                        │    └── apex/www → /srv/www           │  статика
                        └──────────────────────────────────────┘
                                  ▲          ▲          ▲
                              mongo:7   redis:7    backup

   <ip> = 203-0-113-10.sslip.io; после покупки домена — ваш домен.
   Порт 8000 у app привязан к 127.0.0.1 и снаружи недоступен.
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

### 1.1. Домен — на время демо не нужен

Caddy получает сертификат Let's Encrypt через ACME, и для этого ему нужен не
домен как таковой, а **имя, которое разрешается в IP сервера**. Публичный
wildcard-DNS [sslip.io](https://sslip.io) выдаёт такое имя бесплатно: он
превращает IP, записанный с дефисами вместо точек, обратно в A-запись.

Для сервера с IP `203.0.113.10` это даёт готовый набор адресов:

| Роль | Адрес |
|------|-------|
| API | `api.203-0-113-10.sslip.io` |
| Админ-панель | `admin.203-0-113-10.sslip.io` |
| Сайт | `203-0-113-10.sslip.io` (и `www.203-0-113-10.sslip.io`) |

Сертификат при этом **настоящий**, а не самоподписанный: браузеры и
Android-приложение работают с ним без ослабления проверок.

Убедитесь, что имя разрешается именно в ваш IP (подставьте свой):

```bash
nslookup api.203-0-113-10.sslip.io
```

Когда продукт получит финальное имя — покупаете домен и меняете три переменные
в `backend/.env` (§4.1); больше ничего трогать не нужно.

> Если домен уже есть — берите его, `sslip.io` тогда не нужен. Поддомены
> (`api.`, `admin.`, `www.`) выдаются бесплатно, A-записи на IP сервера — как в
> §2. Регистраторы: Cloudflare Registrar (`.com`, ~$10, нужна зарубежная
> карта), HB.BY / reg.ru / Timeweb (оплата локальной картой).

### 1.2. VPS — что заказывать

Нужно минимум **2 vCPU / 4 GB RAM / 40 GB SSD**, Ubuntu 24.04 LTS.

Главное ограничение — не цена, а **оплата**: большинство европейских
провайдеров не принимают карты РБ, поэтому выбирать приходится из тех, кто
принимает локальную карту.

| Провайдер | Конфигурация | Цена/мес (ориентир) | Оплата / площадки |
|-----------|--------------|---------------------|-------------------|
| **[Serverspace](https://serverspace.io/)** | 2 vCPU / 4–5 GB / 60 GB | ~$37 на VMware; на vStack — в разы дешевле (см. ниже) | карты РБ / МИР, безнал. Амстердам (ЕС), Нью-Джерси (США) |
| [Hetzner](https://www.hetzner.com/cloud/) (CX22) | 2 vCPU / 4 GB / 40 GB | ~€4.5 | дешевле всех при том же железе, но нужна зарубежная карта и возможна верификация личности |

**Про Serverspace — два важных момента:**

1. **Платформа.** У них две: `vStack` и `VMware`. VMware — это
   «enterprise»-тариф, и он стоит в разы дороже за то же железо (у них же один и
   тот же конфиг: ~13.94 € на VMware против ~4.55 € на vStack). Если цена пришла
   в районе $37 — это она и есть. **Берите vStack.**

   На vStack проверьте, что Docker работает: он бывает контейнерной
   виртуализацией, где свой kernel не поднять.

   ```bash
   docker run --rm hello-world
   uname -a
   ```

   Весь наш стек живёт в контейнерах, поэтому если Docker не запустится, площадку
   надо менять — и лучше узнать это до демо, а не во время.

2. **Площадка.** Под ваши рынки подходят Амстердам (ЕС) и Нью-Джерси (США).
   Дубай, Алматы, Ташкент, Москва, Сан-Паулу и Торонто для Европы/США не
   подходят: задержка до целевого рынка будет заметна на демо. Амстердам
   периодически распродан — если так, берите Нью-Джерси: это крупнейший из двух
   рынков, а европейскую площадку можно поднять позже и перенести туда
   конфигурацию. Деплой воспроизводимый, ручной привязки к серверу нет.

При заказе выберите образ **Ubuntu 24.04 LTS** и сразу добавьте свой SSH-ключ
(парольный вход потом отключим).

---

## 2. DNS

**Если используете `sslip.io` — этот шаг пропускается.** Адреса уже разрешаются
в IP сервера, достаточно убедиться в этом:

```bash
nslookup api.203-0-113-10.sslip.io
```

**Если у вас свой домен** — добавьте A-записи на IP сервера в панели
регистратора:

| Тип | Имя | Значение | TTL |
|-----|-----|----------|-----|
| A | `api` | `203.0.113.10` | 300 |
| A | `admin` | `203.0.113.10` | 300 |
| A | `www` | `203.0.113.10` | 300 |
| A | `@` (корень) | `203.0.113.10` | 300 |

Проверка (подождите 5–15 минут):

```bash
nslookup api.example.com
```

Должен вернуться IP сервера. **Не идите дальше, пока DNS не разрешается** —
Caddy выдаёт сертификаты через ACME и при неверном DNS упрётся в лимит попыток.
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
git clone <URL-вашего-репозитория> pikupo
cd pikupo/backend
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
| `MONGO_INITDB_ROOT_USERNAME` | `pikupo` | |
| `MONGO_INITDB_ROOT_PASSWORD` | `openssl rand -hex 24` | уникальный |
| `REDIS_PASSWORD` | `openssl rand -hex 24` | уникальный |
| `CORS_ORIGINS` | `https://admin.203-0-113-10.sslip.io,https://203-0-113-10.sslip.io,https://www.203-0-113-10.sslip.io` | иначе браузер заблокирует запросы |
| `CADDYFILE` | `Caddyfile.prod` | включает prod-конфиг Caddy: HTTPS + раздача статики |
| `API_ADDRESS` | `api.203-0-113-10.sslip.io` | адрес API; для него Caddy берёт сертификат |
| `ADMIN_ADDRESS` | `admin.203-0-113-10.sslip.io` | адрес админ-панели |
| `SITE_ADDRESS` | `203-0-113-10.sslip.io, www.203-0-113-10.sslip.io` | адрес сайта; список через запятую (apex + www) |
| `LOG_LEVEL` | `INFO` | |

Сгенерировать секреты пачкой:

```bash
echo "JWT_SECRET=$(openssl rand -hex 32)"
echo "MONGO_INITDB_ROOT_PASSWORD=$(openssl rand -hex 24)"
echo "REDIS_PASSWORD=$(openssl rand -hex 24)"
```

### 4.2. Порт 8000 — уже закрыт, ничего делать не нужно

В `docker-compose.yml` порт привязан к loopback: `127.0.0.1:8000:8000`. Это
значит, что на сервере API недоступен из интернета (Caddy ходит в контейнер по
внутренней docker-сети и публикация ему не нужна), а на локальной машине
`http://localhost:8000` работает как раньше — удобно для скриптов и отладки.

### 4.3. Запуск

```bash
docker compose up -d --build
docker compose ps          # все сервисы healthy
```

Проверка:

```bash
curl -fsS https://api.203-0-113-10.sslip.io/health   # {"status":"ok"}
curl -fsS https://api.203-0-113-10.sslip.io/ready    # {"status":"ready"}
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

> **Важно:** production-сборка **обязана** смотреть на публичный API
> (`https://api.<ip>.sslip.io/`), а не на `localhost:8000`. Vite вшивает
> `VITE_*` в бандл на этапе `build` — если собрать с `.env.example`
> (localhost), опубликованная админка будет бить в несуществующий локальный
> бэкенд. Используйте `.env.production.example` → `.env.production`.

```bash
cd /opt/pikupo/"Admin Dashboard"
cp .env.production.example .env.production
nano .env.production
```

Заполните (обратите внимание — обязателен trailing slash и `wss://` для WS).
Для текущего демо-стенда значения уже в `.env.production.example`:

```dotenv
VITE_SERVER_URL=https://api.203-0-113-10.sslip.io/
VITE_WS_SERVER_URL=wss://api.203-0-113-10.sslip.io/

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
cd /opt/pikupo/Website
cat .env.example > .env.production
nano .env.production
```

```dotenv
VITE_DEMO_URL=https://203-0-113-10.sslip.io/#contact
VITE_ADMIN_URL=https://admin.203-0-113-10.sslip.io
```

```bash
npm ci
npm run build
mkdir -p /srv/www
cp -r dist/* /srv/www/
```

---

## 6. Caddy: раздать всё с одного сервера

Ничего править не нужно: prod-конфиг уже лежит в репозитории
(`backend/Caddyfile.prod`) и включается переменной `CADDYFILE=Caddyfile.prod`
(§4.1). Он отдаёт API, админку и сайт и берёт сертификаты для всех адресов из
`API_ADDRESS` / `ADMIN_ADDRESS` / `SITE_ADDRESS`:

```caddyfile
{$API_ADDRESS} {
	encode gzip
	reverse_proxy app:8000
}

{$ADMIN_ADDRESS} {
	encode gzip
	root * /srv/admin
	try_files {path} /index.html
	file_server
}

{$SITE_ADDRESS} {
	encode gzip
	root * /srv/www
	try_files {path} /index.html
	file_server
}
```

Адреса вынесены в переменные именно затем, чтобы переход с `sslip.io` на
настоящий домен не требовал правки конфига — достаточно поменять `.env` и
перезапустить Caddy.

Статика монтируется в контейнер автоматически: `backend/static` виден внутри
Caddy как `/srv`. Разложите собранные фронтенды (см. шаг 5) по местам, которых
ждёт конфиг:

```bash
cd /opt/pikupo/backend
mkdir -p static/admin static/www

cp -r "/opt/pikupo/Admin Dashboard/dist/." static/admin/
cp -r /opt/pikupo/Website/dist/. static/www/
```

Перезапуск и проверка:

```bash
docker compose up -d --force-recreate caddy
docker compose logs --tail=30 caddy
```

Caddy сам получит и будет продлевать сертификаты для всех имён. Откройте в
браузере:

- `https://api.203-0-113-10.sslip.io/health`
- `https://admin.203-0-113-10.sslip.io`
- `https://203-0-113-10.sslip.io`

---

## 7. Демо-данные

Сидеры идемпотентны: `seed_demo.py` пересоздаёт каталог, поэтому запускать их
нужно именно в этом порядке.

```bash
cd /opt/pikupo/backend
pip install httpx python-dotenv   # если не установлены
```

```bash
# 1. Каталог: 4 категории, 8 блюд с вариациями, опции, аддоны, купон,
#    тестовый покупатель customer@example.com / password123
python scripts/seed_demo.py --url https://api.203-0-113-10.sslip.io/graphql

# 2. Пять заказов с разными статусами (PENDING/ACCEPTED/READY/COMPLETED)
#    и разными статусами оплаты — чтобы дашборд и история заказов выглядели живыми
python scripts/seed_demo_orders.py --url https://api.203-0-113-10.sslip.io/graphql

# 3. Один COMPLETED-заказ для демонстрации «Оставить отзыв»
python scripts/seed_completed_order.py --url https://api.203-0-113-10.sslip.io/graphql
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
cd /opt/pikupo/CustomerApp
cp .env.example .env
nano .env
```

```dotenv
GRAPHQL_URL=https://api.203-0-113-10.sslip.io/graphql
WS_GRAPHQL_URL=wss://api.203-0-113-10.sslip.io/graphql
SERVER_URL=https://api.203-0-113-10.sslip.io/
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

> **Не запускайте `clean` вместе с `assembleRelease`.** Задача
> `:app:externalNativeBuildCleanRelease` удаляет сгенерированные codegen-каталоги
> нативных модулей, а CMake в этот же момент пытается переконфигурироваться и
> падает с `add_subdirectory given source ... which is not an existing directory`
> и `Cannot specify link libraries for target "react_codegen_AmplitudeReactNative"`.
> Сборка при этом не страдает — падает только очистка. Если нужен чистый билд:
> сначала `./gradlew clean` отдельно (он может упасть, это ожидаемо), затем
> `./gradlew assembleRelease`. Ещё надёжнее — `npx expo prebuild --platform android --clean`.

> **Значения из `.env` вшиваются в APK при сборке** (`app.config.js` копирует их в
> `Constants.expoConfig.extra`). Меняете адрес бэкенда — обязателен пересбор.

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
STRIPE_STORE_NAME=Pikupo
STRIPE_IMAGE_URL=https://203-0-113-10.sslip.io/og-image.png
```

4. Пересобрать APK (шаг 8.2) — ключ вшивается в бандл при сборке.

### 9.2. Секретный ключ → в панель админа

Секретный ключ **не** хранится в `.env`: он пишется в конфигурацию через мутацию
`saveStripeConfiguration` (раздел **Configuration** в админ-панели) и уже оттуда
используется бэкендом при списании.

1. Скопируйте **Secret key** (`sk_test_...`).
2. В админке: `https://admin.203-0-113-10.sslip.io` → **Configuration**.
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
curl -fsS https://api.203-0-113-10.sslip.io/health
curl -fsS https://api.203-0-113-10.sslip.io/ready

# Сквозной сценарий на бэкенде: заказ → принят → готов → выдан + WebSocket
cd /opt/pikupo/backend
python scripts/e2e_pickup_smoke.py \
  --url https://api.203-0-113-10.sslip.io/graphql \
  --ws wss://api.203-0-113-10.sslip.io/graphql
```

> `--ws` обязателен отдельно — скрипт не выводит его из `--url`. Учётные данные
> админа берутся из `backend/.env`. Скрипт регистрирует собственного покупателя
> и создаёт **новые заказы**, поэтому после его прогона перезалейте демо-данные:
> `python scripts/seed_demo_orders.py --clear`.

Чек-лист вручную:

- [ ] `https://203-0-113-10.sslip.io` — сайт открывается, HTTPS-замок, переключатель языков работает
- [ ] `https://admin.203-0-113-10.sslip.io` — логин `ADMIN_EMAIL`/`ADMIN_PASSWORD`
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
cd /opt/pikupo/backend

# Обновление кода
git pull
docker compose up -d --build --remove-orphans

# Обновление статики после правок фронтенда
cd "/opt/pikupo/Admin Dashboard" && npm ci && npm run build:prod && cp -r dist/* /srv/admin/
cd /opt/pikupo/Website && npm ci && npm run build && cp -r dist/* /srv/www/

# Логи
docker compose logs -f app
```

Бэкапы: сервис `backup` раз в сутки складывает дамп в
`backend/backups/pikupo_<timestamp>.archive.gz` и хранит 14 последних. Настройте
выгрузку этой папки за пределы сервера (rsync/S3) — подробности в
`backend/DEPLOY.md`.

---

## 12. Смета

| Статья | Стоимость |
|--------|-----------|
| VPS 2 vCPU / 4 GB | ~$25–40/мес (Serverspace vStack, Нью-Джерси/Амстердам); ~€4.5/мес (Hetzner, если доступен) |
| Домен | **$0 на время демо** — `sslip.io`; позже ~$10/год (Cloudflare Registrar) или локальный регистратор |
| TLS-сертификаты | $0 (Let's Encrypt через Caddy, автоматически и продлеваются сами) |
| MongoDB, Redis, бэкапы | $0 (на том же VPS) |
| **Итого** | **~$25–40/мес**, домен — потом |

---

## 13. Что может пойти не так

| Симптом | Причина | Что делать |
|---------|---------|------------|
| `/health` не отвечает, Caddy пишет про ACME | Имя не разрешается в IP сервера или закрыт порт 80 | `nslookup <адрес>`; затем `ufw status` |
| `docker compose up` падает: тома и сеть не создаются | Площадка на контейнерной виртуализации, где Docker не работает | `docker run --rm hello-world`; при провале — менять площадку (§1.2) |
| Caddy отвечает, но админка или сайт пустые / 404 | Статика не разложена в `backend/static/admin` и `static/www` | См. §6 |
| Caddy отдаёт 502 | Контейнер `app` не поднялся | `docker compose logs app` |
| Админка грузится, но данных нет | `CORS_ORIGINS` не содержит адрес админки | Дописать origin, `docker compose up -d app` |
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
