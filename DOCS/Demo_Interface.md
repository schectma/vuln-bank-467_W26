# Demo Interface and Vulnerability Toggle System

The demo interface provides a centralized control panel for viewing and understanding all vulnerability toggles in the Vulnerable Bank application. It serves as an educational tool for security demonstrations and testing.

## Prerequisites

- Browser access to functioning web app
- Application running with Docker or local Flask server

## Accessing the Demo Interface

Navigate to: `http://localhost:5000/demo`

No authentication required - the demo panel is publicly accessible for educational purposes.

## Features

### Real-Time Vulnerability Status Dashboard

The demo interface displays the current state of all 10 vulnerability toggles:

1. **Cross-Site Scripting (XSS)** - CWE-79
2. **Security Misconfiguration** - CWE-16
3. **SQL Injection** - CWE-89
4. **Broken Authorization (BOLA)** - CWE-285
5. **Information Disclosure** - CWE-200
6. **Mass Assignment** - CWE-915
7. **Server-Side Request Forgery (SSRF)** - CWE-918
8. **Weak Password Hashing** - CWE-256/522
9. **File Upload Vulnerabilities** - CWE-434
10. **AI Prompt Injection** - CWE-94

Each vulnerability shows:
- **VULNERABLE** (red) or **PROTECTED** (green) status
- Associated CWE identifier
- Brief description
- Test scenario instructions
- Link to detailed documentation

### Summary Statistics

Top banner displays:
- Total vulnerabilities: 10
- Currently vulnerable count (red)
- Currently protected count (green)

### Color-Coded Status Cards

- **Red cards**: Vulnerability is currently enabled (protection disabled)
- **Green cards**: Protection is currently enabled (vulnerability mitigated)

### Test Scenarios

Each vulnerability card includes:
- Step-by-step exploitation instructions
- Expected results for vulnerable state
- Expected results for protected state
- Links to detailed testing documentation

## Usage

### Viewing Current State

1. Navigate to `/demo`
2. Observe the summary counts at the top
3. Scroll through vulnerability cards to see individual states
4. Each card color indicates current protection status

### Testing a Vulnerability

1. Locate the vulnerability card you want to test
2. Note its current state (VULNERABLE or PROTECTED)
3. Read the "Test Scenario" section
4. Follow the instructions to exploit or verify protection
5. See detailed documentation by clicking vulnerability-specific docs

### Toggling Protections

Vulnerability states are controlled via environment variables in `.env`:

```bash
# Edit .env file
XSS_PROTECTION_ENABLED=false        # Set to true to enable
SECURITY_HARDENING_ENABLED=false    # Set to true to enable
SQL_INJECTION_PROTECTION=false      # Set to true to enable
# ... etc for all 10 vulnerabilities
```

After changing `.env`:
1. Restart the Docker containers: `docker-compose down && docker-compose up`
2. Or restart Flask: Stop server (Ctrl+C) and run `python app.py`
3. Refresh the demo page to see updated states

### Demonstration Workflow

**For Security Presentations:**

1. Start with all protections disabled (all red cards)
2. Demonstrate one vulnerability at a time
3. Show the exploit in action
4. Enable protection for that vulnerability
5. Restart application
6. Demonstrate mitigation
7. Refresh demo page to show green card
8. Repeat for next vulnerability

**For Automated Testing:**

The demo interface reflects the same configuration used by the application, so:
- Automated tests can verify protection states via `/api/security-config`
- CI/CD pipelines can toggle vulnerabilities for different test scenarios
- QA teams can quickly identify which protections are active

## API Endpoint

The demo interface fetches data from:

```
GET /api/security-config
```

Response:
```json
{
    "xss_protection_enabled": false,
    "security_hardening_enabled": false,
    "sql_injection_protection": false,
    "authorization_enabled": false,
    "information_disclosure_protection": false,
    "mass_assignment_protection": false,
    "ssrf_protection": false,
    "password_hashing_enabled": false,
    "file_upload_validation": false,
    "ai_prompt_injection_protection": false
}
```

## Technical Details

**Implementation:**
- Frontend: `templates/demo.html` - Single-page interface with responsive design
- Backend: `app.py` - `/demo` route and `/api/security-config` endpoint
- Configuration: `.env` file controls all toggle states

**Files:**
- `templates/demo.html`: Demo interface HTML/CSS/JavaScript
- `app.py`: Demo route handler and security config API
- `.env.example`: Documentation of all environment variables

**Design Features:**
- Responsive layout (works on mobile/tablet/desktop)
- Real-time status updates on page refresh
- Color-coded visual indicators
- No authentication required (educational tool)
- Links to detailed vulnerability documentation
