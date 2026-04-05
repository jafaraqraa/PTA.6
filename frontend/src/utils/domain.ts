/**
 * Detects the university domain from the hostname or query parameters.
 *
 * Logic:
 * 1. Check for 'domain' query parameter (highest priority for local testing).
 * 2. Check the subdomain (e.g., 'najah.localhost:3000' -> 'najah').
 * 3. Fallback to null.
 */
export function detectDomain(): string | null {
  const params = new URLSearchParams(window.location.search);
  const domainParam = params.get('domain');
  if (domainParam) return domainParam;

  const host = window.location.hostname;
  const parts = host.split('.');

  // Localhost case (e.g., najah.localhost, localhost)
  if (parts.includes('localhost')) {
    const idx = parts.indexOf('localhost');
    if (idx > 0) return parts[idx - 1];
    return null;
  }

  // IP addresses or local hostnames (e.g., 127.0.0.1, dev-machine)
  const isIP = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/.test(host);
  if (isIP || parts.length === 1) {
    return null;
  }

  // Standard domain case (e.g., najah.pta-sim.com)
  if (parts.length >= 3) {
    return parts[0];
  }

  return null;
}

/**
 * Extracts the university name/domain from an email address.
 * e.g., admin@najah.com -> najah
 */
export function extractDomainFromEmail(email: string): string | null {
  const parts = email.split('@');
  if (parts.length !== 2) return null;

  const domainParts = parts[1].split('.');
  if (domainParts.length < 2) return null;

  // Return the first part of the domain (e.g., 'najah' from 'najah.com')
  return domainParts[0];
}
