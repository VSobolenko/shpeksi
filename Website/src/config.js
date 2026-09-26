// Contact / sales CTAs open the visitor's mail client — never the admin
// panel. Merchants get credentials separately; the public site only sells.

export const CONTACT_EMAIL =
  import.meta.env.VITE_CONTACT_EMAIL || 'v.sobolenko.vs@gmail.com'

/**
 * Build a mailto: URL that opens a prefilled compose window.
 *
 * Encoded by hand rather than with URLSearchParams: that class is defined for
 * form bodies and turns a space into "+", which RFC 6068 does not allow in a
 * mailto query. Gmail tolerates it, Outlook shows the plus signs verbatim.
 * @param {{ subject?: string, body?: string }} [opts]
 */
export function mailtoContact(opts = {}) {
  const fields = []
  if (opts.subject) fields.push(['subject', opts.subject])
  if (opts.body) fields.push(['body', opts.body])
  const query = fields
    .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
    .join('&')
  return query
    ? `mailto:${CONTACT_EMAIL}?${query}`
    : `mailto:${CONTACT_EMAIL}`
}
