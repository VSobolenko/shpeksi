/* eslint-disable camelcase */
export const server_url = import.meta.env.VITE_SERVER_URL
export const ws_server_url = import.meta.env.VITE_WS_SERVER_URL
// Restaurant this deployment serves. The dashboard is a single build per
// restaurant, and the backend needs the tenant on every request: a director's
// token already carries it, but the platform owner (superadmin) has no tenant
// and a staff token may predate it, so the header is the reliable fallback.
export const restaurant_slug = import.meta.env.VITE_RESTAURANT_SLUG
export const cloudinary_upload_url = import.meta.env.VITE_CLOUDINARY_UPLOAD_URL
export const cloudinary_category = import.meta.env.VITE_CLOUDINARY_CATEGORY
export const cloudinary_food = import.meta.env.VITE_CLOUDINARY_FOOD
