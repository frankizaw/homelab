# Cybersecurity Homelab (Lab-as-Code)

[English](#english) | [Polski](#polski)

---

<a name="english"></a>
## English Version

A lightweight, repeatable, dual-mode security testing environment designed for **Purple Teaming**, log analysis, attack simulation, and evasion testing.

Created as a practical training environment for detection engineering and security monitoring (e.g. with Log-Sentry).

---

### Architecture Overview

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

### Quick Start

The homelab supports **Dual-Mode**:
1. **Containerized (Docker Compose)**: For production-like isolation (`compose.yaml`).
2. **Native Zero-Dependency (Python)**: Runs out of the box with zero external dependencies and no root permissions required.

#### 1. Start the Lab
```bash
./lab.sh start
```
*The script automatically detects if Docker is active; if not, it launches the native target server on `http://localhost:8080`.*

#### 2. Check Lab Status
```bash
./lab.sh status
```

#### 3. Run Simulated Red Team Attacks
```bash
# Run both standard (blatant) attacks and evasion/obfuscation payloads
./lab.sh attack all

# Or run specific test sets:
./lab.sh attack blatant
./lab.sh attack evasion
```

#### 4. Run Detection Analysis
```bash
./lab.sh analyze
```
*Directly feeds the lab's `logs/access.log` into `log-sentry` to check detection rates.*

#### 5. Stop the Lab
```bash
./lab.sh stop
```

---

### Project Structure

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

### Evasion & Detection Scenarios

See [**`LAB_SCENARIOS.md`**](LAB_SCENARIOS.md) for step-by-step walkthroughs of:
- **SQL Injection**: Plain `UNION SELECT` vs `/**/` comment obfuscation.
- **Directory Traversal**: Plain `../../` vs Single & Double URL Encoding (`%2e%2e%2f`).
- **Cross-Site Scripting (XSS)**: Plain `<script>` tags vs SVG/Body event handlers (`<svg/onload=alert(1)>`).
- **Reconnaissance**: Sensitive file discovery (`.env`, `.git/config`, `phpmyadmin`).
- **User-Agent Fingerprinting**: Detecting tools like `sqlmap`, `nikto`, `gobuster`.

---

### Disclaimer

This laboratory is intended solely for educational purposes, defensive security research, and detection rule development. Do not use these attack techniques against systems without explicit prior authorization.

---

<a name="polski"></a>
## Wersja Polska (Polish Version)

Lekkie, powtarzalne środowisko testowe bezpieczeństwa w trybie dwutrybowym (Dual-Mode), zaprojektowane z myślą o ćwiczeniach **Purple Teaming**, analizie logów, symulacji ataków oraz testowaniu technik omijania systemów detekcji (evasion).

Stworzone jako praktyczny poligon szkoleniowy dla inżynierii detekcji (Detection Engineering) i monitorowania bezpieczeństwa (np. przy użyciu Log-Sentry).

---

### Przegląd architektury

```text
       [ RED TEAM / ATAKUJĄCY ]
   (curl, skrypt w Pythonie, exploity)
                 │
                 ▼ Ruch HTTP
       ┌───────────────────┐
       │   REVERSE PROXY   │  Nginx / Wbudowany rejestrator logów:
       │      (Nginx)      │  Zapisuje wszystkie żądania do access.log
       └─────────┬─────────┘  (Format Nginx Combined Log)
                 │
                 ▼ Przekazywanie żądań (Proxy)
       ┌───────────────────┐
       │ PODATNA APLIKACJA │  Symulowany cel z celowo wprowadzonymi lukami
       │ (Target Service)  │  (SQLi, Directory Traversal, Reflected XSS)
       └───────────────────┘
                 │
                 ▼ Współdzielony plik logs/access.log
       ┌───────────────────┐
       │ BLUE TEAM / SIEM  │  Silnik detekcji (np. log-sentry)
       │   (Log-Sentry)    │  Analizuje strumień logów w czasie rzeczywistym
       └───────────────────┘
```

---

### Szybki start

Homelab obsługuje **tryb dwutrybowy (Dual-Mode)**:
1. **Kontenerowy (Docker Compose)**: Zapewnia produkcyjną izolację usług (`compose.yaml`).
2. **Natywny bez zależności (Python)**: Działa od razu po pobraniu, nie wymaga zewnętrznych bibliotek ani uprawnień roota.

#### 1. Uruchomienie laboratorium
```bash
./lab.sh start
```
*Skrypt automatycznie wykrywa obecność Dockera; jeśli Docker nie jest aktywny, uruchamia natywny serwer w Pythonie pod adresem `http://localhost:8080`.*

#### 2. Sprawdzenie statusu laboratorium
```bash
./lab.sh status
```

#### 3. Wykonanie symulacji ataków Red Team
```bash
# Uruchomienie wszystkich ataków: jawnych (blatant) oraz zaciemnionych (evasion)
./lab.sh attack all

# Lub uruchomienie wybranego zestawu testów:
./lab.sh attack blatant
./lab.sh attack evasion
```

#### 4. Uruchomienie analizy detekcji
```bash
./lab.sh analyze
```
*Przekazuje plik `logs/access.log` bezpośrednio do `log-sentry`, weryfikując skuteczność wykrywania ataków.*

#### 5. Zatrzymanie laboratorium
```bash
./lab.sh stop
```

---

### Struktura projektu

```text
homelab/
├── compose.yaml                # Definicja środowiska kontenerowego (Nginx + Podatna aplikacja)
├── lab.sh                      # Zunifikowany skrypt zarządzający (CLI)
├── LAB_SCENARIOS.md            # Scenariusze Purple Team i ćwiczenia z omijania detekcji
├── README.md                   # Dokumentacja projektu
│
├── proxy/
│   └── nginx.conf              # Konfiguracja produkcyjna reverse proxy Nginx
│
├── targets/
│   └── vulnerable-app/         # Podatna aplikacja docelowa
│       ├── app.py              # Aplikacja w Pythonie bez zewnętrznych zależności
│       ├── Dockerfile          # Definicja kontenera Docker
│       └── requirements.txt    # Wymagania (tylko biblioteka standardowa)
│
├── attacks/                    # Moduł symulacji ataków Red Team
│   ├── exploit_runner.py       # Skrypt automatyzujący wysyłanie ataków
│   └── payloads.json           # Zestaw przygotowanych ładunków (Jawne vs Evasion)
│
└── logs/                       # Współdzielony katalog logów
    └── access.log              # Strumień logów w formacie Nginx Combined Log
```

---

### Scenariusze omijania i detekcji

Zobacz [**`LAB_SCENARIOS.md`**](LAB_SCENARIOS.md), aby poznać szczegółowe instrukcje krok po kroku:
- **SQL Injection**: Jawne `UNION SELECT` vs zaciemnianie komentarzami `/**/`.
- **Directory Traversal**: Jawne `../../` vs pojedyncze i podwójne kodowanie URL (`%2e%2e%2f`).
- **Cross-Site Scripting (XSS)**: Klasyczne znaczniki `<script>` vs procedury obsługi zdarzeń SVG/Body (`<svg/onload=alert(1)>`).
- **Rekonesans**: Wykrywanie prób pobrania wrażliwych plików (`.env`, `.git/config`, `phpmyadmin`).
- **Fingerprinting User-Agent**: Rozpoznawanie skanerów automatycznych, takich jak `sqlmap`, `nikto`, `gobuster`.

---

### Zastrzeżenie prawne (Disclaimer)

To środowisko laboratoryjne jest przeznaczone wyłącznie do celów edukacyjnych, defensywnych badań nad bezpieczeństwem oraz tworzenia i testowania reguł detekcji. Nie wolno stosować przedstawionych technik ataku przeciwko systemom bez uprzedniej wyraźnej zgody ich właścicieli.
