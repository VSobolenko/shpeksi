# Forkly — описание проекта (для новых разработчиков)

> Русскоязычный онбординг по проекту. Актуальное состояние кода, а не
> историческая документация. Полный гайд для ИИ-агентов — в `AGENTS.md`,
> основной документ проекта — в `README.md`.

## Что это за проект

**Forkly** — платформа заказа еды с **самовывозом** (self-pickup). Клиент
выбирает блюда в мобильном приложении, оформляет заказ и забирает его в
ресторане. **Доставки и курьеров нет** — модель только «самовывоз».

Монрепозиторий содержит три приложения + бэкенд:

| Модуль | Назначение | Стек |
| ------ | ---------- | ---- |
| `backend/` | Самодостаточный GraphQL API (HTTP + WebSocket) | Python: FastAPI + Strawberry + Beanie/MongoDB + Redis |
| `Admin Dashboard/` | Веб-панель мерчанта: меню, заказы, настройки | React 18 + Vite + Apollo Client 3 |
| `CustomerApp/` | Мобильное приложение клиента: заказ и самовывоз | React Native + Expo + Apollo Client 3 |
| `Website/` | Публичный маркетинговый лендинг | Vite + React 18 |

> Модуль доставки `RiderApp/` **удалён**. Платформа работает только в режиме
> самовывоза.

## Технологический стек (актуальный)

### Бэкенд — `backend/`

- **FastAPI** (ASGI) + **Uvicorn**
- **Strawberry GraphQL** (code-first, async, подписки)
- **MongoDB** + **Beanie** (Motor + Pydantic v2)
- **Redis** (опционально; при пустом `REDIS_URL` используется in-memory pub/sub)
- **python-jose** (JWT) + **bcrypt** (хэширование паролей)
- **Stripe** + **PayPal** (платежи), **firebase-admin** (FCM push), **aiosmtplib** (email)
- На одном эндпоинте поддерживаются оба WebSocket-протокола подписок:
  `graphql-transport-ws` (новый) и `graphql-ws` / `subscriptions-transport-ws` (legacy).
- Продакшн: не-root `Dockerfile`, `docker-compose.yml`, Caddy (авто-HTTPS),
  бэкапы MongoDB, healthcheck. Полная инструкция — в `backend/DEPLOY.md`.

### Admin Dashboard — `Admin Dashboard/`

- **React 18.2**, **Vite 5**, `@vitejs/plugin-react`
- **Apollo Client 3.8** (`@apollo/client`) + `subscriptions-transport-ws`
- **Material UI 4**, **reactstrap**, **styled-components**
- **Chart.js 4** + `react-chartjs-2`
- **React Router 6**, **Firebase 10** (FCM), **i18next**
- E2E-тесты на **Playwright** (`npm run test:e2e`)

### CustomerApp — `CustomerApp/`

- **React Native 0.86**, **Expo SDK 57**, **React 19**
- **Apollo Client 3.8** + `subscriptions-transport-ws`, `apollo3-cache-persist`
- **React Navigation 7** (native-stack, stack, drawer)
- **i18n-js** (локализация), **Amplitude** (аналитика), **Reanimated 4**
- Тесты на **Jest** (`jest-expo`)

### Website — `Website/`

- **Vite + React 18**, plain JS, **i18next** + **react-i18next**
- **CSS Modules** + CSS-переменные (дизайн-токены)
- 7 языков (`en`, `ar`, `de`, `fr`, `km`, `ru`, `zh`), RTL для арабского.
  Статический билд в `dist/`.
- Не обращается к GraphQL API — чисто статический маркетинговый сайт.

## Структура репозитория

```
backend/            Python GraphQL backend (app/{graphql,models,services,integrations}, tests, scripts)
Admin Dashboard/    React admin panel (Vite) — src/, e2e/, playwright.config.js
CustomerApp/        React Native customer app (Expo) — src/, translations/
Website/            маркетинговый лендинг (Vite + React 18)
openspec/           OpenSpec: изменения (changes/) и основные спеки (specs/)
.superpowers/       SDD-журнал (планы и отчёты по задачам)
.agents/skills/     навыки superpowers + expo
.cursor/            правила (rules/), навыки (skills/), команды (commands/), хуки (hooks/), mcp.json
scripts/            setup-mcp.mjs — проверка настройки MCP-серверов
```

## Как запустить проект

Требования: **Node.js 18/20 LTS**, **Python 3.11+**, **MongoDB** (локально или
Atlas), опционально **Redis**.

### 1. Бэкенд

```bash
cd backend
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env        # заполнить Mongo URL, JWT secret, admin-доступы
uvicorn app.main:app --reload --port 8000
```

GraphQL-эндпоинт: `http://localhost:8000/graphql` (в dev доступен GraphiQL).

### 2. Admin Dashboard

```bash
cd "Admin Dashboard"
npm install
cp .env.example .env        # заполнить VITE_* значения
npm run dev                 # dev-сервер Vite
# или: npm run build && npm run preview
```

### 3. CustomerApp

```bash
cd CustomerApp
npm install
npm start                   # expo start
# npm run android  /  npm run ios
```

Отсканировать QR-код в Expo Go или нажать `a`/`i` для Android/iOS симулятора.

### 4. Website (маркетинговый сайт)

```bash
cd Website
npm install
cp .env.example .env        # VITE_CUSTOMER_APP_URL, VITE_ADMIN_URL
npm run dev                 # dev-сервер
npm run build               # статический билд в dist/
```

## Конфигурация и переменные окружения

Секреты не хранятся в репозитории. Каждый модуль поставляет `.env.example`:

- `backend/.env.example` — MongoDB URI, JWT secret, SMTP, Stripe/PayPal, Firebase, OAuth.
- `Admin Dashboard/.env.example` — `VITE_SERVER_URL`, `VITE_WS_SERVER_URL`, Firebase.
- `CustomerApp/.env.example` — `GRAPHQL_URL`, `WS_GRAPHQL_URL`, Stripe, Google OAuth, Amplitude.
- `Website/.env.example` — `VITE_CUSTOMER_APP_URL`, `VITE_ADMIN_URL`.

По умолчанию фронтенды указывают на локальный бэкенд
(`http://localhost:8000/graphql`).

## GraphQL-контракт (важно)

- Операции — это template-literal строки во `src/apollo/` (Admin —
  `src/apollo/server.js`, Customer — `src/apollo/*.js`).
- **Контракт фиксируется фронтендами**: бэкенд реализует имена операций/полей
  **1:1**, без переименований. Поля в **snake_case** (`order_amount`,
  `payment_status`), идентификаторы `_id`.
- Аутентификация: JWT через заголовок `Authorization: Bearer <token>`.
- Подписки используют legacy-протокол `subscriptions-transport-ws`
  (`apollo-link-ws`). Это критичная точка совместимости.
- Контракт задокументирован в OpenSpec-спеках (`openspec/specs/backend/*`).

## Локализация

- **CustomerApp** использует `i18n-js`, 6 языков: `en`, `ar`, `de`, `fr`, `km`,
  `zh`, строки в `CustomerApp/translations/*.js`.
- **Admin Dashboard** использует `i18next`.
- **Website** использует `i18next` с locale-JSON — 7 языков (`en`, `ar`, `de`,
  `fr`, `km`, `ru`, `zh`; `ar` — RTL).

Каждая пользовательская строка должна быть добавлена во **все** языковые файлы
соответствующего модуля.

## Безопасность

- **Никогда не коммитить секреты и API-ключи.** Использовать `.env` /
  `.env.example`. `.env`, `google-services*.json`, `google-service-account.json`
  держать в `.gitignore`.
- Хук `secret-guard.cjs` блокирует запись известных паттернов секретов.
- Хук `git-guard.cjs` блокирует force-push в main/master и деструктивные
  `reset --hard`/`clean`.
- Параметризованные запросы / ORM (никакой конкатенации SQL-строк); RBAC;
  least privilege; SAST/SCA/secret-scan в CI (см. правила в `.cursor/rules/`).

## Процесс разработки и методология

В проекте используется методология **superpowers** + **OpenSpec** (spec-driven).

### OpenSpec

Изменения описываются в `openspec/changes/<имя>/` (proposal, design, tasks,
delta-specs), после завершения переносятся в `openspec/specs/` и архивируются.
Готовые команды-обёртки в `.cursor/commands/`:

- `/opsx-propose` — предложить изменение (генерирует proposal/design/spec/tasks).
- `/opsx-apply` — реализовать задачи изменения.
- `/opsx-archive` — заархивировать завершённое изменение.
- `/opsx-sync` — синхронизировать delta-specs в основные спеки.
- `/opsx-update` — обновить артефакты изменения.

### Навыки (skills)

- **obra/superpowers** (14 навыков) — методология разработки: brainstorming,
  writing-plans, executing-plans, TDD, systematic-debugging,
  verification-before-completion, subagent-driven-development,
  dispatching-parallel-agents, requesting/receiving-code-review и др.
- **expo/skills** (9 навыков) — Expo-специфичные.
- Проектные навыки в `.cursor/skills/`: `graphql-contract`, `forkly-i18n`,
  `run-the-project`.

### Команды и роли

| Роль | Инструмент |
| ---- | ---------- |
| Оркестратор end-to-end | `/ship <task>` — propose → implement (свежий subagent на задачу + review + fix-loop) → verify → UI-check → review (bugbot + security-review) → merge/PR |
| Проверка перед merge | `/review` — запускает `bugbot` + `security-review` |
| Проверка UI в рантайме | `/ui-verify` — Playwright (web) + Maestro (native) |
| Policy enforcer | хуки `secret-guard.cjs` / `git-guard.cjs` (автоматически) |
| Контракт | OpenSpec спеки + `/opsx-*` |
| Доказательства | `verification-before-completion` |

### MCP-серверы (`.cursor/mcp.json`)

| Сервер | Источник | Auth |
| ------ | -------- | ---- |
| context7 | `@upstash/context7-mcp` | нет |
| playwright | `@playwright/mcp` | нет |
| expo | `https://mcp.expo.dev/mcp` | OAuth (Expo-аккаунт) |
| firebase | `firebase-tools mcp` | `firebase login` |
| mongodb | `mongodb-mcp-server` | `MDB_MCP_CONNECTION_STRING` |

Проверка настройки: `node scripts/setup-mcp.mjs`.

## Текущее состояние и план работ

По состоянию на сентябрь 2026:

1. ✅ **Бэкенд написан** — `backend/` реализован и покрывает GraphQL-контракт
   фронтендов (заказы, каталог, платежи, уведомления, подписки).
2. ✅ **CustomerApp модернизирован** — Expo SDK 57, React 19, Apollo Client 3
   (изменение `modernize-customer-app` заархивировано).
3. ✅ **Доставка удалена** — `RiderApp/` и вся rider/delivery-логика убраны.
4. 🔄 **Финальный предрелизный прогон** — `final-preprod-sweep`: полная
   верификация бэкенда, Admin-маршрутов (Playwright) и клиентского пути
   (Maestro).
5. ✅ **Маркетинговый сайт** — `add-marketing-site`: модуль `Website/`
   (Vite + React 18, 7 языков, RTL).
6. ⏭️ **Дальше по плану** — cleanup секретов/мёртвого кода, финализация
   документации (см. `README.md`).

## Стиль кода

- **Plain JavaScript (ES modules), без TypeScript.**
- **StandardJS**: без точек с запятой, одинарные кавычки, 2 пробела,
  `space-before-function-paren: never`, `react/prop-types: 0`.
- Экраны — в `src/screens/<Screen>/`; переиспользуемый UI — в
  `src/components/<Group>/<Component>/`; стили — co-located (`styles.js` в RN,
  SCSS/CSS в Admin/Website).

## Примечание о синхронизации документации

Документация проекта (`README.md`, `README_RU.md`, `AGENTS.md`, правила в
`.cursor/rules/` и навык `run-the-project`) приведена в соответствие с
**актуальным** состоянием кода. При расхождении доверяйте коду.

## Лицензия

MIT.
