# Demo Interface - Vulnerability Status Dashboard

The demo interface provides a **live status monitoring dashboard** that displays the current state of all vulnerability toggles in the Vulnerable Bank application. This is a presentation tool that complements the comprehensive documentation in the markdown files.

**Note:** This dashboard displays status only. For detailed testing instructions, exploit scenarios, and mitigation steps, see the individual vulnerability documentation files: `XSS.md`, `BOLA.md`, `Security_Misconfiguration.md`, etc.

## Prerequisites

- Browser access to functioning web app
- Application running with Docker or local Flask server
- At least one registered user account
## Accessing the Demo Interface
Log in to any user account
Navigate to: `http://localhost:5000/demo`

No authentication required - the demo panel is publicly accessible for educational purposes.

## Features

### Real-Time Vulnerability Status Dashboard

The demo interface displays the current state of all 10 vulnerability toggles:

1. **Cross-Site Scripting (XSS)**
2. **Security Misconfiguration**
3. **SQL Injection**
4. **Broken Authorization (BOLA)**
5. **Information Disclosure**
6. **Mass Assignment**
7. **Server-Side Request Forgery (SSRF)**
8. **Weak Password Hashing**
9. **File Upload Vulnerabilities**
10. **AI Prompt Injection**

Each vulnerability card displays:
- **VULNERABLE** (red) or **PROTECTED** (green) status
- Vulnerability name

### Summary Statistics

Top banner displays:
- Total vulnerabilities: 10
- Currently vulnerable count (red)
- Currently protected count (green)

### Color-Coded Status Cards

- **Red cards**: Vulnerability is currently enabled (protection disabled)
- **Green cards**: Protection is currently enabled (vulnerability mitigated)
- **Documentation Links**: Each card links to the detailed markdown documentation for that vulnerability

## Usage

### Viewing Current State

1. Navigate to `/demo`
2. Observe the summary counts at the top
3. Scroll through vulnerability cards to see individual states
4. Each card color indicates current protection status

### Testing a Vulnerability

1. Locate the vulnerability card you want to test on the dashboard
2. Note its current state (VULNERABLE or PROTECTED)
3. Click the documentation link on the card (e.g., "DOCS/XSS.md")
4. Follow the detailed testing instructions in the markdown documentation file
5. Return to the dashboard to verify status changes after toggling protections

### Toggling Protections (for Development)

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

### Using the Global Toggle

For quick demonstrations without restarting the application:

1. Navigate to the home page at `http://localhost:5000`
2. Click the yellow **"Toggle Vulnerabilities"** link in the header
3. An alert will show "Hardened mode: ON" or "Hardened mode: OFF"
4. Refresh the `/demo` page to see all protections switch to green (ON) or return to individual states (OFF)
5. Refresh the dashboard to see the badge indicators update

**Note:** This is a runtime toggle that overrides `.env` settings temporarily without requiring an application restart. It resets when the application is restarted.

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
