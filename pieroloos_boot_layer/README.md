# PieroloOS — Independent Visual Boot Layer

This directory implements Option 5: a presentation-only boot layer separated from the PieroloOS application runtime.

## Design principle

The official PieroloCorp logo is treated as a fixed identity asset. The logo itself does not rotate, drift, scale repeatedly, or morph. Ambient stars, nebula glow, and orbital lines provide motion around it, while the complete boot layer fades away before the application loads.

The boot layer contains **no database logic, business logic, Streamlit code, authentication logic, or application state**.

## Files

```text
pieroloos_boot_layer/
├── index.html
├── boot.css
├── boot.js
├── README.md
└── assets/
    └── PieroloCorp_Logo.webp
```

## Application hand-off

The boot page redirects to `/app/` after the visual startup sequence. In a production deployment, `/` should be served by a lightweight web server or frontend gateway, while `/app/` routes to the Streamlit application.

Recommended topology:

```text
Browser
  │
  ▼
HTTPS / Reverse Proxy
  │
  ├── /       → Static PieroloOS Boot Layer
  │             └── official logo + cosmic environment
  │
  └── /app/   → Streamlit PieroloOS runtime
                ├── UI
                ├── SQLite/PostgreSQL
                ├── workflows
                └── business logic
```

## Important deployment note

Streamlit Community Cloud does not provide the kind of root-level reverse-proxy routing needed to make this a genuinely independent pre-application document. For the full Option 5 architecture, deploy the boot layer and Streamlit behind a gateway/reverse proxy such as Nginx, Caddy, Traefik, or a small frontend server.

The current `app.py` should not be modified merely to create this visual layer.
