# Security Misconfiguration

Security misconfiguration occurs when security settings are defined, implemented, or maintained improperly. This includes weak secret keys, permissive CORS policies, missing security headers, debug mode in production, and insecure session management.

## Prerequisites

- Browser access to functioning web app
- One registered user account
- Access to browser developer tools (Network and Console tabs)

## Configuration

**Runtime Toggle (Recommended for Testing)**

Use the **Toggle Vulnerabilities** button on the homepage at `http://localhost:5000/` to switch between vulnerable and hardened modes without restarting the application.

---

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
2. Go to `http://localhost:5000/` and click the **Toggle Vulnerabilities** button
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

---

### Permissive CORS Policy

Allows any origin to make cross-origin requests, exposing sensitive data.

#### Exploit

##### Method 1: Malicious HTML Page Attack

1. Ensure Security Hardening is **disabled** (vulnerable mode)
2. Open the included `attack.html` file by double-clicking it (located in the project root)
   - The file opens with `file://` origin (simulating a malicious website)
   - It provides two attack buttons with visual feedback
3. Click "Launch Attack on /api/security-config"
4. Click "Launch Attack on /check_balance/ACC1001"

**Expected Result (Vulnerable):** Both attacks show red "ATTACK SUCCEEDED" boxes. Attack 1 displays the full security configuration JSON stolen from the server. Attack 2 returns a response from the balance endpoint — the important thing is that the cross-origin request was **not blocked**. The server responded with `Access-Control-Allow-Origin: *`, which means any website can read the response.

##### Method 2: Via Browser Console (Quick Test)

1. Ensure Security Hardening is **disabled** (vulnerable mode)
2. Log into Vulnerable Bank at `http://localhost:5000/login`
3. Open a completely different website (e.g., google.com) in a new tab
4. Open browser console on that tab
5. Execute:
   ```javascript
   fetch('http://localhost:5000/api/security-config')
       .then(r => r.json())
       .then(data => console.log('Cross-origin data stolen:', data))
       .catch(e => console.log('Blocked by CORS:', e));
   ```

**Expected Result (Vulnerable):** The console prints the stolen security configuration JSON. This request originated from a completely different domain yet the server accepted it and returned readable data.

#### Mitigate

**Option 1: Using Runtime Toggle**
1. Go to `http://localhost:5000`
2. Click the **Toggle Vulnerabilities** button
3. Open `attack.html` and click both attack buttons

**Option 2: Using Environment Variables (Persistent)**
1. Update `.env` file:
   ```
   SECURITY_HARDENING_ENABLED=true
   ALLOWED_CORS_ORIGINS=http://localhost:5000,http://127.0.0.1:5000
   ```
2. Restart the application:
   - Docker: `docker-compose down -v --remove-orphans && docker-compose up -d --build`
   - Local: Stop and run `python app.py`
3. Open `attack.html` and click both attack buttons

**Expected Result (Protected):** Both attacks show green "ATTACK BLOCKED BY CORS!" boxes. The browser blocks the `attack.html` page (which runs from the `file://` origin) from reading any response.

---

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
    }
  ]
}
```

##### Method 2: Triggering Detailed Error Messages

1. Log in as any user.
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

**Expected Result (Vulnerable):** The console shows a `500 INTERNAL SERVER ERROR` with detailed diagnostic information revealing internal application structure including database constraint details, exception class names, and endpoint information.

#### Mitigate

**Option 1: Using Runtime Toggle (Recommended)**
1. Go to `http://localhost:5000/`
2. Click the **Toggle Vulnerabilities** button
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
   - Docker: `docker-compose down -v --remove-orphans && docker-compose up -d --build`
   - Local: Stop server (Ctrl+C) and run `python app.py`
3. Try accessing the debug endpoint

**Expected Result (Protected):**
- Debug endpoint returns `{"status": "error", "message": "Not found"}` with 404 status
- Error responses contain only generic messages without revealing internal details
