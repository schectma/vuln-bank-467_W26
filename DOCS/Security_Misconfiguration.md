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
3. Login as `victim` and note their account details
4. Logout

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

**Expected Result (Protected):** The forged token is rejected, the dashboard does NOT show victim's account information. Instead you will see an error upon refresh, because the token was signed with `secret123` but the server now uses a strong random secret. The same forgery steps that worked in the exploit no longer succeed.

**Note on Token Expiration:** When hardening is enabled, tokens expire after 5 seconds (configured in `mitigations/session_exp.py`) for quick demonstration purposes. If you need tokens to last longer for extended testing, modify `timedelta(seconds=5)` to a longer duration in that file (e.g., `timedelta(hours=1)`).

### Missing Security Headers

Exposes application to clickjacking, MIME-type sniffing, and other attacks.

#### Exploit

1. Ensure Security Hardening is **disabled** (vulnerable mode)
2. Log in to your account at `http://localhost:5000/login`
3. Press F12 to open browser DevTools
4. Click the **Network** tab at the top of the DevTools panel
5. Refresh the page (F5) — a list of network requests will appear
6. Click on the first request in the list (usually named `dashboard`)
7. In the detail panel that opens, look for a **Headers** sub-tab and click it
8. Scroll down to the **Response Headers** section
9. Look for the following headers — they should all be **missing**:
   - `Strict-Transport-Security`
   - `X-Content-Type-Options`
   - `X-Frame-Options`
   - `X-XSS-Protection`

**Expected Result (Vulnerable):** None of the four security headers appear in the Response Headers. The server is not sending any protections against clickjacking, MIME-sniffing, or other browser-level attacks.

#### Mitigate

**Using Runtime Toggle**
1. Log out of the application
2. Go to `http://localhost:5000/` and click "Enable Security Hardening" toggle
3. Log back in at `http://localhost:5000/login`
4. Press F12 to open browser DevTools → click the **Network** tab
5. Refresh the page (F5)
6. Click on the first request in the list (usually named `dashboard`)
7. Click the **Headers** sub-tab → scroll down to **Response Headers**
8. Look for the same four headers, they should now be **present**

**Expected Result (Protected):** Response includes security headers:
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` - Forces HTTPS
- `X-Content-Type-Options: nosniff` - Prevents MIME-type sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-XSS-Protection: 1; mode=block` - Enables browser XSS filter

### Permissive CORS Policy

Allows any origin to make cross-origin requests, exposing sensitive data.

#### Exploit

##### Method 1: Malicious HTML Page Attack

1. Ensure Security Hardening is **disabled** (vulnerable mode)
2. Ensure you are logged in and on the dashboard(http://localhost:5000/dashboard) in your browser
3. Open the included `attack.html` file by double-clicking it (located in the project root)
   - The file opens with `file://` origin (simulating a malicious website)
   - It provides two attack buttons with visual feedback
4. Click "Launch Attack on /api/security-config"
5. Click "Launch Attack on /check_balance/ACC1001"

**Expected Result (Vulnerable):** Both attacks show red "ATTACK SUCCEEDED" boxes. Attack 1 displays the full security configuration JSON stolen from the server. Attack 2 returns a response from the balance endpoint, even though it shows `{"error": "Invalid token"}` (because `attack.html` has no valid auth cookie), the important thing is that the cross-origin request was **not blocked**. The server responded with `Access-Control-Allow-Origin: *`, which means any website can read the response. With a proper CORS policy, the browser would block the response entirely and no data would be returned at all.

##### Method 2: Via Browser Console (Quick Test)

1. Ensure Security Hardening is **disabled** (vulnerable mode)
2. Log into Vulnerable Bank at http://localhost:5000/login
3. Open a completely different website (e.g., google.com) in a new tab
4. Open browser console on that tab
5. Execute:
   ```javascript
   fetch('http://localhost:5000/api/security-config')
       .then(r => r.json())
       .then(data => console.log('Cross-origin data stolen:', data))
       .catch(e => console.log('Blocked by CORS:', e));
   ```

**Expected Result (Vulnerable):** The console prints the stolen security configuration JSON. This request originated from a completely different domain (e.g., google.com), yet the server accepted it and returned readable data. This is because the server's `Access-Control-Allow-Origin: *` header tells the browser to allow any origin to read the response.

#### Mitigate

**Option 1: Using Runtime Toggle**
1. Go to http://localhost:5000
2. Enable the "Global Security Hardening" toggle at the top of the page
3. Open `attack.html` and click both attack buttons

**Option 2: Using Environment Variables (Persistent)**
1. Update `.env` file:
   ```
   SECURITY_HARDENING_ENABLED=true
   ALLOWED_CORS_ORIGINS=http://localhost:5000,http://127.0.0.1:5000
   ```
   Note: Only specify the exact origins that should have access
2. Restart the application:
   - Docker: `docker-compose down && docker-compose up -d`
   - Local: Stop and run `python app.py`
3. Open `attack.html` and click both attack buttons

**Expected Result (Protected):** Both attacks show green "ATTACK BLOCKED BY CORS!" boxes. The browser console shows a CORS error (`Failed to fetch`) because the server no longer sends `Access-Control-Allow-Origin: *`. Instead, it only allows requests from `http://localhost:5000`, so the browser blocks the `attack.html` page (which runs from the `file://` origin) from reading any response. The same requests that succeeded before are now completely blocked at the browser level.

### Debug Mode in Production

Exposes detailed error messages and debug endpoints with sensitive information.

#### Exploit

##### Method 1: Accessing Debug Endpoint

1. Ensure Security Hardening is **disabled** (vulnerable mode)
2. In your browser address bar, navigate to:
   ```
   http://localhost:5000/debug/users
   ```
3. Observe exposed debug information including:
   - Complete list of all users in the database
   - User IDs and usernames
   - Account numbers
   - **Plain text passwords**
   - Admin status flags

**Expected Result (Vulnerable):** Debug endpoint returns JSON with all user records including sensitive data:
```json
{
  "users": [
    {
      "account_number": "ADMIN001",
      "id": 1,
      "is_admin": true,
      "password": "admin123",
      "username": "admin"
    },
    ...
  ]
}
```

##### Method 2: Triggering Detailed Error Messages

Log in as any user.
2. Open browser console (F12 → Console)
3. Execute an intentionally malformed API request:
   ```javascript
   fetch('/api/bill-payments/create', {
       method: 'POST',
       headers: {
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
       },
       body: JSON.stringify({biller_id: 999999, amount: -100})
   })
   .then(r => r.json())
   .then(data => console.log('ERROR:', JSON.stringify(data, null, 2)));
   ```
4. Observe the detailed error response includes:
   - `status`: Error status
   - `message`: Full database constraint violation details (table name, column name, row contents)
   - `error_type`: Exception class name (e.g., "NotNullViolation")
   - `timestamp`: Exact time of the error
   - `debug_info`: Endpoint name and detailed error information

**Expected Result (Vulnerable):** The console shows a `500 INTERNAL SERVER ERROR` with detailed diagnostic information revealing internal application structure:
```json
{
  "status": "error",
  "message": "null value in column \"payment_method\" of relation \"bill_payments\" violates not-null constraint\nDETAIL:  Failing row contains (14, 3, 999999, -100.00, null, null, BILL..., pending, 2026-..., null, Bill Payment).\n",
  "error_type": "NotNullViolation",
  "timestamp": "2026-02-09 04:09:22.562588",
  "debug_info": {
    "endpoint": "unknown_endpoint",
    "error_details": "null value in column \"payment_method\" of relation \"bill_payments\" violates not-null constraint\nDETAIL:  Failing row contains (14, 3, 999999, -100.00, null, null, BILL..., pending, 2026-..., null, Bill Payment).\n"
  }
}
```

#### Mitigate

**Option 1: Using Runtime Toggle (Recommended)**
1. Go to `http://localhost:5000/dashboard`
2. Click "Enable Security Hardening" toggle
3. Try accessing the debug endpoint:
   ```
   http://localhost:5000/debug/users
   ```

**Option 2: Using Environment Variables**
1. Update `.env` file:
   ```
   SECURITY_HARDENING_ENABLED=true
   ```
2. Restart the application:
   - Docker: `docker-compose down && docker-compose up -d`
   - Local: Stop server (Ctrl+C) and run `python app.py`
3. Try accessing the debug endpoint:
   ```
   http://localhost:5000/debug/users
   ```

**Test Error Message Handling:**
Execute a malformed API request in browser console:
```javascript
fetch('/api/bill-payments/create', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
    },
    body: JSON.stringify({biller_id: 999999, amount: -100})
})
.then(r => r.json())
.then(data => console.log('ERROR:', JSON.stringify(data, null, 2)));
```

**Expected Result (Protected):**
- Debug endpoint returns `{"status": "error", "message": "Not found"}` with 404 status
- Error responses contain ONLY generic messages without revealing internal details:
```json
{
  "status": "error",
  "message": "An error occurred processing your request. Please contact support if this persists.",
  "error_code": "ERR_500"
}
```

**Notice what's MISSING in hardened mode:**
- No `error_type` (exception class names)
- No `timestamp` (error timing information)
- No `debug_info` (endpoint details)
- No database constraint details
- No stacktraces or file paths
- ✗No internal variable names

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
   - **Secure**: Should show false
   - **HttpOnly**: Should show false
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
   - **Secure**: Still false — expected on HTTP localhost, only set over HTTPS
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

