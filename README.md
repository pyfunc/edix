
# Edix - Uniwersalny Edytor Struktur Danych

## 📋 Spis treści
1. [Wprowadzenie](#-wprowadzenie)
2. [Wymagania systemowe](#-wymagania-systemowe)
3. [Instalacja](#-instalacja)
4. [Konfiguracja](#-konfiguracja)
5. [Uruchomienie](#-uruchomienie)
6. [Testowanie](#-testowanie)
7. [Rozwój](#-rozwój)
8. [Wdrażanie](#-wdrażanie)
9. [Licencja](#-licencja)

## 🌟 Wprowadzenie

Edix to zaawansowany edytor struktur danych z dynamicznym tworzeniem tabel SQL, wbudowanym frontendem i możliwością integracji z istniejącymi projektami. Pozwala na definiowanie i zarządzanie strukturami danych za pomocą intuicyjnego interfejsu użytkownika.

## 💻 Wymagania systemowe

- Python 3.8+
- Node.js 16+ (tylko do rozwoju frontendu)
- SQLite (domyślnie) lub PostgreSQL/MySQL
- System operacyjny: Linux, macOS, Windows (z WSL2 zalecane dla Windows)

## 📥 Instalacja

### Środowisko wirtualne (zalecane)

```bash
# Utwórz i aktywuj środowisko wirtualne
python -m venv venv
source venv/bin/activate  # Linux/macOS
# lub
# .\venv\Scripts\activate  # Windows

# Zainstaluj zależności
pip install -e .

# Zainstaluj zależności deweloperskie
pip install -e ".[dev]"
```

### Instalacja frontendu

```bash
cd frontend_src
npm install
npm run build
cd ..
```

## ⚙️ Konfiguracja

Skopiuj plik `.env.example` do `.env` i dostosuj ustawienia:

```bash
cp .env.example .env
```

Przykładowa konfiguracja:
```env
# Tryb działania (development, production, test)
APP_ENV=development

# Ustawienia bazy danych
DATABASE_URL=sqlite+aiosqlite:///./edix.db
# Dla PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://user:password@localhost/edix

# Ustawienia bezpieczeństwa
SECRET_KEY=twoj_tajny_klucz
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Ustawienia aplikacji
API_PREFIX=/api/v1
FRONTEND_URL=http://localhost:3000
```

## 🚀 Uruchomienie

### Tryb deweloperski (z automatycznym przeładowaniem)

```bash
# Uruchom serwer backendowy
uvicorn edix.main:app --reload

# W osobnym terminalu uruchom frontend w trybie deweloperskim
cd frontend_src
npm run dev
```

### Tryb produkcyjny

```bash
# Zbuduj frontend
cd frontend_src
npm run build
cd ..

# Uruchom serwer produkcyjny
uvicorn edix.main:app --host 0.0.0.0 --port 8000
```

Aplikacja będzie dostępna pod adresem: http://localhost:8000

## 🧪 Testowanie

### Testy jednostkowe (backend)

```bash
# Uruchom wszystkie testy
pytest

# Uruchom testy z pokryciem kodu
pytest --cov=edix --cov-report=term-missing

# Uruchom testy z generowaniem raportu HTML
pytest --cov=edix --cov-report=html
```

### Testy integracyjne

```bash
# Uruchom testy integracyjne
pytest tests/integration
```

### Testy frontendowe

```bash
cd frontend_src

# Uruchom testy jednostkowe
npm test

# Uruchom testy z pokryciem
npm run test:coverage
```

### Testy wydajnościowe

```bash
# Uruchom testy wydajnościowe z użyciem locust
locust -f tests/performance/locustfile.py
```

## 🔧 Rozwój

### Struktura projektu

```
edix/
├── edix/                # Kod źródłowy Pythona
│   ├── api/             # Endpointy API
│   ├── core/            # Logika biznesowa
│   ├── crud/            # Operacje na bazie danych
│   ├── db/              # Konfiguracja bazy danych
│   ├── models/          # Modele Pydantic i SQLAlchemy
│   ├── schemas/         # Schematy Pydantic
│   ├── static/          # Pliki statyczne
│   └── templates/       # Szablony HTML
├── frontend_src/        # Kod źródłowy frontendu
│   ├── public/          # Zasoby statyczne
│   └── src/             # Kod React
├── migrations/          # Migracje bazy danych
├── tests/               # Testy
│   ├── unit/            # Testy jednostkowe
│   ├── integration/     # Testy integracyjne
│   └── performance/     # Testy wydajnościowe
├── .env                # Zmienne środowiskowe
├── .gitignore
├── pyproject.toml      # Konfiguracja projektu Python
└── README.md           # Ten plik
```

### Tworzenie migracji bazy danych

```bash
# Utwórz nową migrację
alembic revision --autogenerate -m "Opis zmiany"

# Zastosuj migracje
alembic upgrade head

# Cofnij migrację
alembic downgrade -1
```

## 🚀 Wdrażanie

### Docker

```bash
# Zbuduj obrazy
docker-compose build

# Uruchom kontenery
docker-compose up -d

# Zatrzymaj kontenery
docker-compose down
```

### Systemd (produkcja)

Przykładowa konfiguracja usługi systemd (`/etc/systemd/system/edix.service`):

```ini
[Unit]
Description=Edix Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/edix
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn edix.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📄 Licencja

Ten projekt jest dostępny na licencji MIT. Zobacz plik [LICENSE](LICENSE) aby uzyskać więcej informacji.

## 👥 Wkład

1. Sklonuj repozytorium
2. Utwórz nowy branch (`git checkout -b feature/nazwa-funkcjonalnosci`)
3. Zatwierdź zmiany (`git commit -m 'Dodano nową funkcjonalność'`)
4. Wypchnij zmiany (`git push origin feature/nazwa-funkcjonalnosci`)
5. Otwórz Pull Request
- Zarządzanie produktami/katalogami

Cały projekt jest **production-ready** i może być od razu opublikowany na PyPI, zintegrowany z istniejącymi aplikacjami lub użyty jako standalone CMS.