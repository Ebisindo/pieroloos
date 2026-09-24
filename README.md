# PieroloOS — Fresh Streamlit Deployment Kit

This package is a clean deployment baseline for **PieroloOS v0.1**, with the missing
root-level `app.py` included.

## Repository structure

```text
PieroloOS/
├── app.py
├── requirements.txt
├── railway.toml
├── Procfile
├── .gitignore
├── .streamlit/
│   └── config.toml
├── assets/
│   ├── PieroloCorp_Logo.webp
│   ├── pierolocorp_logo.png
│   ├── pieroloos_background.svg
│   └── PieroloOS interface assets...
└── reports/
    └── .gitkeep
```

## Fresh GitHub deployment

1. Create a new GitHub repository.
2. Upload the **contents of this folder** to the repository root.
3. Confirm that `app.py` is visible at the repository root — not inside another
   nested folder.
4. Connect the repository to Railway.
5. Railway can use `railway.toml`, or the Start Command can be set manually to:

```bash
streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT
```

The application is deliberately configured to bind to Railway's runtime `$PORT`.

## Important MVP persistence note

The current application uses SQLite for the MVP. Railway containers use ephemeral
local storage, so the SQLite database should be treated as development/MVP state,
not as the long-term production database.

For the next scaling stage, move persistence to PostgreSQL and store secrets in
Railway environment variables.

## Official logo

`assets/PieroloCorp_Logo.webp` is included as the primary supplied logo asset.
The application also retains the previous PNG asset as a compatibility fallback.

## Scope

This kit focuses on getting the main PieroloOS application deployed cleanly.
The independent Option 5 visual boot layer can remain a separate presentation
layer and should not be confused with the Streamlit application entry point.
