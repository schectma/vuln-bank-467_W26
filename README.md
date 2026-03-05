# Web Security Research — Vulnerable Bank

A web security research project conducted as part of CS 467 (Online Capstone) at Oregon State University, Winter 2026. This project is student managed and directed.

## Disclaimer

**This application is for web security research purposes only.** 

The Vulnerable Bank web application was not developed by this team. It is [an existing open source, intentionally vulnerable banking app](https://github.com/Commando-X/vuln-bank) developed by GitHub user [Commando-X.](https://github.com/Commando-X) Our work focuses on **demonstrating exploits** against its built-in vulnerabilities, **developing mitigations**, and **documenting** both the attacks and defenses so that anyone can reproduce the results.

## Project Overview

The goal of this project is to study common web application vulnerabilities by demonstrating exploits against a deliberately insecure web app, then hardening it against each discovered attack. For each vulnerability we produce:

1. **An exploit demonstration** showing the vulnerability in action
2. **A mitigation** that can be toggled on at runtime to harden the application
3. **A detailed write up** documenting both the attack and the mitigation

The final deliverable is this repository: all code, mitigations, and how-to documentation in one place. The application supports toggling protections on and off at runtime so that reviewers (TAs, instructors, or anyone else) can easily test each vulnerability in both its exploitable and hardened states.

## Table of Contents

- [Vulnerabilities Researched](#vulnerabilities-researched)
- [Stretch Goal: Password Hashing and Cracking](#stretch-goal-password-hashing-and-cracking)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Documentation](#documentation)
- [Team](#team)
- [References](#references)
- [License](#license)

## Vulnerabilities Researched

Each vulnerability can be toggled on/off at runtime via the hardening switch on the landing page or through the `/api/toggle/harden` endpoint. Detailed write-ups for each are linked in the Documentation column.

| # | Vulnerability | CWE | Documentation |
|---|---|---|---|
| 1 | SQL Injection | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) | [DOCS/SQLi.md](DOCS/SQLi.md) |
| 2 | Broken Object-Level Authorization (BOLA) | [CWE-639](https://cwe.mitre.org/data/definitions/639.html) | [DOCS/BOLA.md](DOCS/BOLA.md) |
| 3 | Cross-Site Scripting (XSS) | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) | [DOCS/XSS.md](DOCS/XSS.md) |
| 4 | Mass Assignment | [CWE-915](https://cwe.mitre.org/data/definitions/915.html) | [DOCS/MA.md](DOCS/MA.md) |
| 5 | Server-Side Request Forgery (SSRF) | [CWE-918](https://cwe.mitre.org/data/definitions/918.html) | [DOCS/SSRF.md](DOCS/SSRF.md) |
| 6 | Weak JWT Implementation | [CWE-347](https://cwe.mitre.org/data/definitions/347.html) | [DOCS/token_exp.md](DOCS/token_exp.md) |
| 7 | Cross-Site Request Forgery (CSRF) | [CWE-352](https://cwe.mitre.org/data/definitions/352.html) | [DOCS/CSRF.md](DOCS/CSRF.md) |
| 8 | Security Misconfiguration | [CWE-2](https://cwe.mitre.org/data/definitions/2.html) | [DOCS/Security_Misconfiguration.md](DOCS/Security_Misconfiguration.md) |
| 9 | Plaintext / Weak Password Storage | [CWE-256](https://cwe.mitre.org/data/definitions/256.html) | [DOCS/hashing.md](DOCS/hashing.md) |
| 10 | AI Prompt Injection | [CWE-77](https://cwe.mitre.org/data/definitions/77.html) | [DOCS/AI.md](DOCS/AI.md) |
| 11 | Exposure of Sensitive Information | [CWE-200](https://cwe.mitre.org/data/definitions/200.html) | [DOCS/AI.md](DOCS/AI.md) |
| 12 | Broken Authorization (AI Endpoint) | [CWE-862](https://cwe.mitre.org/data/definitions/862.html) | [DOCS/AI.md](DOCS/AI.md) |
| 13 | Insufficient Input Validation | [CWE-20](https://cwe.mitre.org/data/definitions/20.html) | — |
| 14 | Insufficient Rate Limiting | [CWE-770](https://cwe.mitre.org/data/definitions/770.html) | [DOCS/RATE_LIMITING.md](DOCS/RATE_LIMITING.md) |
| 15 | Race Conditions | [CWE-362](https://cwe.mitre.org/data/definitions/362.html) | — |
| 16 | Hardcoded Credentials | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) | — |

## Stretch Goal: Password Hashing and Cracking

The application includes a database of passwords hashed using different algorithms (plaintext, SHA-1, SHA-256, Argon2) at various difficulty levels. This allows demonstrating how to steal password hashes and attempt to crack them, illustrating the importance of proper cryptographic implementations.

- [Password Hashing Modes](DOCS/hashing.md)
- [Password Cracking Demonstrations](DOCS/hashing_cracking.md)

## Tech Stack

The upstream Vulnerable Bank application uses:

- **Backend:** Python 3.9, Flask 2.0.1, PostgreSQL 13, PyJWT, Argon2
- **Frontend:** HTML, CSS, JavaScript (Jinja2 templates)
- **Deployment:** Docker, Docker Compose, Google Cloud Platform (GCP)
- **Testing:** pytest
- **AI Integration:** [OpenRouter API](https://openrouter.ai/) (NVIDIA Nemotron)

## Live Instance

A hosted instance of the application is available for testing on Google Cloud Platform:

**http://34.28.235.106/**

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) (recommended)
- Or: Python 3.9+ and PostgreSQL 13

### Quick Start with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/schectma/vuln-bank-467_W26.git
   cd vuln-bank-467_W26
   ```

2. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   ```

3. (Optional) Add your [OpenRouter](https://openrouter.ai/) API key to `.env` if desired:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

4. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

5. Open your browser and navigate to `http://localhost:5000`.

### Local Development Setup

1. Clone the repository and create a virtual environment:
   ```bash
   git clone https://github.com/schectma/vuln-bank-467_W26.git
   cd vuln-bank-467_W26
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Ensure PostgreSQL is running and update `.env` with your database credentials (set `DB_HOST=localhost`).

3. Start the application:
   ```bash
   python3 app.py
   ```

## Usage

### Default Accounts

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |

New users can register through the UI and start with a $1,000 balance.

### Toggling Security Protections

The landing page includes a **Harden** toggle button that enables or disables all security mitigations at once. Individual protections (SQL injection, hashing, CORS, etc.) can also be toggled independently through the API.

- **Hardening off (default):** The application runs in its vulnerable state, all built in weaknesses are active.
- **Hardening on:** Parameterized queries, input validation, security headers, rate limiting, and other protections are activated.

This toggle system allows reviewers to easily test each vulnerability in both states without restarting the application.

### Resetting the Database

A **Reset Database** button on the landing page and in the admin control panel wipes all user created data and re-seeds the database with the default accounts and test data from `seed_data.sql`. This is useful after testing exploits that modify or corrupt data.

### Exploring Vulnerabilities

See the [DOCS/](DOCS/) directory for step by step guides on exploiting and mitigating each vulnerability. The [DOCS/README.md](DOCS/README.md) provides an application walkthrough with architecture diagrams.

## Project Structure

```
vuln-bank-467_W26/
├── app.py                  # Main Flask application (all routes)
├── auth.py                 # JWT token generation and verification
├── database.py             # PostgreSQL schema, connection pooling, seed data
├── ai_agent_deepseek.py    # AI chatbot integration (OpenRouter API)
├── attack.html             # Standalone CSRF attack demo page
├── templates/              # Jinja2 HTML templates (login, dashboard, admin, etc.)
├── static/                 # CSS, JS, uploaded files
├── mitigations/            # Hardened implementations for each vulnerability
│   ├── sql_injections.py   #   Parameterized queries
│   ├── BOLA.py             #   Authorization checks
│   ├── hashing.py          #   Argon2 password hashing
│   ├── MA.py               #   Field whitelisting
│   ├── SSRF.py             #   URL validation
│   ├── session_exp.py      #   Token expiration
│   ├── rate_limiting.py    #   Request rate enforcement
│   └── AI.py               #   AI prompt guardrails
├── seed_data.sql           # SQL seed data for default accounts and test data
├── exploits/               # Exploit payloads for demos
├── tests/                  # pytest test suite
├── DOCS/                   # Vulnerability write-ups and guides
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Testing

Build the test container/environment with Docker:
```bash
docker-compose -f docker-compose-test.yml up --build
```

Or locally (requires a running PostgreSQL instance):
```bash
pytest tests/
```

See [DOCS/tests.md](DOCS/tests.md) for details on the test suite.

## Documentation

Each write up in [DOCS/](DOCS/) covers:
- What the vulnerability is and its CWE classification
- Where it exists in the application
- Step by step instructions to exploit it
- How the corresponding mitigation works
- How to verify the mitigation is effective

The documentation is designed so that anyone can reproduce the results.

## Team

CS 467 — Online Capstone, Oregon State University, Winter 2026. This project is student managed and directed.

- [Jessica Johnson](https://github.com/JessJohn0)
- [Alexander Schectman](https://github.com/schectma)
- [Alejandro Rodriguez Varona](https://github.com/alejandrorodvar)
- [Chrystyan Pulido](https://github.com/chrys-pl)

## References

- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP Vulnerable Web Applications Directory](https://github.com/OWASP/OWASP-VWAD)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)
- [Top 10 Common Web Attacks](https://www.vpnmentor.com/blog/top-10-common-web-attacks)
- [Original Vulnerable Bank](https://github.com/milosilo/vuln-bank)

## License

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.
