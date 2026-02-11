# Cross-Site Scripting (XSS)

XSS allows attackers to inject malicious scripts into web pages viewed by other users. When user input is rendered without sanitization, attackers can execute arbitrary JavaScript in victims' browsers.

## Prerequisites

- Browser access to functioning web app
- One registered user account
- Access to browser developer console

## Toggle Setup

Use the global **Toggle Vulnerabilities** button on the app's homepage to switch between Vulnerable (protections off) and Hardened (protections on) states. For the exploit steps, ensure the toggle is set to **Vulnerable**. For mitigation verification, set it to **Hardened**—no env changes or restarts needed.

**Important — Token Expiration in Hardened Mode:** When the toggle is set to Hardened, JWT tokens expire after **5 seconds** by default, which is too short to complete any test. Before testing mitigations, increase the expiration in `mitigations/session_exp.py` at **line 10**. Change:
```python
'exp': datetime.utcnow() + timedelta(seconds=5)
```
to a longer duration, for example:
```python
'exp': datetime.utcnow() + timedelta(minutes=10)
```
After making this change, restart the application. You must also **log out and log back in** after toggling to Hardened mode so your new token is signed with the updated secret.

## Demonstrations

### Transaction Description XSS

Allows injection of malicious scripts through transaction descriptions.

#### Exploit

1. Confirm the app is in **Vulnerable** mode (Toggle Mitigation should indicate protections are off)
2. Log in to your account
3. Navigate to "Money Transfer" section in the dashboard
4. Fill in the transfer form:
   - **Recipient Account Number**: Enter any valid account number (e.g., `ACC1002` for another test user)
   - **Amount**: Enter any amount (e.g., `10.00`)
   - **Description**: Enter the following XSS payload:
     ```
     <img src=x onerror="alert('XSS Vulnerability!')">
     ```
5. Click "Send Money" button to submit the transaction
6. Navigate to "Transaction History" section on your dashboard
7. Observe the alert popup appears immediately when the page renders

**Expected Result (Vulnerable):** Alert popup displays "XSS Vulnerability!" demonstrating arbitrary JavaScript execution. The script executes each time the transaction history is rendered (including immediately after the transfer completes).

#### Mitigate

1. Click **Toggle Mitigation** to switch to **Hardened** mode (protections on)
2. Log out and log back in (to get a new token signed with the updated secret)
3. Repeat the exploit steps (send a new transfer with the same XSS payload in the description)
4. Navigate to "Transaction History" section

**Expected Result (Protected):** The payload is rendered as plain text: `<img src=x onerror="alert('XSS Vulnerability!')">` with no script execution. The HTML is escaped and displayed literally.

### Bill Payment XSS

Allows injection of malicious scripts through bill payment descriptions. This demonstrates stored XSS that executes when payment history is viewed.

#### Exploit

1. Confirm the app is in **Vulnerable** mode (Toggle Mitigation should indicate protections are off)
2. Log in and navigate to "Bill Payments" section
3. Click "Pay Bill" button
4. Select any category (e.g., "Utilities") and biller (e.g., "Electric Company")
5. Fill in payment details:
   - **Amount**: Enter any amount (e.g., `50.00`)
   - **Payment Method**: Select "Account Balance" or "Virtual Card"
   - **Description**: Enter the following payload:
     ```
     <img src=x onerror="console.log('XSS in payment:',document.cookie)">
     ```
6. Submit the payment
7. Navigate to "Bill Payments" section and view payment history
8. Open browser console (F12 → Console tab)
9. Observe the XSS payload executes and logs session cookies

**Expected Result (Vulnerable):** Browser console displays session cookies with message "XSS in payment:" followed by the cookie data including JWT token.

#### Mitigate

1. Click **Toggle Mitigation** to switch to **Hardened** mode (protections on)
2. Log out and log back in (to get a new token signed with the updated secret)
3. Repeat exploit steps (create a new payment with XSS payload in description)
4. View payment history and check browser console

**Expected Result (Protected):** Browser console shows no XSS execution. The payload appears as literal text in the description of the bill payment: `<img src=x onerror="console.log('XSS in payment:',document.cookie)">`
