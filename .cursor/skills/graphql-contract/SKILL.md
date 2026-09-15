---
name: graphql-contract
description: Work with the Forkly GraphQL contract — locate, add, and keep operations consistent across the two frontends. Use when adding or editing GraphQL queries, mutations, or subscriptions in this repo.
disable-model-invocation: true
---

# GraphQL contract

## Where operations live

- Admin: `Admin Dashboard/src/apollo/server.js`
- Customer: `CustomerApp/src/apollo/server.js` (client setup in `src/apollo/index.js`)

Operations are exported template-literal strings; the app wraps them with
`gql` at the call site.

## Rules

1. Use the existing field names exactly (`_id`, snake_case like `order_amount`). Do not rename.
2. Subscriptions use the legacy `subscriptions-transport-ws` protocol on the client; the backend supports both that and `graphql-transport-ws`.
3. Auth header is `Authorization: Bearer <token>`.
4. When you add a field/operation to the frontend, the backend must implement it 1:1 (see the `python-fastapi` rule and the OpenSpec specs in `openspec/specs/backend/`).

## Add a new query (example)

1. Add the string to the module's `server.js`:

```js
export const getProfile = `query Profile {
  profile {
    _id
    name
    email
    phone
  }
}`
```

2. At the call site, wrap with `gql` and execute via `useQuery`/`client.query` or `useMutation`.
