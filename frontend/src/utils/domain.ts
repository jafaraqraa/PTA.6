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

  // Localhost case (e.g., najah.localhost)
  if (parts.length >= 2 && parts[parts.length - 1] === 'localhost') {
    return parts[0];
  }

  // Standard domain case (e.g., najah.pta-sim.com)
  if (parts.length >= 3) {
    return parts[0];
  }

  return null;
}
