# 📦 Edix - Universal Data Structure Editor

## Struktura projektu

```
edix/
│
├── edix/
│   ├── __init__.py
│   ├── __main__.py           # Entry point dla CLI
│   ├── app.py                 # FastAPI główna aplikacja
│   ├── models.py              # Modele danych i walidacja
│   ├── database.py            # Dynamiczne zarządzanie SQLite
│   ├── schemas.py             # Schema manager
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py          # API endpoints
│   │   └── websocket.py       # Real-time updates
│   ├── static/                # Frontend (bundled)
│   │   ├── index.html
│   │   ├── app.js
│   │   └── styles.css
│   └── templates/
│       └── editor.html        # Template dla edytora
│
├── frontend_src/              # Źródła frontend (do budowania)
│   ├── package.json
│   ├── src/
│   │   ├── index.js
│   │   ├── Editor.jsx
│   │   ├── SchemaEditor.jsx
│   │   └── DataGrid.jsx
│   └── webpack.config.js
│
├── pyproject.toml
├── setup.py
├── MANIFEST.in
├── README.md
├── LICENSE
├── requirements.txt
├── build.py                   # Skrypt do budowania frontend
└── tests/
    └── test_edix.py
```