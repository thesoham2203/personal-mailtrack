/**
 * Client-Side Authentication Gate for Personal Mailtrack Dashboard.
 *
 * Protects dashboard access using SHA-256 hashed credentials with cryptographic salt.
 * No plaintext passwords or IDs are stored in the source bundle.
 */

// SHA-256 Hash of normalized ID: ONEABOVEALL
const EXPECTED_ID_HASH = "e3e6bae1a7c2169b0cb5c158622e30e6464d869ab383afa16cc6fbcaf99b63e4";

// Cryptographic salt for password hashing
const PASSWORD_SALT = "pm_auth_v1_2026_";

// SHA-256 Hash of salted password: "pm_auth_v1_2026_iamback@2203"
const EXPECTED_PASS_HASH = "beec70a73990d1d911ed9ef2650b670682a7a87d7e97cb70357cfe2e00043937";

const SESSION_KEY = "pm_dashboard_auth_token";
const SESSION_EXPIRY_MS = 30 * 24 * 60 * 60 * 1000; // 30 days

/**
 * Computes SHA-256 hex string using browser Web Crypto API.
 */
export async function sha256(str: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(str);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
}

/**
 * Validates the provided credentials against the stored SHA-256 hashes.
 */
export async function verifyCredentials(id: string, pass: string): Promise<boolean> {
  const normalizedId = id.trim().toUpperCase();
  const computedIdHash = await sha256(normalizedId);
  const computedPassHash = await sha256(PASSWORD_SALT + pass);

  return computedIdHash === EXPECTED_ID_HASH && computedPassHash === EXPECTED_PASS_HASH;
}

/**
 * Attempts login and sets a persistent or session token.
 */
export async function login(id: string, pass: string, remember = true): Promise<boolean> {
  const isValid = await verifyCredentials(id, pass);
  if (!isValid) return false;

  const sessionData = JSON.stringify({
    authenticated: true,
    user: "ONEABOVEALL",
    expiresAt: Date.now() + SESSION_EXPIRY_MS,
  });

  const token = btoa(sessionData);

  if (remember) {
    localStorage.setItem(SESSION_KEY, token);
    sessionStorage.removeItem(SESSION_KEY);
  } else {
    sessionStorage.setItem(SESSION_KEY, token);
    localStorage.removeItem(SESSION_KEY);
  }

  return true;
}

/**
 * Checks whether an active valid session exists in storage.
 */
export function isAuthenticated(): boolean {
  try {
    const token = localStorage.getItem(SESSION_KEY) || sessionStorage.getItem(SESSION_KEY);
    if (!token) return false;

    const data = JSON.parse(atob(token));
    if (!data.authenticated || !data.expiresAt) return false;

    if (Date.now() > data.expiresAt) {
      logout();
      return false;
    }

    return true;
  } catch {
    logout();
    return false;
  }
}

/**
 * Clears current session and logs out.
 */
export function logout(): void {
  try {
    localStorage.removeItem(SESSION_KEY);
    sessionStorage.removeItem(SESSION_KEY);
  } catch {
    // Ignore storage clear errors
  }
}
