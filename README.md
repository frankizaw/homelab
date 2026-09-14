# Cybersecurity Homelab (Lab-as-Code)

[English](#english) | [Polski](#polski)

---

<a name="english"></a>
## English

A lightweight, practical cybersecurity testbed built for hands-on Purple Teaming, web log analysis, and detection rule evaluation (designed to pair with the `log-sentry` project).

The goal of this project is to observe how common web attack vectors appear in web server access logs, and to evaluate how effectively evasion techniques bypass simple signature-based detection rules.

---

### Architecture & Traffic Flow

```text
       [ ATTACKER / RED TEAM ]
    (curl, Python exploit runner)
                 │
                 ▼ HTTP Traffic
       ┌───────────────────┐
       │   REVERSE PROXY   │  Nginx (or built-in Python logger):
       │      (Nginx)      │  Captures all requests into access.log
       └─────────┬─────────┘  (Standard Combined Log Format)
                 │
                 ▼ Proxy forwarding
       ┌───────────────────┐
       │  VULNERABLE APP   │  Target service with intentional flaws:
       │  (Target Service) │  SQLi, Directory Traversal, Reflected XSS
       └───────────────────┘
                 │
                 ▼ Shared logs/access.log
       ┌───────────────────┐
       │ BLUE TEAM / SIEM  │  Detection tool (log-sentry)
       │    (Log-Sentry)   │  Analyzes log stream to catch suspicious requests
       └───────────────────┘
```

---

### Dual-Mode Execution

The lab supports two operational modes:
1. **Docker Compose Mode**: Runs Nginx as a reverse proxy and the vulnerable application in isolated containers (`compose.yaml`).
2. **Native Python Mode (Zero Dependencies)**: Fallback for environments without Docker. Runs directly using the Python 3 standard library, requiring no third-party packages and no root privileges.

---

### Quick Start / Usage

The `lab.sh` script provides a unified CLI for managing the environment:

#### 1. Start the lab
```bash
./lab.sh start
```
*Automatically checks for Docker. If Docker is running, it deploys containers via Compose; otherwise, it starts the native Python server on port 8080.*

#### 2. Check status
```bash
./lab.sh status
```

#### 3. Run attack simulations
```bash
# Run all test scenarios (both standard and evasion payloads)
./lab.sh attack all

# Or run specific categories:
./lab.sh attack blatant
./lab.sh attack evasion
```

#### 4. Analyze detections with log-sentry
```bash
./lab.sh analyze
```
*Feeds `logs/access.log` into the `log-sentry` analyzer to verify detection rates and identify bypassed rules.*

#### 5. Stop the lab
```bash
./lab.sh stop
```

---

### Project Structure

```text
homelab/
├── compose.yaml                # Docker Compose environment definition (Nginx + Target App)
├── lab.sh                      # Management CLI script
├── LAB_SCENARIOS.md            # Purple Team scenarios & evasion exercise guide
├── README.md                   # Project documentation
│
├── proxy/
│   └── nginx.conf              # Nginx reverse proxy configuration (Combined log format)
│
├── targets/
│   └── vulnerable-app/         # Vulnerable web target application
│       ├── app.py              # Zero-dependency Python web application
│       ├── Dockerfile          # Container packaging
│       └── requirements.txt    # Standard library only
│
├── attacks/                    # Red Team attack simulation module
│   ├── exploit_runner.py       # Automated attack runner script
│   └── payloads.json           # Curated test payloads (blatant vs evasion)
│
└── logs/                       # Shared access log directory
    └── access.log              # Log stream parsed by Blue Team detection
```

---

### Test Scenarios & Coverage

Detailed walkthroughs, payload examples, and evasion mechanics are documented in [**`LAB_SCENARIOS.md`**](LAB_SCENARIOS.md):
- **SQL Injection**: Standard `UNION SELECT` vs obfuscation using inline SQL comments (`/**/`).
- **Directory Traversal**: Plain `../../` vs single (`%2f`) and double (`%252e`) URL encoding.
- **Cross-Site Scripting (XSS)**: Classic `<script>` tags vs event handlers in SVG and Body tags (`<svg/onload=alert(1)>`).
- **Reconnaissance**: Probing sensitive paths (`.env`, `.git/config`, `phpmyadmin`).
- **User-Agent Fingerprinting**: Identifying automated security tools (e.g. `sqlmap`) via HTTP headers.

---

### Security Disclaimer

This project is intended strictly for educational purposes, defensive security research, and detection rule development in a controlled lab environment. Do not use these attack tools or payloads against systems without explicit authorization.

---

<a name="polski"></a>
## Wersja Polska

Lokalne środowisko testowe typu Lab-as-Code stworzone do praktycznej nauki Purple Teamingu, analizy logów serwerowych oraz testowania skuteczności reguł detekcji (zaprojektowane do współpracy z narzędziem `log-sentry`).

Głównym celem projektu jest obserwacja, w jaki sposób typowe ataki webowe zapisują się w logach serwera Nginx oraz badanie, na ile techniki zaciemniania zapytań (evasion) pozwalają ominąć proste reguły detekcyjne oparte na wyrażeniach regularnych.

---

### Architektura i przepływ ruchu

```text
       [ ATAKUJĄCY / RED TEAM ]
    (curl, skrypt exploit_runner)
                 │
                 ▼ Ruch HTTP
       ┌───────────────────┐
       │   REVERSE PROXY   │  Nginx (lub wbudowany logger w Pythonie):
       │      (Nginx)      │  Zapisuje wszystkie żądania do access.log
       └─────────┬─────────┘  (standardowy format Combined Log)
                 │
                 ▼ Przekazywanie żądań (Proxy)
       ┌───────────────────┐
       │ PODATNA APLIKACJA │  Aplikacja docelowa ze świadomymi lukami:
       │ (Target Service)  │  SQLi, Directory Traversal, Reflected XSS
       └───────────────────┘
                 │
                 ▼ Współdzielony plik logs/access.log
       ┌───────────────────┐
       │ BLUE TEAM / SIEM  │  Narzędzie detekcyjne (log-sentry)
       │   (Log-Sentry)    │  Analizuje logi i identyfikuje podejrzane żądania
       └───────────────────┘
```

---

### Dwa tryby uruchomienia (Dual-Mode)

Środowisko obsługuje dwa tryby działania:
1. **Tryb Docker Compose**: Uruchamia proxy Nginx oraz podatną aplikację w odizolowanych kontenerach (`compose.yaml`).
2. **Tryb natywny (Python bez zależności)**: Rozwiązanie zapasowe dla środowisk bez zainstalowanego Dockera. Aplikacja działa w oparciu o bibliotekę standardową Pythona 3 – nie wymaga zewnętrznych pakietów z `pip` ani uprawnień roota.

---

### Instrukcja uruchomienia

Zarządzanie środowiskiem odbywa się za pomocą skryptu pomocniczego `lab.sh`:

#### 1. Uruchomienie środowiska
```bash
./lab.sh start
```
*Skrypt automatycznie sprawdza obecność i działanie Dockera. Jeśli usługa jest aktywna, uruchamia kontenery; w przeciwnym razie startuje serwer natywny na porcie 8080.*

#### 2. Sprawdzenie statusu
```bash
./lab.sh status
```

#### 3. Uruchomienie symulacji ataków
```bash
# Wykonanie wszystkich scenariuszy (jawne oraz z technikami evasion)
./lab.sh attack all

# Uruchomienie wybranej kategorii:
./lab.sh attack blatant
./lab.sh attack evasion
```

#### 4. Weryfikacja detekcji w log-sentry
```bash
./lab.sh analyze
```
*Przekazuje plik `logs/access.log` do analizatora `log-sentry`, weryfikując skuteczność reguł i wskazując zapytania, które ominęły filtry.*

#### 5. Zatrzymanie środowiska
```bash
./lab.sh stop
```

---

### Struktura projektu

```text
homelab/
├── compose.yaml                # Konfiguracja środowiska kontenerowego (Nginx + Aplikacja)
├── lab.sh                      # Skrypt CLI do zarządzania laboratorium
├── LAB_SCENARIOS.md            # Przewodnik po scenariuszach ataków i omijania detekcji
├── README.md                   # Dokumentacja projektu
│
├── proxy/
│   └── nginx.conf              # Konfiguracja Nginx (zapis logów w formacie Combined)
│
├── targets/
│   └── vulnerable-app/         # Podatna aplikacja docelowa
│       ├── app.py              # Aplikacja w czystym Pythonie (biblioteka standardowa)
│       ├── Dockerfile          # Definicja kontenera Docker
│       └── requirements.txt    # Brak zewnętrznych zależności
│
├── attacks/                    # Moduł symulacji ataków (Red Team)
│   ├── exploit_runner.py       # Skrypt automatyzujący wysyłanie payloadów
│   └── payloads.json           # Zestaw przygotowanych ładunków (jawne vs evasion)
│
└── logs/                       # Współdzielony katalog logów
    └── access.log              # Logi dostępowe analizowane przez reguły Blue Team
```

---

### Zakres scenariuszy testowych

Szczegółowy opis testów, przykłady poleceń curl oraz mechanizmy omijania opisano w [**`LAB_SCENARIOS.md`**](LAB_SCENARIOS.md):
- **SQL Injection**: Standardowe zapytanie `UNION SELECT` vs rozbijanie słów kluczowych komentarzami SQL (`/**/`).
- **Directory Traversal**: Jawna sekwencja `../../` vs pojedyncze (`%2f`) oraz podwójne (`%252e`) kodowanie URL.
- **Cross-Site Scripting (XSS)**: Klasyczne znaczniki `<script>` vs procedury obsługi zdarzeń w tagach SVG i Body (`<svg/onload=alert(1)>`).
- **Rekonesans**: Próby odpytywania wrażliwych plików konfiguracyjnych (`.env`, `.git/config`, `phpmyadmin`).
- **Identyfikacja narzędzi (User-Agent)**: Wykrywanie skanerów automatycznych (np. `sqlmap`) na podstawie nagłówków żądań HTTP.

---

### Uwagi dotyczące bezpieczeństwa (Disclaimer)

Projekt został opracowany wyłącznie do celów edukacyjnych, badań nad bezpieczeństwem defensywnym oraz testowania reguł detekcji w kontrolowanym środowisku. Narzędzi ani ładunków testowych nie należy stosować przeciwko systemom bez uprzedniej wyraźnej zgody ich właścicieli.
