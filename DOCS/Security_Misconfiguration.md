# Security Misconfiguration

Security misconfiguration occurs when security settings are defined, implemented, or maintained improperly. This includes weak secret keys, permissive CORS policies, missing security headers, debug mode in production, and insecure session management.

## Prerequisites

- Browser access to functioning web app
- One registered user account
- Access to browser developer tools (Network and Console tabs)

## Configuration

**Runtime Toggle (Recommended for Testing)**

Use the Security Hardening toggle on the dashboard at `http://localhost:5000/dashboard` to switch between vulnerable and hardened modes without restarting the application.


### Weak Secret Keys

Allows attackers to forge session tokens and JWT tokens using easily guessable secrets.

#### Exploit

##### Method 1: JWT Token Forgery via Local Tool

**Setup:**
1. Ensure Security Hardening is **disabled** (vulnerable mode) - this ensures weak secret keys are in use
2. Create two test accounts (e.g., `attacker` and `victim`)

**Obtain Victim's Token Structure:**
1. Login as `victim` at `http://localhost:5000/login`
2. Press F12 → **Storage** tab (Firefox) or **Application** tab (Chrome)
3. Click **Cookies** → `http://localhost:5000`
4. Find the `token` cookie and copy its value (starts with `eyJ...`)
5. Open the JWT Forgery Tool at `http://localhost:5000/tools/forge-jwt` and decode the token to see victim's `user_id`
6. Logout from victim account

**Forge and Use Token:**
1. Login as `attacker` at `http://localhost:5000/login`
2. F12 → **Cookies** → copy the `token` cookie value
3. Open the JWT Forgery Tool at `http://localhost:5000/tools/forge-jwt` in a new tab
4. Paste attacker's token → Click "Decode Token"
5. In Step 2, modify the payload:
   - Change `user_id` to victim's user_id (from earlier)
   - Change `username` to `"victim"`
   - Keep `is_admin` value as-is or modify if testing privilege escalation
   - Do NOT add `exp` field (vulnerable mode tokens don't have expiration)
6. Click "Forge Token with New Payload" (uses weak secret `secret123`)
7. Copy the forged token
8. Back in browser: F12 → **Cookies** → double-click the `token` cookie **Value**
9. Replace with your forged token → Press Enter
10. Refresh the page (F5)

**Expected Result (Vulnerable):** Dashboard now shows victim's account information (name, account number, balance). You successfully impersonated victim by forging a JWT token with the weak secret `secret123`.

**Important:** The server authenticates using the `token` **cookie**, not LocalStorage. You must replace the cookie value to use the forged token.

#### Mitigate

**Using Runtime Toggle**
1. Log out of the application
2. Go to `http://localhost:5000/` and click "Enable Security Hardening" toggle
3. Log in as `attacker` at `http://localhost:5000/login`
4. F12 → **Cookies** → copy the `token` cookie value
5. Open the JWT Forgery Tool at `http://localhost:5000/tools/forge-jwt`
6. Paste attacker's token → Click "Decode Token"
7. In Step 2, modify the payload:
   - Change `user_id` to victim's user_id (same as the exploit)
   - Change `username` to `"victim"`
8. Click "Forge Token with New Payload" (still using `secret123` as the secret)
9. Copy the forged token
10. Back in browser: F12 → **Cookies** → double-click the `token` cookie **Value**
11. Replace with your forged token → Press Enter
12. Refresh the page (F5)

**Expected Result (Protected):** The forged token is rejected, the dashboard does NOT show victim's account information. Instead you will see an error upon refresh, because the forged token lacks an `exp` claim and hardened mode requires one. The same forgery steps that worked in the exploit no longer succeed.

**Note on Token Expiration:** When hardening is enabled, tokens expire after 5 seconds (configured in `mitigations/session_exp.py`) for quick demonstration purposes. If you need tokens to last longer for extended testing, modify `timedelta(seconds=5)` to a longer duration in that file (e.g., `timedelta(hours=1)`).

**Runtime Toggle Limitation:** The runtime toggle protects against forgery by requiring an `exp` claim — a forged token without `exp` is rejected. However, `JWT_SECRET` is fixed at startup (`secret123` by default), so a forged token that includes a valid `exp` and is signed with `secret123` would still be accepted in toggle-hardened mode. For full protection (different secret), set `JWT_SECRET_KEY` to a strong random value in `.env` and restart the application instead of using the toggle.

### Insecure Cookie Configuration

Session cookies lack security flags, exposing them to interception and XSS attacks.

#### Exploit

##### Method 1: Inspecting Cookie Security via DevTools

1. Ensure Security Hardening is **disabled** (vulnerable mode)
2. Log in to your account at http://localhost:5000/login
3. Open browser developer tools (F12)
4. Go to Application tab → Storage → Cookies → `http://localhost:5000`
5. Locate the `token` cookie in the list
6. Examine the cookie properties columns:
   - **Secure**: Should be false or blank
   - **HttpOnly**: Should be false or blank
   - **SameSite**: Shows "None" or blank (vulnerable to CSRF)
7. Note the cookie value (your session token)

**Expected Result (Vulnerable):** Cookie lacks all three critical security flags, making it vulnerable to:
- Interception over unencrypted connections
- Theft via XSS attacks
- CSRF attacks from malicious sites

##### Method 2: Accessing Cookie via JavaScript (Demonstrates HttpOnly Risk)

1. Ensure Security Hardening is **disabled** (vulnerable mode)
2. Remain logged in
3. Open browser console (F12 → Console)
4. Execute:
   ```javascript
   // This should work if HttpOnly is disabled
   console.log('All cookies:', document.cookie);

   // Extract just the token
   const cookies = document.cookie.split('; ');
   const tokenCookie = cookies.find(c => c.startsWith('token='));
   if (tokenCookie) {
       console.log('Session token accessible via JS:', tokenCookie);
       console.log('This token can be stolen by XSS attacks!');
   }
   ```

**Expected Result (Vulnerable):** Console displays the session token. An XSS attack could execute similar code to steal the token

##### Method 3: Demonstrating Missing Secure Flag

1. Ensure Security Hardening is **disabled** (vulnerable mode)
2. Note that the application is running on `http://localhost:5000` (not HTTPS)
3. The session cookie is transmitted in clear text over HTTP
4. Execute in console to see request headers:
   ```javascript
   fetch('/api/security-config', {
       credentials: 'include'
   })
   .then(r => {
       console.log('Cookie sent over HTTP - visible to network sniffers');
       return r.json();
   });
   ```

**Expected Result (Vulnerable):** Cookie transmitted without encryption. Network sniffers (like Wireshark) can capture the session token in plaintext.

#### Mitigate

**Option 1: Using Runtime Toggle (Recommended)**
1. Go to `http://localhost:5000` and enable the "Global Security Hardening" toggle
2. Log back in at `http://localhost:5000/login` to receive a new secure cookie
3. Open DevTools (F12) → Application tab → Storage → Cookies → `http://localhost:5000`
4. Examine the `token` cookie properties (corresponds to Method 1):
   - **Secure**: Still false or blank — expected on HTTP localhost, only set over HTTPS
   - **HttpOnly**: `True` (now set)
   - **SameSite**: `Strict` (now set)
5. Open the Console tab and try accessing the cookie via JavaScript (corresponds to Method 2):
   ```javascript
   const cookie = document.cookie;
   if (cookie && cookie.includes('token=')) {
       console.log('Token stolen:', cookie);
   } else {
       console.log('Access denied, HttpOnly flag prevents JavaScript from reading the token cookie');
   }
   ```

**Option 2: Using Environment Variables**
1. Update `.env` file:
   ```
   SECURITY_HARDENING_ENABLED=true
   ```
2. Restart the application:
   - Docker: `docker-compose down && docker-compose up -d`
   - Local: Stop server (Ctrl+C) and run `python app.py`
3. Log out and log in again (to get a new secure cookie)
4. Follow steps 3-5 from Option 1

**Expected Result (Protected):**
- **DevTools (Method 1):** HttpOnly and SameSite flags are now set. Secure remains false on HTTP localhost but would be set over HTTPS.
- **Console (Method 2):** Prints "Access denied" — the token cookie is no longer accessible via `document.cookie` because HttpOnly is set.
- **Method 3:** Cookie is still sent over HTTP on localhost, but in a production HTTPS deployment the Secure flag would prevent transmission over unencrypted connections.
