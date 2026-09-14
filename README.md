# Cybersecurity Homelab (Lab-as-Code)

A lightweight, repeatable, dual-mode security testing environment designed for **Purple Teaming**, log analysis, attack simulation, and evasion testing.

Created as a practical training environment for detection engineering and security monitoring (e.g. with Log-Sentry).

---

## Architecture Overview

```text
       [ RED TEAM / ATTACKER ]
   (curl, Python runner, exploits)
                 │
                 ▼ HTTP Traffic
       ┌───────────────────┐
       │   REVERSE PROXY   │  Nginx / Standalone Logger:
       │      (Nginx)      │  Captures all requests into access.log
       └─────────┬─────────┘  (Standard Combined Log Format)
                 │
                 ▼ Proxy forwarding
       ┌───────────────────┐
       │  VULNERABLE APP   │  Simulated target with intentional flaws
       │  (Target Service) │  (SQLi, Directory Traversal, Reflected XSS)
       └───────────────────┘
                 │
                 ▼ Shared logs/access.log
       ┌───────────────────┐
       │ BLUE TEAM / SIEM  │  Detection Engine (e.g. log-sentry)
       │    (Log-Sentry)   │  Analyzes log stream in real time
       └───────────────────┘
```

---

## Quick Start

The homelab supports **Dual-Mode**:
1. **Containerized (Docker Compose)**: For production-like isolation (`compose.yaml`).
2. **Native Zero-Dependency (Python)**: Runs out of the box with zero external dependencies and no root permissions required.

### 1. Start the Lab
```bash
./lab.sh start
```
*The script automatically detects if Docker is active; if not, it launches the native target server on `http://localhost:8080`.*

### 2. Check Lab Status
```bash
./lab.sh status
```

### 3. Run Simulated Red Team Attacks
```bash
# Run both standard (blatant) attacks and evasion/obfuscation payloads
./lab.sh attack all

# Or run specific test sets:
./lab.sh attack blatant
./lab.sh attack evasion
```

### 4. Run Detection Analysis
```bash
./lab.sh analyze
```
*Directly feeds the lab's `logs/access.log` into `log-sentry` to check detection rates.*

### 5. Stop the Lab
```bash
./lab.sh stop
```

---

## Project Structure

```text
homelab/
├── compose.yaml                # Container environment definition (Nginx + Target App)
├── lab.sh                      # Unified management CLI
├── LAB_SCENARIOS.md            # Purple Team lab scenarios & evasion exercises
├── README.md                   # Project documentation
│
├── proxy/
│   └── nginx.conf              # Production Nginx reverse proxy configuration
│
├── targets/
│   └── vulnerable-app/         # Vulnerable web target
│       ├── app.py              # Zero-dependency Python target application
│       ├── Dockerfile          # Container packaging
│       └── requirements.txt    # Dependencies (standard library)
│
├── attacks/                    # Red Team attack module
│   ├── exploit_runner.py       # Automated attack execution runner
│   └── payloads.json           # Curated test payloads (Blatant vs Evasion)
│
└── logs/                       # Shared access log directory
    └── access.log              # Nginx Combined Log format stream
```

---

## Evasion & Detection Scenarios

See [**`LAB_SCENARIOS.md`**](LAB_SCENARIOS.md) for step-by-step walkthroughs of:
- **SQL Injection**: Plain `UNION SELECT` vs `/**/` comment obfuscation.
- **Directory Traversal**: Plain `../../` vs Single & Double URL Encoding (`%2e%2e%2f`).
- **Cross-Site Scripting (XSS)**: Plain `<script>` tags vs SVG/Body event handlers (`<svg/onload=alert(1)>`).
- **Reconnaissance**: Sensitive file discovery (`.env`, `.git/config`, `phpmyadmin`).
- **User-Agent Fingerprinting**: Detecting tools like `sqlmap`, `nikto`, `gobuster`.

---

## Disclaimer

This laboratory is intended solely for educational purposes, defensive security research, and detection rule development. Do not use these attack techniques against systems without explicit prior authorization.
