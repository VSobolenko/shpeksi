# ПРОМТ ДЛЯ АГЕНТА — подготовка проекта к работе + написание бэкенда

> Этот документ — полное техническое задание для агента (AI или человека), который должен
> привести проект `food-delivery-singlevendor` в рабочее состояние:
> 1) написать бэкенд с нуля на Python,
> 2) удалить всё, что связано с доставкой (включая приложение курьера целиком),
> 3) почистить мусор,
> 4) обновить/исправить всё устаревшее.
>
> Проект должен превратиться из «фуд-доставки с курьером» в «сервис заказа еды с самовывозом»:
> **клиент заказывает → магазин видит заказ → магазин готовит → клиент забирает.**
> Никакого курьера и доставки не остаётся.

---

## 0. РОЛЬ АГЕНТА И ГЛОБАЛЬНАЯ ЦЕЛЬ

Ты — senior full-stack инженер. Тебе доверен репозиторий, который нужно привести в порядок и
дополнить недостающей серверной частью. Действуй аккуратно, но решительно: проект сейчас в
полурабочем состоянии, часть кода устарела, часть мусорная, а бэкенда нет вообще.

Глобальный результат:
- Рабочий бэкенд на Python, совместимый с уже существующим GraphQL-контрактом фронтенда.
- Два живых фронта: **CustomerApp** (клиент) и **Admin Dashboard** (магазин). **RiderApp удалён.**
- Сквозной сценарий: клиент оформил заказ → магазин увидел в админке → подтвердил/приготовил → клиент забрал.
- Никаких следов доставки, курьеров, гео-трекинга курьера, платы за доставку.
- Чистый, современный стек без легаси-зависимостей.

---

## 1. КОНТЕКСТ ПРОЕКТА (что уже известно, перепроверять не нужно)

Репозиторий — open-source проект **Enatega Single Vendor** (white-label решение для ресторана).
Структура на момент начала работы:

```
food-delivery-singlevendor/
├── Admin Dashboard/   # веб-панель магазина (React + reactstrap + Apollo GraphQL)
├── CustomerApp/       # мобильное приложение клиента (React Native + Expo 47, RN 0.70.5)
├── RiderApp/          # мобильное приложение курьера (ПОДЛЕЖИТ ПОЛНОМУ УДАЛЕНИЮ)
├── assets/            # картинки/скриншоты для README
├── contributingGuides/# гайды для контрибьюторов
├── SECURITY.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md, LICENSE, README.md
└── AGENT_PROMPT.md    # этот файл
```

Ключевые факты (уже установлены, доверяй им):
- **Бэкенда в репозитории нет.** Фронтенд сейчас подключён к чужому демо-серверу
  `https://enatega-singlevendor.up.railway.app/graphql` (см. `CustomerApp/environment.js`,
  `RiderApp/environment.js`, `Admin Dashboard/.env.*`). Его нужно заменить на собственный.
- Все три приложения общаются с сервером **по GraphQL** (HTTP + WebSocket для подписок).
- Авторизация — **JWT**, заголовок `Authorization: Bearer <token>`.
- Оплата — **COD (наличные), STRIPE, PAYPAL**.
- База данных — **MongoDB** (в README прямо указан Mongo; фронт завязан на `_id` и вложенные документы).
- Push-уведомления — **Firebase**.
- Email — через SMTP (Gmail).
- Картинки — **Cloudinary**.

---

## 2. ИТОГОВАЯ ЦЕЛЕВАЯ АРХИТЕКТУРА

```
┌──────────────┐         GraphQL (HTTP + WS)         ┌─────────────────────┐
│ CustomerApp  │ ◄─────────────────────────────────► │  ТВОЙ БЭКЕНД        │
│  (клиент)    │                                     │  Python (FastAPI +  │
└──────────────┘                                     │  Strawberry GraphQL)│
                                                     │  + MongoDB + Redis  │
┌──────────────┐         GraphQL (HTTP + WS)         │  + Stripe/PayPal    │
│ Admin        │ ◄─────────────────────────────────► │  + Firebase + SMTP  │
│ Dashboard    │                                     └─────────────────────┘
└──────────────┘
```

Целевой бизнес-флоу (без доставки):
1. Клиент выбирает еду в `CustomerApp`, применяет купон, выбирает оплату.
2. Клиент оформляет заказ → заказ уходит на бэкенд и сохраняется.
3. Магазин мгновенно видит новый заказ в `Admin Dashboard` (раздел Orders, через подписку).
4. Магазин меняет статус: `PENDING` → `ACCEPTED` (принят) → `READY` (готов к выдаче) → `COMPLETED` (забран).
5. Клиент видит смену статуса в реальном времени и забирает еду сам.

---

## 3. СТЕК БЭКЕНДА (Python — зафиксирован, не менять без необходимости)

Команда — питонисты, поэтому бэкенд пишется на Python. Рекомендованный и **обязательный к использованию** стек:

| Слой | Технология | Обоснование |
|---|---|---|
| Веб-каркас | **FastAPI** (ASGI) + **Uvicorn[standard]** | async, WebSocket из коробки |
| GraphQL | **Strawberry GraphQL** | code-first, типизация, async, подписки |
| БД | **MongoDB** + **Beanie** (async ODM на Motor + Pydantic) | фронт завязан на Mongo и вложенные документы |
| Pub/Sub для подписок | **Redis** (для прод) / in-memory PubSub (для MVP) | рассылка realtime-событий |
| Auth | **python-jose** (JWT) + **passlib[bcrypt]** | хэш паролей, токены |
| Платежи | **stripe** (Python SDK) + **paypalrestsdk** | оплата картой и PayPal |
| Push | **firebase-admin** | FCM-уведомления |
| Email | **aiosmtplib** | отправка писем |
| Валидация/модели | **Pydantic v2** | типы, схемы |

Требования к структуре бэкенда (создать отдельную папку, НЕ внутри существующих модулей фронта):

```
backend/
├── pyproject.toml / requirements.txt
├── .env.example
├── README.md
├── app/
│   ├── main.py                 # FastAPI app, подключение GraphQL, CORS, /stripe
│   ├── config.py               # настройки из env (pydantic-settings)
│   ├── db.py                   # подключение Beanie/Motor
│   ├── models/                 # Beanie-документы (см. п.4.1)
│   ├── graphql/
│   │   ├── schema.py           # Strawberry Query/Mutation/Subscription
│   │   ├── types/              # GraphQL-типы (DTO)
│   │   ├── resolvers/          # резолверы query/mutation/subscription
│   │   ├── context.py          # контекст запроса (auth, db, pubsub)
│   │   └── pubsub.py           # PubSub-каналы и события
│   ├── services/               # бизнес-логика (orders, payments, notifications, email)
│   └── integrations/           # stripe, paypal, firebase, cloudinary, smtp
└── tests/
```

GraphQL-эндпоинт должен быть доступен по пути **`/graphql`** (HTTP и WebSocket), потому что фронт
хардкодит именно этот путь (`SERVER_URL` + `graphql`, `WS_SERVER_URL` + `graphql`).

---

## 4. ЗАДАЧА 1 — НАПИСАТЬ БЭКЕНД (полная спецификация)

Вся спецификация ниже восстановлена из GraphQL-запросов фронтенда (файлы `*/apollo/server.js`).
Контракт фиксирован — НЕ выдумывай новые имена операций/полей, используй ровно те, что ждёт фронт.

### 4.1 Модели данных (коллекции MongoDB)

| Коллекция | Поля |
|---|---|
| **Category** | `_id`, `title`, `description`, `img_menu` |
| **Food** | `_id`, `title`, `description`, `img_url`, `stock`, `tag`, `variations[]` (влож.), `category` (ref → Category) |
| **Variation** (влож. в Food) | `_id`, `title`, `price`, `discounted`, `addons[]` (ref → Addon) |
| **Addon** | `_id`, `title`, `description`, `quantity_minimum`, `quantity_maximum`, `options[]` (ref → Option), `is_active` |
| **Option** | `_id`, `title`, `description`, `price` |
| **Coupon** | `_id`, `code`, `discount`, `enabled` |
| **User** (клиент) | `_id`, `name`, `email`, `phone`, `password` (hash), `is_active`, `notificationToken`, `is_order_notification`, `is_offer_notification`, `addresses[]` (влож.), `facebookId`, `appleId` |
| **Address** (влож. в User) | `_id`, `label`, `delivery_address`, `details`, `latitude`, `longitude`, `selected` |
| **Order** | `_id`, `order_id` (человекочитаемый номер), `user` (ref), `items[]` (влож.), `order_amount`, `paid_amount`, `payment_method`, `payment_status`, `order_status`, `status_queue`, `reason`, `review` (влож.), `createdAt`, `updatedAt` |
| **OrderItem** (влож. в Order) | `_id`, `food` (ref), `variation` (ref/влож.), `addons[]` (влож.), `quantity` |
| **Review** (влож. в Order / отдельно) | `_id`, `rating`, `description`, `order` (ref), `is_active`, `createdAt`, `updatedAt` |
| **Configuration** | **СИНГЛТОН** (один документ): `_id`, `order_id_prefix`, `email`, `password`, `enable_email`, `client_id`, `client_secret`, `sandbox`, `publishable_key`, `secret_key`, `delivery_charges`, `currency`, `currency_symbol` |

> ⚠️ После удаления доставки (см. п.5) поля `delivery_address`, `delivery_charges`, `rider`
> в модели Order и `delivery_charges` в Configuration **удаляются или перестают использоваться**.
> Ориентируйся на п.5 как на финальное состояние модели.

### 4.2 Полный список GraphQL-операций (восстановить 1-в-1)

#### Админка (Admin Dashboard)
**Query:** `foods`, `categories`, `allCategories(page)`, `allOrders(page,rows,search)`, `users(page)`,
`allReviews(offset)`, `riders`, `availableRiders`, `orderCount`, `options`, `allOptions(page)`,
`addons`, `allAddons(page)`, `coupons`, `configuration`, `getDashboardTotal(starting_date,ending_date)`,
`getDashboardSales(...)`, `getDashboardOrders(...)`, `getDashboardData(...)`,
`getOrderStatuses`, `getPaymentStatuses`.

**Mutation:** `createFood`, `editFood`, `deleteFood`, `createCategory`, `editCategory`, `deleteCategory`,
`createOptions`, `editOption`, `deleteOption`, `createAddons`, `editAddon`, `deleteAddon`,
`createCoupon`, `editCoupon`, `deleteCoupon`, `createRider`, `editRider`, `deleteRider`,
`toggleAvailablity`, `assignRider`, `updateOrderStatus`, `updatePaymentStatus`, `updateStatus`,
`adminLogin`, `resetPassword`, `sendNotificationUser`, `uploadToken`,
`saveOrderConfiguration`, `saveEmailConfiguration`, `savePaypalConfiguration`,
`saveStripeConfiguration`, `saveDeliveryConfiguration`, `saveCurrencyConfiguration`.

**Subscription:** `subscribePlaceOrder`.

#### Клиент (CustomerApp)
**Query:** `categories`, `foodByCategory`, `foodByIds(ids)`, `profile`, `order(id)`, `orders(offset)`,
`rider(id)`, `configuration`.

**Mutation:** `login`, `createUser`, `updateUser`, `updateNotificationStatus`, `pushToken`,
`placeOrder`, `reviewOrder`, `coupon(coupon)`, `createAddress`, `editAddress`, `deleteAddress`,
`selectAddress`, `changePassword`, `forgotPassword`.

**Subscription:** `orderStatusChanged(userId)`, `subscriptionRiderLocation(riderId)`.

#### Курьер (RiderApp) — НЕ РЕАЛИЗОВЫВАТЬ
RiderApp удаляется (п.5). Все его операции (`riderLogin`, `updateOrderStatusRider`, `assignOrder`,
`updateRiderLocation`, `assignedOrders`, `unassignedOrders`, `subscriptionAssignRider`, `unassignedOrder`)
**исключить из схемы**, если только их поля не нужны клиенту/магазину.

### 4.3 Realtime-подписки (WebSocket)

Оставить только те, что нужны после удаления доставки:

| Подписка | Потребитель | Событие |
|---|---|---|
| `subscribePlaceOrder` | админка | новый заказ появился |
| `orderStatusChanged(userId)` | клиент | смена статуса заказа |

Удалить вместе с доставкой: `subscriptionRiderLocation`, `subscriptionAssignRider`, `unassignedOrder`.

### 4.4 Статусы (enum, фиксированы фронтом)

- `order_status`: `PENDING → ACCEPTED → READY → COMPLETED` (+ `CANCELLED`).
  ВАЖНО: в текущем фронте есть `PICKED` и `DELIVERED` — они курьерские. После удаления доставки
  статусы пересматриваются на «магазин-клиент» (см. п.5). Согласуй финальный набор с правками фронта.
- `payment_status`: `PENDING`, `PAID`.
- `payment_method`: `COD`, `STRIPE`, `PAYPAL`.
- Поле `status_queue` в заказе — объект с временными метками прохождения этапов
  (в оригинале: `pending, preparing, picked, delivered, cancelled`). Приведи к новому набору этапов.

### 4.5 REST-эндпоинты (только для Stripe, вне GraphQL)

Фронт (`CustomerApp/src/screens/Stripe/StripeCheckout.js`) ждёт от сервера:
- `POST /stripe/charge?id=<order_id>` — принять Stripe-токен, списать средства.
- `GET /stripe/cancel` — возвращает HTML с `<title>cancel</title>`.
- Редирект на `success` / `failed` (HTML с соответствующим `<title>`).

PayPal — client-side, бэкенду достаточно хранить/отдавать `client_id`, `client_secret`, `sandbox`.

### 4.6 Внешние интеграции (обязательные)

1. **Stripe** — `secret_key`/`publishable_key` из Configuration; списание карты.
2. **PayPal** — `client_id`/`client_secret`/`sandbox` из Configuration.
3. **Firebase (FCM)** — push-уведомления: сохранять `notificationToken`/`push_token` устройств;
   реализовать `sendNotificationUser` и уведомления при смене статуса заказа.
4. **Email (SMTP/Gmail)** — `email`+`password` из Configuration; письма подтверждения заказа и сброса пароля (`forgotPassword`/`resetPassword`).
5. **Cloudinary** — загрузка изображений (`img_url`, `img_menu`); в админке есть `cloudinary_upload_url`/`cloudinary_category`/`cloudinary_food`.

### 4.7 Авторизация и роли

- Три точки входа (до удаления доставки — две): `adminLogin` (магазин), `login`/`createUser` (клиент).
- Роль определяет доступ: админ не может вызвать клиентские `placeOrder` и наоборот. Реализуй middleware/guard по роли из JWT.
- `login` клиента принимает `type` (обычный/Facebook/Apple) → нужна проверка OAuth-токенов соцсетей.
- Пароли — bcrypt. Токены — JWT с `exp`.

### 4.8 ⚠️ КРИТИЧЕСКИ ВАЖНО: совместимость WebSocket-протокола

Фронт использует **старый** протокол подписок `subscriptions-transport-ws` (Apollo Client v2,
`apollo-link-ws`), тогда как современные Python-библиотеки (Strawberry/Ariadne) по умолчанию говорят
на **новом** `graphql-transport-ws`. Эти протоколы несовместимы из коробки.

Обязательные действия (выбери рабочий вариант и зафиксируй):
1. Поддержать оба протокола на одном WebSocket-эндпоинте (dual-protocol), ЛИБО
2. Реализовать старый `subscriptions-transport-ws` (GQL_CONNECTION_INIT / GQL_START / GQL_STOP), ЛИБО
3. Мигрировать фронт на `@apollo/client` (это уже правка фронта, см. п.7).

Первый же прототип должен проверить, что подписка реально доходит до фронта. Это самая рискованная часть — закрой её в первую очередь.

---

## 5. ЗАДАЧА 2 — УДАЛИТЬ ДОСТАВКУ И СОЕДИНИТЬ КЛИЕНТА С МАГАЗИНОМ НАПРЯМУЮ

Цель: превратить продукт в **заказ с самовывозом**. Курьер как сущность исчезает полностью.

### 5.1 Удалить целиком

- Папку **`RiderApp/`** (весь модуль: код, `package.json`, `google-services.json`, `google-service-account.json`, `patches/`).
- Упоминания RiderApp в README, скриншоты, ссылки на rider-app в сторах.
- Ветку/упоминания `adnan-rider-app-singlevendor` (если влияют на рабочие файлы).

### 5.2 Убрать из `CustomerApp`

- Компонент `src/components/OrderDetail/TrackingRider/` (трекинг курьера на карте).
- Query `rider(id)` и subscription `subscriptionRiderLocation` (файл `src/apollo/server.js`).
- Всё, что показывает статус `PICKED`/`DELIVERED` и «курьер в пути»:
  - `src/screens/OrderDetail/OrderDetail.js` (блоки с `order.rider`, `PICKED`, `DELIVERED`, `COMPLETED`).
  - `src/components/Menu/StatusCard/StatusCard.js` и `src/screens/MyOrders/MyOrders.js` (массивы статусов).
- Плату за доставку (`delivery_charges`, `deliveryFee`) в `src/screens/Cart/Cart.js` и `src/context/Configuration.js`.
- Поле `delivery_address`/`deliveryAddress` в корзине — заменить на логику самовывоза (клиенту не нужен адрес; оставить только контактные данные — телефон/имя).
- Статусы `PICKED`/`DELIVERED` → новый набор: `PENDING`, `ACCEPTED`, `READY`, `COMPLETED` (+ `CANCELLED`).
- Строки локализации про доставку/курьера в `translations/*.js` (en, ar, de, fr, km, zh).
- Экраны `Chat` (чат с курьером) и связанные зависимости, если они завязаны только на курьера.

### 5.3 Убрать из `Admin Dashboard`

- `src/views/Riders.jsx` и `src/components/Rider/` (управление курьерами) — удалить.
- Пункт меню «Riders» в `src/routes.js` и сайдбаре.
- Блок «Assign Rider» / назначение курьера в `src/components/Order/Order.jsx` и `OrderData.jsx`.
- `src/components/Configuration/Delivery/` (настройка цены доставки) и его подключение в `Configuration.jsx`.
- Отображение `delivery_address`, `delivery_charges`, `rider` в карточке/детали заказа.
- Соответствующие операции из `src/apollo/server.js`: `riders`, `availableRiders`, `createRider`,
  `editRider`, `deleteRider`, `toggleAvailablity`, `assignRider`, `saveDeliveryConfiguration`.

### 5.4 Соответствующие правки на бэкенде

- Убрать модель `Rider`, операции курьера и подписки курьера.
- Убрать `delivery_charges`, `delivery_address`, `rider` из Order.
- Обновить `placeOrder`: принимать только товары + контакт + оплату (без адреса и без расчёта доставки).
- Обновить `status_queue` и enum статусов на самовывоз.

> Если останется неоднозначность по UX самовывоза (нужно ли время готовности, уведомление «заказ готов»
> и т.п.) — принимай минимально жизнеспособное решение и **явно опиши его в итоговом отчёте**.

---

## 6. ЗАДАЧА 3 — ПОЧИСТИТЬ МУСОР

Удалить/исправить всё, что не относится к работе продукта:

1. **Secrets/ключи Enatega** (чужие, подлежат замене/удалению):
   - `CustomerApp/google-services*.json`, `RiderApp/google-services.json`,
     `RiderApp/google-service-account.json`.
   - Закоммиченные ключи в `Admin Dashboard/src/index.js` (Firebase `apiKey` и т.д.) → вынести в `.env`.
   - Хардкод ключей Stripe/Google/Amplitude в `CustomerApp/environment.js` → вынести в env/конфиг.
   - Демо-URL `enatega-singlevendor.up.railway.app` → заменить на локальный/свой бэкенд.
2. **Файлы кэша/локальных настроек**: `.expo/`, `reset-cache/`, `node_modules/` (не коммитить), `.DS_Store`.
3. **Мёртвый код**: закомментированные блоки (например, в `Cart.js`, `index.js` админки),
   неиспользуемые импорты, `console.log` для отладки (например, `console.log(observer)` в `Admin Dashboard/src/index.js`).
4. **Ненужные зависимости** (после удаления доставки и трекинга):
   - `react-native-maps`, `react-native-maps-directions`, `react-native-gifted-chat`,
     `react-native-timeline-flatlist` — если остались без использования.
5. **Странный пакет**: `"npm": "^6.14.9"` в dependencies админки — убрать (это ошибка).
6. **Дубли/непоследовательность i18n**: в CustomerApp `i18n-js`, в RiderApp `i18next` — привести к одному решению (после удаления RiderApp остаётся `i18n-js`; оцени, стоит ли перевести на `i18next` или оставить).
7. **Лишние README-активы**: удалить неиспользуемые изображения из `assets/` (если не нужны в README).

---

## 7. ЗАДАЧА 4 — ОБНОВИТЬ ВСЁ УСТАРЕВШЕЕ

### 7.1 `Admin Dashboard` (самое легаси)

`Admin Dashboard/package.json` сейчас на:
- `react 16.8.4` / `react-dom 16.8.4` → **React 18**.
- `react-scripts 2.1.8` → **CRA 5** или миграция на **Vite** (предпочтительно Vite).
- `node-sass 4.12` → **sass (dart-sass)**; убрать скрипты `compile-sass/minify-sass/map-sass`.
- `react-router-dom 4.3.1` → **v6** (поправить `<Switch>` → `<Routes>`, `component` → `element`).
- `chart.js 2.7.3` + `react-chartjs-2 2.7.4` → **v4**.
- `firebase 7.14` → **firebase 9+/10** (modular API).
- `moment 2.24` → **dayjs** (или оставить, но актуализировать).
- Apollo: `apollo-boost 0.3` + `react-apollo 2.5` + `apollo-client 2.x` → **`@apollo/client` 3.x**.
- `material-ui 4` → оставить или **MUI 5** (оцени трудоёмкость; можно оставить v4, если не мешает).
- `reactstrap 7`, `react-data-table-component 6`, `react-datetime`, `nouislider`, `react-bootstrap-typeahead` — аудит: обновить или удалить неиспользуемые.
- Подписки `subscriptions-transport-ws` → пересмотреть в связке с п.4.8.

### 7.2 `CustomerApp`

- `Expo 47` / `RN 0.70.5` → **Expo SDK 50+** (обновить по официальной инструкции `expo install --fix` / `npx expo install expo@latest`).
- Apollo: смесь `apollo-client 2.5` + `apollo-boost` + `react-apollo 3` + `@apollo/react-hooks` → **`@apollo/client` 3.x** (единый пакет).
- `subscriptions-transport-ws 0.11` → согласовать с выбранным вариантом из п.4.8.
- Убрать `deprecated-react-native-prop-types` если после апдейта не нужен.
- `react-native-material-textfield` (запатчен) — заменить нативный инпут или актуальную альтернативу.
- Обновить `README` (требование Node 14–16 устарело) → **Node 18/20 LTS** и новый порядок запуска.

### 7.3 README и общее

- Переписать README под новый продукт: без доставки/курьера, с описанием бэкенда и инструкцией запуска (backend + CustomerApp + Admin Dashboard).
- Убрать/обновить секции «Demos», скриншоты Rider App, ссылки на rider-приложения.
- Указать актуальные версии Node и команды запуска.
- Добавить `.env.example` для бэкенда и для админки.

---

## 8. ПОРЯДОК РАБОТ (рекомендуемые фазы)

1. **Фаза 0 — инвентаризация.** Убедись, что знаешь текущее состояние; зафиксируй, что фронт не запущен и бэка нет.
2. **Фаза 1 — бэкенд (каркас + контракт).** Поднять FastAPI + Strawberry, MongoDB, JWT. Реализовать Query/Mutation для сущностей меню (Category, Food, Addon, Option, Coupon, Configuration) и auth. Сразу закрыть вопрос совместимости WebSocket-протокола (п.4.8) прототипом.
3. **Фаза 2 — бэкенд (заказы и realtime).** `placeOrder`, `orders`, `order`, статусы, `subscribePlaceOrder`, `orderStatusChanged`, платежи (COD/Stripe/PayPal), email, push.
4. **Фаза 3 — удаление доставки.** Удалить RiderApp; вычистить доставку из CustomerApp и Admin Dashboard; привести статусы к самовывозу; поправить схемы бэкенда.
5. **Фаза 4 — чистка.** Мусор, секреты, мёртвый код, лишние зависимости.
6. **Фаза 5 — обновление легаси.** React 18 + Vite/CRA5, Apollo Client 3, Expo SDK, README.
7. **Фаза 6 — сквозная проверка.** Полный сценарий: клиент заказал → магазин увидел → статусы → забрал. Плюс lint/build всех модулей.

---

## 9. КРИТЕРИИ ГОТОВНОСТИ (Definition of Done)

- [ ] `backend/` запускается одной командой, читает конфиг из `.env`, поднимает GraphQL на `/graphql` (HTTP + WS).
- [ ] Все операции из п.4.2 реализованы и отдают поля ровно в том виде, что ждёт фронт (сравнить с `*/apollo/server.js`).
- [ ] Подписки `subscribePlaceOrder` и `orderStatusChanged` работают с реальным фронтом (проверено на устройстве/эмуляторе).
- [ ] Сквозной сценарий «клиент → магазин → самовывоз» работает без ошибок.
- [ ] `RiderApp/` удалён, в коде и README нет упоминаний курьера/доставки/трекинга.
- [ ] В заказе и корзине нет `delivery_charges`, `delivery_address`, `rider`.
- [ ] Нет закоммиченных секретов; все ключи в `.env` / `.env.example`.
- [ ] `Admin Dashboard` собирается на React 18 (Vite или CRA5) без ошибок; `npm run build` проходит.
- [ ] `CustomerApp` запускается на актуальном Expo SDK без ошибок; `npx expo start` проходит.
- [ ] `npm run lint` (или аналог) проходит во всех оставшихся модулях.
- [ ] README актуален: описывает новый продукт, запуск бэкенда и обоих фронтов.
- [ ] В итоговом отчёте перечислены все принятые UX/архитектурные решения и что именно изменено/удалено.

---

## 10. ОГРАНИЧЕНИЯ И ПРЕДУПРЕЖДЕНИЯ

- **Не менять GraphQL-контракт** без явной необходимости. Если меняешь — синхронно правь фронт и отрази в отчёте.
- **Не ломать оплату**: Stripe legacy `checkout.js` устарел, но пока работает; миграцию на Payment Intents делай аккуратно и проверь.
- **Секреты не коммитить**: `.env`, `google-services*.json`, ключи API — в `.gitignore`.
- **Windows-окружение** (PowerShell): команды и скрипты должны быть кросс-платформенными или с явным учётом Windows.
- **Монорепо**: бэкенд добавляется как новая папка `backend/` на верхнем уровне, не смешивать с фронтами.
- Если какое-то решение неоднозначно (напр., оставить ли адрес клиента для контакта, нужна ли оплата онлайн) — **зафиксируй выбор в отчёте**, но не блокируй работу.

---

## 11. ЧТО НЕ ТРОГАТЬ (без необходимости)

- Существующую бизнес-логику меню: Category/Food/Addon/Option/Coupon (она рабочая).
- Локализацию как механизм (только вычистить строки про доставку/курьера).
- `LICENSE`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CONTRIBUTING.md` (можно актуализировать только при явной необходимости).
- Git-историю (не переписывать коммиты без явного запроса).

---

## 12. ФОРМА ИТОГОВОГО ОТЧЁТА

По завершении предоставь:
1. Что сделано по каждой задаче (1–4) кратко, списком.
2. Структура созданного `backend/` и как его запустить.
3. Принятые решения и компромиссы (особенно по самовывозу и WS-протоколу).
4. Список удалённых файлов/зависимостей.
5. Что осталось нереализованным/требует внимания и почему.
6. Команды для запуска всех трёх частей (backend, CustomerApp, Admin Dashboard).
