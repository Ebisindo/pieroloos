from pathlib import Path
import base64
import sqlite3
from datetime import datetime
from typing import Optional

import streamlit as st


# ============================================================
# PIEROLOOS v0.1
# PROFESSIONAL SERVICE OPERATING SYSTEM
# PIEROLOCORP INTERNATIONAL LLC
# ============================================================

st.set_page_config(
    page_title="PieroloOS | PieroloCorp International LLC",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 1. PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ASSET_DIR = BASE_DIR / "assets"
REPORT_DIR = BASE_DIR / "reports"
DB_PATH = BASE_DIR / "pieroloos.db"

BACKGROUND_PATH = ASSET_DIR / "pieroloos_background.svg"

# Support either spelling while the repository is being standardised.
LOGO_CANDIDATES = [
    ASSET_DIR / "pierolocorp_logo.png",
    ASSET_DIR / "pierolooscorp_logo.png",
]

LOGO_PATH = next(
    (path for path in LOGO_CANDIDATES if path.exists()),
    None,
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# 2. ASSET LOADING
# ============================================================

@st.cache_data(show_spinner=False)
def load_background() -> str:
    """
    Convert the supplied SVG background into a base64 data URI.
    """
    if not BACKGROUND_PATH.exists():
        return ""

    encoded = base64.b64encode(
        BACKGROUND_PATH.read_bytes()
    ).decode("utf-8")

    return f"data:image/svg+xml;base64,{encoded}"


BACKGROUND_URI = load_background()

BACKGROUND_EXISTS = BACKGROUND_PATH.exists()
LOGO_EXISTS = LOGO_PATH is not None


@st.cache_data(show_spinner=False)
def load_image_data_uri(path_string: str) -> str:
    """Return a local image as a browser-safe data URI."""
    path = Path(path_string)
    if not path.exists() or not path.is_file():
        return ""

    suffix = path.suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }
    mime = mime_types.get(suffix)
    if not mime:
        return ""

    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def asset_exists(path: Path) -> bool:
    return (
        path.exists()
        and path.is_file()
        and path.stat().st_size > 100
    )


# Additional page-specific visual assets.
# This registry MUST be defined before PAGE_ASSET_STATUS because
# the status map is built from these paths.
PAGE_BANNER_CANDIDATES = {
    "Command Center": ASSET_DIR / "pieroloos_command_center.png",
    "Client Intake": ASSET_DIR / "pieroloos_client_intake.png",
    "Business Profile": ASSET_DIR / "pieroloos_business_profile.png",
    "Jurisdiction Lens": ASSET_DIR / "pieroloos_jurisdiction.png",
    "Formation Roadmap": ASSET_DIR / "pieroloos_formation.png",
    "Compliance": ASSET_DIR / "pieroloos_compliance.png",
    "Report Generator": ASSET_DIR / "pieroloos_reports.png",
    "Engagement Records": ASSET_DIR / "pieroloos_engagements.png",
}


# Evaluate asset availability only after the banner registry exists.
PAGE_ASSET_STATUS = {
    name: asset_exists(path)
    for name, path in PAGE_BANNER_CANDIDATES.items()
}


PAGE_BANNER_WIDTH = 1600


# ============================================================
# 2A. CRITICAL BOOT LOGO — RENDER BEFORE DATABASE INITIALISATION
# ============================================================
#
# This is intentionally placed before SQLite migration/start-up work.
# Streamlit can send these early UI deltas while the remaining Python
# application continues initialising. The logo therefore becomes the
# first meaningful visual element instead of waiting for the database
# layer to finish.
#
# The full visual system is injected later by inject_styles().
# These styles are deliberately self-contained so the boot experience
# does not depend on the later application stylesheet.
#

def render_critical_boot_logo() -> None:
    """Render the logo immediately, before slow application initialisation."""

    if st.session_state.get("pieroloos_boot_seen", False):
        return

    st.session_state["pieroloos_boot_seen"] = True

    if LOGO_EXISTS:
        logo_uri = load_image_data_uri(str(LOGO_PATH))
        logo_markup = (
            f"""
            <div class="pieroloos-critical-logo-frame">
                <img
                    class="pieroloos-critical-logo"
                    src="{logo_uri}"
                    alt="PieroloCorp International LLC"
                />
            </div>
            """
            if logo_uri
            else
            """
            <div class="pieroloos-critical-logo-fallback">
                PIEROLOOS
            </div>
            """
        )
    else:
        logo_markup = """
        <div class="pieroloos-critical-logo-fallback">
            PIEROLOOS
        </div>
        """

    st.markdown(
        f"""
        <style>
        .pieroloos-critical-boot {{
            position: fixed;
            inset: 0;
            z-index: 2147483647;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            background:
                radial-gradient(
                    circle at 50% 50%,
                    rgba(155,108,255,0.20),
                    transparent 24%
                ),
                radial-gradient(
                    circle at 50% 50%,
                    rgba(98,217,255,0.07),
                    transparent 40%
                ),
                linear-gradient(
                    135deg,
                    #02020b 0%,
                    #08051c 48%,
                    #03030d 100%
                );
            pointer-events: none;
            animation:
                pieroloos-critical-boot-exit
                800ms
                cubic-bezier(.22,.61,.36,1)
                7200ms
                forwards;
        }}

        .pieroloos-critical-boot::before {{
            content: "";
            position: absolute;
            width: min(520px, 92vw);
            height: min(520px, 92vw);
            border: 1px solid rgba(155,108,255,0.16);
            border-radius: 50%;
            box-shadow:
                0 0 80px rgba(155,108,255,0.10),
                inset 0 0 70px rgba(98,217,255,0.035);
            animation: pieroloos-critical-orbit 7s linear infinite;
        }}

        .pieroloos-critical-boot::after {{
            content: "";
            position: absolute;
            width: min(330px, 66vw);
            height: min(330px, 66vw);
            border: 1px solid rgba(215,180,90,0.18);
            border-radius: 50%;
            transform: rotate(22deg) scaleX(1.55);
            box-shadow: 0 0 38px rgba(215,180,90,0.055);
            animation: pieroloos-critical-orbit-reverse 5s linear infinite;
        }}

        .pieroloos-critical-core {{
            position: relative;
            z-index: 3;
            width: min(250px, 62vw);
            height: min(250px, 62vw);
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .pieroloos-critical-logo-frame {{
            position: relative;
            z-index: 4;
            width: min(168px, 43vw);
            height: min(168px, 43vw);
            border-radius: 50%;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            background:
                radial-gradient(
                    circle at 35% 30%,
                    rgba(255,255,255,0.10),
                    rgba(12,8,34,0.92) 62%
                );
            border: 2px solid rgba(244,220,145,0.72);
            box-shadow:
                0 0 0 6px rgba(155,108,255,0.055),
                0 0 30px rgba(215,180,90,0.24),
                0 0 70px rgba(155,108,255,0.22),
                inset 0 0 26px rgba(98,217,255,0.08);
            animation:
                pieroloos-critical-logo-in 650ms ease-out both,
                pieroloos-critical-frame-advert 2.8s ease-in-out 650ms infinite;
        }}

        .pieroloos-critical-logo-frame::before {{
            content: "";
            position: absolute;
            inset: 6px;
            border: 1px solid rgba(98,217,255,0.32);
            border-radius: 50%;
            pointer-events: none;
        }}

        .pieroloos-critical-logo {{
            position: relative;
            z-index: 1;
            width: 100%;
            height: 100%;
            display: block;
            object-fit: cover;
            object-position: center;
            border-radius: 50%;
            clip-path: circle(50% at 50% 50%);
            transform: scale(1.02);
            animation: pieroloos-critical-logo-motion 3.2s ease-in-out 650ms infinite;
            will-change: transform, filter;
        }}

        .pieroloos-critical-logo-frame::after {{
            content: "";
            position: absolute;
            z-index: 2;
            top: -20%;
            left: -75%;
            width: 45%;
            height: 140%;
            transform: rotate(22deg);
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.26), transparent);
            filter: blur(2px);
            pointer-events: none;
            animation: pieroloos-critical-logo-shine 3.6s ease-in-out 900ms infinite;
        }}

        .pieroloos-critical-logo-fallback {{
            position: relative;
            z-index: 4;
            width: min(168px, 43vw);
            height: min(168px, 43vw);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
            border: 2px solid rgba(244,220,145,0.72);
            background: rgba(12,8,34,0.94);
            color: #f4dc91;
            font-size: clamp(1rem, 4vw, 1.65rem);
            font-weight: 900;
            letter-spacing: 0.14em;
            text-align: center;
            box-shadow:
                0 0 32px rgba(215,180,90,0.20),
                0 0 70px rgba(155,108,255,0.20);
        }}

        .pieroloos-critical-label {{
            position: absolute;
            z-index: 5;
            left: 50%;
            bottom: -5.25rem;
            transform: translateX(-50%);
            white-space: nowrap;
            color: rgba(230,221,248,0.78);
            font-size: 0.60rem;
            font-weight: 750;
            letter-spacing: 0.28em;
            text-transform: uppercase;
        }}

        .pieroloos-critical-progress {{
            position: absolute;
            z-index: 5;
            left: 50%;
            bottom: -6.45rem;
            width: min(180px, 48vw);
            height: 2px;
            transform: translateX(-50%);
            overflow: hidden;
            border-radius: 99px;
            background: rgba(155,108,255,0.14);
        }}

        .pieroloos-critical-progress::after {{
            content: "";
            display: block;
            width: 42%;
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(
                90deg,
                #62d9ff,
                #9b6cff,
                #f4dc91
            );
            box-shadow: 0 0 12px rgba(155,108,255,0.42);
            animation:
                pieroloos-critical-progress
                7600ms
                linear
                150ms
                forwards;
        }}

        @keyframes pieroloos-critical-logo-in {{
            from {{
                opacity: 0;
                transform: scale(0.72);
            }}
            to {{
                opacity: 1;
                transform: scale(1);
            }}
        }}

        @keyframes pieroloos-critical-frame-advert {{
            0%, 100% {{
                transform: translateY(0) scale(1);
                box-shadow:
                    0 0 0 6px rgba(155,108,255,0.055),
                    0 0 30px rgba(215,180,90,0.24),
                    0 0 70px rgba(155,108,255,0.22),
                    inset 0 0 26px rgba(98,217,255,0.08);
            }}
            50% {{
                transform: translateY(-7px) scale(1.035);
                box-shadow:
                    0 0 0 10px rgba(155,108,255,0.075),
                    0 0 44px rgba(215,180,90,0.34),
                    0 0 95px rgba(155,108,255,0.30),
                    inset 0 0 34px rgba(98,217,255,0.13);
            }}
        }}

        @keyframes pieroloos-critical-logo-motion {{
            0%, 100% {{
                transform: scale(1.02) rotate(-1.2deg);
                filter: brightness(0.98) saturate(1);
            }}
            50% {{
                transform: scale(1.055) rotate(1.2deg);
                filter: brightness(1.10) saturate(1.08);
            }}
        }}

        @keyframes pieroloos-critical-logo-shine {{
            0% {{
                left: -75%;
                opacity: 0;
            }}
            18% {{
                opacity: 0.85;
            }}
            42% {{
                left: 135%;
                opacity: 0;
            }}
            100% {{
                left: 135%;
                opacity: 0;
            }}
        }}

        @keyframes pieroloos-critical-orbit {{
            from {{
                transform: rotate(0deg);
            }}
            to {{
                transform: rotate(360deg);
            }}
        }}

        @keyframes pieroloos-critical-orbit-reverse {{
            from {{
                transform: rotate(22deg) scaleX(1.55);
            }}
            to {{
                transform: rotate(-338deg) scaleX(1.55);
            }}
        }}

        @keyframes pieroloos-critical-progress {{
            from {{
                transform: translateX(-120%);
            }}
            to {{
                transform: translateX(280%);
            }}
        }}

        @keyframes pieroloos-critical-boot-exit {{
            0% {{
                opacity: 1;
                visibility: visible;
            }}
            90% {{
                opacity: 1;
                visibility: visible;
            }}
            100% {{
                opacity: 0;
                visibility: hidden;
            }}
        }}

        @media (prefers-reduced-motion: reduce) {{
            .pieroloos-critical-boot {{
                animation-duration: 1ms !important;
                animation-delay: 650ms !important;
            }}

            .pieroloos-critical-boot::before,
            .pieroloos-critical-boot::after,
            .pieroloos-critical-logo-frame,
            .pieroloos-critical-logo,
            .pieroloos-critical-logo-frame::after,
            .pieroloos-critical-progress::after {{
                animation: none !important;
            }}
        }}
        </style>

        <div
            class="pieroloos-critical-boot"
            aria-label="PieroloCorp International LLC initializing"
        >
            <div class="pieroloos-critical-core">
                {logo_markup}
                <div class="pieroloos-critical-label">
                    PIEROLOOS · OFFICIAL IDENTITY · INITIALIZING
                </div>
                <div class="pieroloos-critical-progress"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# CRITICAL ORDER:
# The logo is emitted before SQLite/database migration begins.
render_critical_boot_logo()


# ============================================================
# 3. DATABASE
# ============================================================

def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(
        str(DB_PATH),
        check_same_thread=False,
    )

    connection.row_factory = sqlite3.Row

    return connection


DATABASE_SCHEMA_VERSION = 2


def _create_canonical_tables(cursor: sqlite3.Cursor) -> None:
    """Create the current PieroloOS database schema."""

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            country TEXT,
            business_name TEXT,
            business_type TEXT,
            service TEXT,
            status TEXT DEFAULT 'New',
            notes TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            report_type TEXT,
            content TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS engagements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            service TEXT,
            status TEXT DEFAULT 'Open',
            next_action TEXT,
            notes TEXT,
            updated_at TEXT NOT NULL
        )
        """
    )


def _table_columns(
    cursor: sqlite3.Cursor,
    table_name: str,
) -> list[str]:
    return [
        row[1]
        for row in cursor.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()
    ]


def _rebuild_table(
    cursor: sqlite3.Cursor,
    table_name: str,
    columns: list[str],
) -> None:
    """
    Rebuild a table using the canonical schema while preserving
    all data that can be mapped into the current schema.

    This handles legacy tables that contain additional NOT NULL
    columns which would otherwise make INSERT statements fail.
    """

    existing = _table_columns(cursor, table_name)

    temporary_name = f"{table_name}__migration"

    cursor.execute(
        f"DROP TABLE IF EXISTS {temporary_name}"
    )

    if table_name == "clients":

        cursor.execute(
            f"""
            CREATE TABLE {temporary_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                country TEXT,
                business_name TEXT,
                business_type TEXT,
                service TEXT,
                status TEXT DEFAULT 'New',
                notes TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

    elif table_name == "reports":

        cursor.execute(
            f"""
            CREATE TABLE {temporary_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT,
                report_type TEXT,
                content TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

    elif table_name == "engagements":

        cursor.execute(
            f"""
            CREATE TABLE {temporary_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT,
                service TEXT,
                status TEXT DEFAULT 'Open',
                next_action TEXT,
                notes TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )

    else:
        return

    available = [
        column
        for column in columns
        if column in existing
    ]

    if available:
        target_sql = ", ".join(available)
        source_expressions = []

        for column in available:
            if column == "client_name":
                source_expressions.append(
                    "COALESCE(client_name, 'Migrated Client')"
                )
            elif column in {"created_at", "updated_at"}:
                source_expressions.append(
                    f"COALESCE({column}, datetime('now'))"
                )
            else:
                source_expressions.append(column)

        source_sql = ", ".join(source_expressions)

        # Required fields that did not exist in the legacy table.
        missing_required = []

        if "client_name" in columns and "client_name" not in existing:
            missing_required.append("client_name")

        if "created_at" in columns and "created_at" not in existing:
            missing_required.append("created_at")

        if "updated_at" in columns and "updated_at" not in existing:
            missing_required.append("updated_at")

        if missing_required:
            target_sql = ", ".join(
                available + missing_required
            )

            for column in missing_required:
                if column == "client_name":
                    source_expressions.append(
                        "'Migrated Client'"
                    )
                else:
                    source_expressions.append(
                        "datetime('now')"
                    )

            source_sql = ", ".join(source_expressions)

        cursor.execute(
            f"""
            INSERT INTO {temporary_name}
            ({target_sql})
            SELECT {source_sql}
            FROM {table_name}
            """
        )

    cursor.execute(
        f"DROP TABLE {table_name}"
    )

    cursor.execute(
        f"ALTER TABLE {temporary_name} RENAME TO {table_name}"
    )


def initialize_database() -> None:
    """
    Initialise and migrate the PieroloOS SQLite database.

    Version 2 uses canonical table schemas. Legacy tables are rebuilt
    when necessary so old required columns cannot break new INSERTs.
    Existing data in matching columns is preserved.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pieroloos_schema (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL
        )
        """
    )

    schema_row = cursor.execute(
        """
        SELECT version
        FROM pieroloos_schema
        WHERE id = 1
        """
    ).fetchone()

    current_version = (
        int(schema_row[0])
        if schema_row is not None
        else 0
    )

    if current_version < DATABASE_SCHEMA_VERSION:

        # Create missing tables first so the migration logic can
        # inspect them safely.
        _create_canonical_tables(cursor)

        canonical_columns = {
            "clients": [
                "id",
                "client_name",
                "email",
                "phone",
                "country",
                "business_name",
                "business_type",
                "service",
                "status",
                "notes",
                "created_at",
            ],
            "reports": [
                "id",
                "client_name",
                "report_type",
                "content",
                "created_at",
            ],
            "engagements": [
                "id",
                "client_name",
                "service",
                "status",
                "next_action",
                "notes",
                "updated_at",
            ],
        }

        for table_name, columns in canonical_columns.items():

            existing_columns = _table_columns(
                cursor,
                table_name,
            )

            if existing_columns != columns:
                _rebuild_table(
                    cursor,
                    table_name,
                    columns,
                )

        cursor.execute(
            """
            INSERT INTO pieroloos_schema (id, version)
            VALUES (1, ?)
            ON CONFLICT(id)
            DO UPDATE SET version = excluded.version
            """,
            (DATABASE_SCHEMA_VERSION,),
        )

    else:
        # Safety check in case a table was removed or damaged after
        # the migration was recorded.
        _create_canonical_tables(cursor)

    connection.commit()
    connection.close()


initialize_database()


# ============================================================
# 4. DATABASE FUNCTIONS
# ============================================================

def execute_write(
    query: str,
    params: tuple = (),
) -> None:

    connection = get_connection()

    try:
        connection.execute(query, params)
        connection.commit()
    except sqlite3.Error as exc:
        connection.rollback()
        raise RuntimeError(f"Database operation failed: {exc}") from exc
    finally:
        connection.close()


def fetch_all(
    query: str,
    params: tuple = (),
) -> list[sqlite3.Row]:

    connection = get_connection()

    rows = connection.execute(
        query,
        params,
    ).fetchall()

    connection.close()

    return rows


def fetch_one(
    query: str,
    params: tuple = (),
) -> Optional[sqlite3.Row]:

    connection = get_connection()

    row = connection.execute(
        query,
        params,
    ).fetchone()

    connection.close()

    return row


def count_records(
    table: str,
) -> int:

    allowed = {
        "clients",
        "reports",
        "engagements",
    }

    if table not in allowed:
        return 0

    row = fetch_one(
        f"SELECT COUNT(*) AS total FROM {table}"
    )

    if row is None:
        return 0

    return int(row["total"])


def current_timestamp() -> str:

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def safe_filename(value: str) -> str:

    result = ""

    for character in value:

        if (
            character.isalnum()
            or character in "-_"
        ):
            result += character

        else:
            result += "_"

    result = result.strip("_")

    return result or "report"


# ============================================================
# 5. JURISDICTION DATA
# ============================================================

JURISDICTIONS = [
    {
        "jurisdiction": "United States — New Mexico",
        "country": "United States",
        "formation_complexity": 2,
        "cost": 2,
        "remote_friendliness": 5,
        "international_fit": 4,
        "banking_payment_fit": 5,
        "compliance_complexity": 3,
        "privacy": 4,
        "summary": (
            "Flexible U.S. LLC jurisdiction commonly considered "
            "by remote founders."
        ),
        "source": (
            "New Mexico Secretary of State / IRS / FinCEN"
        ),
    },
    {
        "jurisdiction": "United States — Delaware",
        "country": "United States",
        "formation_complexity": 3,
        "cost": 3,
        "remote_friendliness": 5,
        "international_fit": 5,
        "banking_payment_fit": 5,
        "compliance_complexity": 4,
        "privacy": 3,
        "summary": (
            "Major U.S. corporate jurisdiction with extensive "
            "business-law infrastructure."
        ),
        "source": (
            "Delaware Division of Corporations / IRS / FinCEN"
        ),
    },
    {
        "jurisdiction": "United Kingdom",
        "country": "United Kingdom",
        "formation_complexity": 2,
        "cost": 3,
        "remote_friendliness": 4,
        "international_fit": 5,
        "banking_payment_fit": 4,
        "compliance_complexity": 4,
        "privacy": 3,
        "summary": (
            "Established international business environment "
            "with strong corporate infrastructure."
        ),
        "source": "Companies House / HMRC",
    },
    {
        "jurisdiction": "Nigeria",
        "country": "Nigeria",
        "formation_complexity": 3,
        "cost": 2,
        "remote_friendliness": 3,
        "international_fit": 3,
        "banking_payment_fit": 3,
        "compliance_complexity": 4,
        "privacy": 2,
        "summary": (
            "Relevant for businesses operating locally and "
            "serving the Nigerian market."
        ),
        "source": "CAC / FIRS / relevant Nigerian authorities",
    },
]



def render_page_banner(page_name: str) -> None:
    """Render a page-specific graphical banner only.

    Page titles and descriptive text are intentionally NOT rendered
    inside the banner. Each page's Streamlit H1 below the banner is
    the authoritative page heading.
    """
    banner_path = PAGE_BANNER_CANDIDATES.get(page_name)

    if banner_path and asset_exists(banner_path):
        image_uri = load_image_data_uri(str(banner_path))

        if image_uri:
            st.markdown(
                f"""
                <section class="page-banner" aria-label="{page_name} graphical banner">
                    <img
                        class="page-banner-image"
                        src="{image_uri}"
                        alt=""
                    />
                    <div class="page-banner-overlay"></div>
                </section>
                """,
                unsafe_allow_html=True,
            )
            return

    # Keep a graphical fallback so the page layout remains stable when
    # an asset is unavailable. The missing asset message is intentionally
    # omitted from the visible banner; the sidebar System Status provides
    # asset diagnostics.
    st.markdown(
        """
        <section class="page-banner page-banner-fallback" aria-label="Graphical banner">
            <div class="page-banner-fallback-glow"></div>
        </section>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 6. VISUAL DESIGN
# ============================================================

def inject_styles() -> None:
    """Inject the full PieroloOS cosmic visual environment.

    The existing page structure remains unchanged. This layer extends the
    visual system from the static page banners to the entire application:
    deep-space gradients, subtle star fields, orbital rings, global glow,
    translucent work surfaces, and responsive behavior.
    """
    if BACKGROUND_URI:
        background_css = (
            "background-image: "
            "linear-gradient(rgba(4,5,20,0.62), rgba(5,4,22,0.78)), "
            f"url('{BACKGROUND_URI}');"
        )
    else:
        background_css = (
            "background-image: "
            "radial-gradient(circle at 15% 15%, rgba(155,108,255,0.24), transparent 28%), "
            "radial-gradient(circle at 82% 18%, rgba(68,164,255,0.18), transparent 25%), "
            "radial-gradient(circle at 50% 90%, rgba(215,180,90,0.12), transparent 30%), "
            "linear-gradient(135deg, #03030d, #0b0922 45%, #03030d);"
        )

    css = """
    <style>
    :root {
        --gold: #d7b45a;
        --gold-light: #f4dc91;
        --violet: #9b6cff;
        --violet-light: #cbb5ff;
        --cyan: #62d9ff;
        --blue: #4e8cff;
        --navy: #03030d;
        --panel: rgba(10, 8, 29, 0.68);
        --panel-strong: rgba(8, 7, 24, 0.84);
        --border: rgba(215, 180, 90, 0.20);
        --text: #f6f3ff;
        --muted: #aaa3c2;
    }

    /* ========================================================
       GLOBAL COSMIC ENVIRONMENT
       ======================================================== */

    html, body {
        background: #03030d !important;
    }

    html, body, #root {
        margin: 0 !important;
        padding: 0 !important;
        min-height: 0 !important;
        height: 100% !important;
        overflow-x: hidden !important;
    }

    .stApp {
        position: relative;
        isolation: isolate;
        min-height: 0 !important;
        height: auto !important;
        BACKGROUND_CSS_PLACEHOLDER
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: var(--text);
        overflow: visible !important;
    }

    /* Deep-space colour field + stars across the entire application. */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        background:
            radial-gradient(circle at 12% 18%, rgba(155,108,255,0.22), transparent 23%),
            radial-gradient(circle at 86% 14%, rgba(72,166,255,0.17), transparent 24%),
            radial-gradient(circle at 68% 78%, rgba(215,180,90,0.11), transparent 22%),
            radial-gradient(circle at 32% 92%, rgba(112,77,255,0.14), transparent 26%),
            radial-gradient(circle at 18% 65%, rgba(0,210,255,0.07), transparent 18%),
            radial-gradient(circle at 78% 48%, rgba(255,255,255,0.055) 0 1px, transparent 1.5px),
            radial-gradient(circle at 24% 34%, rgba(255,255,255,0.07) 0 1px, transparent 1.6px),
            radial-gradient(circle at 58% 24%, rgba(255,255,255,0.055) 0 1px, transparent 1.5px),
            radial-gradient(circle at 42% 74%, rgba(255,255,255,0.06) 0 1px, transparent 1.5px),
            linear-gradient(135deg, rgba(3,3,13,0.18), rgba(12,8,35,0.16));
        background-size: auto, auto, auto, auto, auto, 360px 360px, 290px 290px, 420px 420px, 330px 330px, auto;
        animation: cosmicDrift 28s ease-in-out infinite alternate;
    }

    /* Large orbital geometry creates the global-presence effect. */
    .stApp::after {
        content: "";
        position: fixed;
        width: min(1100px, 92vw);
        height: min(1100px, 92vw);
        left: 50%;
        top: 48%;
        transform: translate(-50%, -50%) rotate(-18deg);
        border: 1px solid rgba(155,108,255,0.15);
        border-radius: 50%;
        box-shadow:
            0 0 80px rgba(155,108,255,0.055),
            inset 0 0 80px rgba(98,217,255,0.035);
        z-index: 0;
        pointer-events: none;
        animation: orbitFloat 32s linear infinite;
    }

    /* Keep Streamlit's real application surfaces above the cosmic layers. */
    .stApp > * {
        position: relative;
        z-index: 1;
    }

    @keyframes cosmicDrift {
        from { transform: scale(1); filter: saturate(0.95); }
        to { transform: scale(1.035); filter: saturate(1.12); }
    }

    @keyframes orbitFloat {
        from { transform: translate(-50%, -50%) rotate(-18deg); }
        to { transform: translate(-50%, -50%) rotate(342deg); }
    }

    /* Additional orbital tracks on the main workspace. */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        width: min(760px, 74vw);
        height: min(330px, 32vw);
        left: 50%;
        top: 52%;
        transform: translate(-50%, -50%) rotate(-13deg);
        border: 1px solid rgba(98,217,255,0.12);
        border-radius: 50%;
        box-shadow: 0 0 45px rgba(98,217,255,0.035);
        z-index: 0;
        pointer-events: none;
        animation: orbitTilt 24s linear infinite reverse;
    }

    [data-testid="stAppViewContainer"]::after {
        content: "";
        position: fixed;
        width: min(500px, 55vw);
        height: min(500px, 55vw);
        left: 88%;
        top: 17%;
        transform: translate(-50%, -50%);
        border: 1px solid rgba(215,180,90,0.11);
        border-radius: 50%;
        box-shadow: 0 0 65px rgba(215,180,90,0.045);
        z-index: 0;
        pointer-events: none;
        animation: orbitPulse 8s ease-in-out infinite alternate;
    }

    @keyframes orbitTilt {
        from { transform: translate(-50%, -50%) rotate(-13deg); }
        to { transform: translate(-50%, -50%) rotate(347deg); }
    }

    @keyframes orbitPulse {
        from { opacity: 0.42; transform: translate(-50%, -50%) scale(0.96); }
        to { opacity: 0.9; transform: translate(-50%, -50%) scale(1.04); }
    }

    /* ========================================================
       SIDEBAR / NAVIGATION
       ======================================================== */

    [data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 50% 12%, rgba(155,108,255,0.18), transparent 30%),
            radial-gradient(circle at 20% 82%, rgba(98,217,255,0.07), transparent 24%),
            linear-gradient(180deg, rgba(4,4,17,0.94), rgba(8,5,25,0.97));
        border-right: 1px solid rgba(215,180,90,0.22);
        box-shadow: 14px 0 55px rgba(0,0,0,0.28);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }

    [data-testid="stSidebar"]::before {
        content: "";
        position: absolute;
        inset: 0;
        pointer-events: none;
        background:
            radial-gradient(circle at 78% 20%, rgba(98,217,255,0.08), transparent 18%),
            radial-gradient(circle at 28% 65%, rgba(155,108,255,0.08), transparent 22%);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.25rem !important;
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }

    [data-testid="stMain"],
    [data-testid="stAppViewContainer"] {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }

    [data-testid="stAppViewContainer"] {
        min-height: 100vh !important;
        height: 100vh !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        scroll-padding-bottom: 0 !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }

    [data-testid="stAppViewContainer"] > .main > div {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }

    /* Eliminate Streamlit's own trailing platform/footer region. */
    [data-testid="stFooter"],
    footer:not(.pieroloos-footer) {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        max-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ========================================================
       TYPOGRAPHY
       ======================================================== */

    h1 {
        color: var(--gold-light);
        text-shadow: 0 0 24px rgba(215,180,90,0.12);
    }

    h2 { color: #f6f0ff; }
    h3 { color: #f1eaff; }
    p { color: #d8d1e8; }
    .stCaption { color: #aaa3c2; }

    /* ========================================================
       TRANSLUCENT APPLICATION SURFACES
       ======================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(145deg, rgba(15,11,38,0.66), rgba(7,6,22,0.54));
        border-color: rgba(155,108,255,0.17) !important;
        box-shadow: 0 16px 45px rgba(0,0,0,0.16);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }

    div[data-testid="stMetric"] {
        background:
            linear-gradient(145deg, rgba(18,13,43,0.76), rgba(7,7,24,0.68));
        border: 1px solid rgba(215,180,90,0.20);
        border-radius: 18px;
        padding: 1rem;
        box-shadow: 0 14px 40px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.025);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
    }

    div[data-testid="stMetricLabel"] { color: #aaa3c2; }
    div[data-testid="stMetricValue"] { color: #f1d98a; }

    [data-testid="stExpander"] {
        background: rgba(10,8,29,0.62);
        border: 1px solid rgba(155,108,255,0.18);
        border-radius: 15px;
        box-shadow: 0 14px 38px rgba(0,0,0,0.14);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }

    /* Inputs remain readable while allowing the cosmic environment to show through. */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] {
        background: rgba(9,8,27,0.72) !important;
        border-color: rgba(155,108,255,0.20) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    input, textarea {
        color: #f6f3ff !important;
    }

    /* ========================================================
       BUTTONS / INTERACTION
       ======================================================== */

    div[data-testid="stButton"] > button,
    div[data-testid="stFormSubmitButton"] > button {
        border: 1px solid rgba(215,180,90,0.27);
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(20,14,47,0.88), rgba(10,8,28,0.88));
        color: #f4edff;
        font-weight: 700;
        box-shadow: 0 8px 22px rgba(0,0,0,0.16);
        transition: all 180ms ease;
    }

    div[data-testid="stButton"] > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        border-color: rgba(215,180,90,0.72);
        color: #f1d98a;
        box-shadow: 0 0 24px rgba(215,180,90,0.10);
        transform: translateY(-1px);
    }

    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 12px 32px rgba(0,0,0,0.16);
    }

    /* ========================================================
       PROFESSIONAL COSMIC CONTENT SYSTEM
       ======================================================== */

    /* High-contrast body copy */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stText"],
    .stWrite,
    .stCaption {
        color: #ded8ef !important;
    }

    .stCaption {
        color: #b9afd3 !important;
    }

    /* Section headings use a gold/violet/cyan hierarchy. */
    h1 {
        color: #f6dc91 !important;
        letter-spacing: -0.025em;
        text-shadow:
            0 0 18px rgba(215,180,90,0.18),
            0 0 38px rgba(155,108,255,0.10);
    }

    h2 {
        color: #d9c5ff !important;
        text-shadow: 0 0 18px rgba(155,108,255,0.12);
    }

    h3 {
        color: #70ddff !important;
        text-shadow: 0 0 15px rgba(98,217,255,0.12);
    }

    /* Content cards: layered cosmic glass with gold/violet/cyan edge. */
    [data-testid="stVerticalBlockBorderWrapper"] {
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(circle at 100% 0%, rgba(155,108,255,0.12), transparent 34%),
            radial-gradient(circle at 0% 100%, rgba(98,217,255,0.075), transparent 32%),
            linear-gradient(145deg, rgba(19,13,48,0.82), rgba(6,6,24,0.72)) !important;
        border: 1px solid rgba(155,108,255,0.24) !important;
        border-radius: 18px !important;
        box-shadow:
            0 16px 42px rgba(0,0,0,0.22),
            inset 0 1px 0 rgba(255,255,255,0.035);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }

    [data-testid="stVerticalBlockBorderWrapper"]::before {
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        top: 0;
        height: 3px;
        background: linear-gradient(90deg, #62d9ff, #9b6cff, #d7b45a);
        opacity: 0.78;
        pointer-events: none;
    }

    /* Alternate card accents across the workspace. */
    [data-testid="stVerticalBlockBorderWrapper"]:nth-of-type(3n+1)::before {
        background: linear-gradient(90deg, #62d9ff, #4e8cff);
    }

    [data-testid="stVerticalBlockBorderWrapper"]:nth-of-type(3n+2)::before {
        background: linear-gradient(90deg, #9b6cff, #d76cff);
    }

    [data-testid="stVerticalBlockBorderWrapper"]:nth-of-type(3n)::before {
        background: linear-gradient(90deg, #d7b45a, #f4dc91, #9b6cff);
    }

    [data-testid="stVerticalBlockBorderWrapper"] h3 {
        color: #f3dc92 !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] strong {
        color: #e7d0ff !important;
    }

    /* Workflow labels / numbered content. */
    [data-testid="stMarkdownContainer"] strong {
        color: #f0d787 !important;
    }

    /* Status/info surfaces become part of the cosmic palette. */
    [data-testid="stAlert"] {
        background: rgba(13,10,35,0.72) !important;
        border-radius: 14px !important;
        backdrop-filter: blur(12px);
    }

    /* Inputs, selects and textareas: readable, luminous, restrained. */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] {
        background: rgba(8,7,27,0.80) !important;
        border-color: rgba(155,108,255,0.28) !important;
        box-shadow: inset 0 0 0 1px rgba(98,217,255,0.025);
    }

    label,
    [data-testid="stWidgetLabel"] p {
        color: #cbb9ee !important;
        font-weight: 650 !important;
    }

    input, textarea {
        color: #f7f4ff !important;
        caret-color: #f1d98a !important;
    }

    /* ========================================================
       COSMIC ACTION BUTTON SYSTEM
       ======================================================== */

    div[data-testid="stButton"] > button,
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stDownloadButton"] > button {
        min-height: 44px;
        border: 1px solid rgba(215,180,90,0.34) !important;
        border-radius: 13px !important;
        background:
            linear-gradient(135deg, rgba(32,19,70,0.94), rgba(10,8,30,0.94)) !important;
        color: #f8f3ff !important;
        font-weight: 750 !important;
        letter-spacing: 0.01em;
        box-shadow:
            0 8px 24px rgba(0,0,0,0.20),
            inset 0 1px 0 rgba(255,255,255,0.035);
        transition:
            transform 160ms ease,
            border-color 160ms ease,
            box-shadow 160ms ease,
            color 160ms ease;
    }

    div[data-testid="stButton"] > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-1px);
        border-color: rgba(244,220,145,0.82) !important;
        color: #f7dd8f !important;
        box-shadow:
            0 0 28px rgba(155,108,255,0.13),
            0 10px 26px rgba(0,0,0,0.24);
    }

    /* Distinct button families by position create a richer visual package. */
    div[data-testid="stButton"]:nth-of-type(3n+1) > button {
        background: linear-gradient(135deg, rgba(18,54,78,0.94), rgba(8,20,42,0.94)) !important;
        border-color: rgba(98,217,255,0.38) !important;
    }

    div[data-testid="stButton"]:nth-of-type(3n+2) > button {
        background: linear-gradient(135deg, rgba(52,24,84,0.94), rgba(17,9,43,0.94)) !important;
        border-color: rgba(155,108,255,0.40) !important;
    }

    div[data-testid="stButton"]:nth-of-type(3n) > button {
        background: linear-gradient(135deg, rgba(71,53,20,0.94), rgba(27,19,10,0.94)) !important;
        border-color: rgba(215,180,90,0.42) !important;
    }

    /* Data/table text */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(155,108,255,0.20);
        border-radius: 14px;
        box-shadow: 0 14px 35px rgba(0,0,0,0.18);
        overflow: hidden;
    }

    /* Expander headers get a distinct cosmic treatment. */
    [data-testid="stExpander"] {
        background:
            linear-gradient(145deg, rgba(15,11,38,0.80), rgba(7,6,23,0.70)) !important;
        border: 1px solid rgba(155,108,255,0.23) !important;
        border-radius: 15px !important;
    }

    [data-testid="stExpander"] summary {
        color: #e4d3ff !important;
        font-weight: 700 !important;
    }

    /* ========================================================
       PAGE-SPECIFIC BANNERS
       ======================================================== */


    .page-banner {
        position: relative;
        width: 100%;
        min-height: 290px;
        margin: 0 0 1.5rem 0;
        overflow: hidden;
        border-radius: 24px;
        border: 1px solid rgba(215,180,90,0.28);
        background: rgba(8,7,24,0.72);
        box-shadow:
            0 24px 70px rgba(0,0,0,0.35),
            0 0 55px rgba(155,108,255,0.055);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }

    .page-banner-image {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }

    .page-banner-overlay {
        position: absolute;
        inset: 0;
        background:
            linear-gradient(90deg, rgba(5,5,18,0.18), rgba(5,5,18,0.03) 52%, rgba(5,5,18,0.18)),
            radial-gradient(circle at 72% 50%, rgba(155,108,255,0.08), transparent 32%);
        pointer-events: none;
    }

    .page-banner-fallback {
        background:
            radial-gradient(circle at 80% 20%, rgba(155,108,255,0.28), transparent 34%),
            radial-gradient(circle at 20% 80%, rgba(98,217,255,0.10), transparent 25%),
            radial-gradient(circle at 55% 45%, rgba(215,180,90,0.10), transparent 24%),
            linear-gradient(135deg, #090718, #17102e, #050512);
    }

    .page-banner-fallback-glow {
        position: absolute;
        inset: 0;
        background:
            radial-gradient(ellipse at center, transparent 0 32%, rgba(155,108,255,0.08) 50%, transparent 70%),
            linear-gradient(115deg, transparent 0%, rgba(255,255,255,0.03) 45%, transparent 70%);
        animation: bannerGlow 7s ease-in-out infinite alternate;
    }

    @keyframes bannerGlow {
        from { opacity: 0.55; transform: translateX(-1%); }
        to { opacity: 1; transform: translateX(1%); }
    }

    .asset-status {
        padding: 0.75rem 0.9rem;
        margin: 0.35rem 0;
        border-radius: 12px;
        background: rgba(12,10,31,0.72);
        border: 1px solid rgba(155,108,255,0.14);
        font-size: 0.78rem;
    }

    /* ========================================================
       TRUE APPLICATION ENDPOINT / FOOTER
       ======================================================== */

    .pieroloos-footer-spacer {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .pieroloos-footer {
        position: relative;
        width: 100%;
        margin: 1.75rem 0 0 0 !important;
        padding: 1.15rem 1rem 1.25rem 1rem !important;
        box-sizing: border-box;
        text-align: center;
        border-top: 1px solid rgba(215,180,90,0.30);
        background:
            radial-gradient(circle at 50% 0%, rgba(155,108,255,0.14), transparent 45%),
            linear-gradient(180deg, rgba(9,7,28,0.76), rgba(4,4,16,0.94));
        box-shadow:
            0 -18px 50px rgba(0,0,0,0.22),
            inset 0 1px 0 rgba(255,255,255,0.025);
        overflow: hidden;
    }

    .footer-orbit {
        position: absolute;
        width: 230px;
        height: 38px;
        left: 50%;
        top: -19px;
        transform: translateX(-50%) rotate(-7deg);
        border: 1px solid rgba(98,217,255,0.22);
        border-radius: 50%;
        box-shadow: 0 0 28px rgba(98,217,255,0.08);
        pointer-events: none;
    }

    .footer-brand {
        position: relative;
        color: #f2d98d;
        font-size: 0.90rem;
        font-weight: 850;
        letter-spacing: 0.18em;
        text-shadow: 0 0 18px rgba(215,180,90,0.16);
    }

    .footer-company {
        position: relative;
        margin-top: 0.25rem;
        color: #cdbce9;
        font-size: 0.76rem;
        font-weight: 650;
    }

    .footer-disclaimer {
        position: relative;
        max-width: 920px;
        margin: 0.45rem auto 0;
        color: #938aa9;
        font-size: 0.68rem;
        line-height: 1.45;
    }

    .pieroloos-scroll-end {
        display: block !important;
        height: 0 !important;
        min-height: 0 !important;
        max-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }

    /* No hidden tail below the final footer element. */
    .pieroloos-footer + * {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        max-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ========================================================
       MOBILE / TABLET
       ======================================================== */

    @media (max-width: 768px) {
        [data-testid="stAppViewContainer"] {
            height: 100vh !important;
            min-height: 100vh !important;
        }

        .block-container {
            padding-left: 0.85rem;
            padding-right: 0.85rem;
            padding-bottom: 0 !important;
        }

        .pieroloos-footer {
            margin-top: 1rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }

        .footer-company {
            font-size: 0.70rem;
        }

        .footer-disclaimer {
            font-size: 0.62rem;
        }

        .page-banner {
            min-height: 220px;
            border-radius: 18px;
        }

        .page-banner-overlay {
            background: linear-gradient(90deg, rgba(5,5,18,0.16), rgba(5,5,18,0.04));
        }

        .stApp::after {
            width: 720px;
            height: 720px;
            top: 44%;
        }

        [data-testid="stAppViewContainer"]::before {
            width: 520px;
            height: 230px;
        }
    }

    /* Native scrollbar remains available, but the scrollable surface is
       the application container whose content terminates at the footer. */
    [data-testid="stAppViewContainer"]::-webkit-scrollbar {
        width: 8px;
    }

    [data-testid="stAppViewContainer"]::-webkit-scrollbar-track {
        background: rgba(3,3,13,0.30);
    }

    [data-testid="stAppViewContainer"]::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, rgba(155,108,255,0.62), rgba(215,180,90,0.62));
        border-radius: 20px;
        border: 2px solid rgba(3,3,13,0.45);
    }

    [data-testid="stAppViewContainer"] {
        scrollbar-color: rgba(155,108,255,0.65) rgba(3,3,13,0.30);
        scrollbar-width: thin;
    }

    @media (prefers-reduced-motion: reduce) {
        .stApp::before,
        .stApp::after,
        [data-testid="stAppViewContainer"]::before,
        [data-testid="stAppViewContainer"]::after,
        .page-banner-fallback-glow {
            animation: none !important;
        }
    }
    </style>
    """

    st.markdown(
        css.replace("BACKGROUND_CSS_PLACEHOLDER", background_css),
        unsafe_allow_html=True,
    )


# Apply the global visual environment before rendering any application UI.
inject_styles()


# ============================================================
# 7. SIDEBAR
# ============================================================

with st.sidebar:

    # Official logo
    if LOGO_EXISTS:

        st.image(
            str(LOGO_PATH),
            width=185,
        )

    else:

        st.title(
            "PIEROLOOS"
        )

        st.caption(
            "PIEROLOCORP INTERNATIONAL LLC"
        )

    st.divider()

    st.caption(
        "PROFESSIONAL SERVICE OS · v0.1"
    )

    st.divider()

    navigation = [
        "Command Center",
        "Client Intake",
        "Business Profile",
        "Jurisdiction Lens",
        "Formation Roadmap",
        "Compliance",
        "Report Generator",
        "Engagement Records",
    ]

    page = st.radio(
        "Navigation",
        navigation,
        label_visibility="collapsed",
    )

    st.divider()

    st.caption(
        "Prepare → Analyse → Decide → Execute → Record → Improve"
    )

    with st.expander("System Status"):
        if BACKGROUND_EXISTS:
            st.success("Background loaded")
        else:
            st.warning("Background not found")

        if LOGO_EXISTS:
            st.success(f"Logo loaded: {LOGO_PATH.name}")
        else:
            st.warning("Logo not found")

        st.success("Database ready")

        banner_count = sum(
            1 for path in PAGE_BANNER_CANDIDATES.values()
            if path.exists()
        )
        if banner_count == len(PAGE_BANNER_CANDIDATES):
            st.success(f"Page visual system ready: {banner_count}/{len(PAGE_BANNER_CANDIDATES)} banners")
        else:
            st.warning(f"Page visual system: {banner_count}/{len(PAGE_BANNER_CANDIDATES)} banners")

    st.divider()

    st.caption(
        "Decision-support prototype. "
        "Not legal, tax, accounting, financial, "
        "or other licensed professional advice."
    )


# ============================================================
# 8. COMMAND CENTER
# The graphical banner is visual-only. The Streamlit H1 below is the page heading.
# ============================================================

if page == "Command Center":

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    render_page_banner(
        "Command Center",
    )

    st.title(
        "PieroloOS"
    )

    st.subheader(
        "Professional Service Operating System"
    )

    st.write(
        "A structured operating environment for "
        "PieroloCorp International LLC — combining "
        "client intake, business intelligence, "
        "jurisdiction analysis, formation planning, "
        "compliance tracking, reporting, and "
        "engagement management."
    )

    st.divider()

    # --------------------------------------------------------
    # CORE METRICS
    # --------------------------------------------------------

    st.subheader(
        "Command Center"
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:

        st.metric(
            "Clients",
            count_records("clients"),
        )

    with metric2:

        st.metric(
            "Reports",
            count_records("reports"),
        )

    with metric3:

        st.metric(
            "Engagements",
            count_records("engagements"),
        )

    with metric4:

        st.metric(
            "Jurisdictions",
            len(JURISDICTIONS),
        )

    st.divider()

    # --------------------------------------------------------
    # QUICK ACCESS
    # --------------------------------------------------------

    st.subheader(
        "Quick Access"
    )

    quick1, quick2 = st.columns(2)

    with quick1:

        with st.container(border=True):

            st.markdown(
                "### Client Intake"
            )

            st.write(
                "Capture a new client, business objective, "
                "service requirement, and engagement status."
            )

            if st.button(
                "Open Client Intake",
                key="home_client_intake",
                use_container_width=True,
            ):

                st.session_state[
                    "navigation_override"
                ] = "Client Intake"

                st.info(
                    "Select Client Intake from the sidebar."
                )

    with quick2:

        with st.container(border=True):

            st.markdown(
                "### Jurisdiction Lens"
            )

            st.write(
                "Compare selected jurisdictions using "
                "structured business criteria."
            )

            if st.button(
                "Open Jurisdiction Lens",
                key="home_jurisdiction",
                use_container_width=True,
            ):

                st.info(
                    "Select Jurisdiction Lens from the sidebar."
                )

    quick3, quick4 = st.columns(2)

    with quick3:

        with st.container(border=True):

            st.markdown(
                "### Formation Roadmap"
            )

            st.write(
                "Turn a business objective into an "
                "ordered formation and operating sequence."
            )

            if st.button(
                "Open Formation Roadmap",
                key="home_formation",
                use_container_width=True,
            ):

                st.info(
                    "Select Formation Roadmap from the sidebar."
                )

    with quick4:

        with st.container(border=True):

            st.markdown(
                "### Report Generator"
            )

            st.write(
                "Generate structured reports from "
                "stored client information."
            )

            if st.button(
                "Open Report Generator",
                key="home_report",
                use_container_width=True,
            ):

                st.info(
                    "Select Report Generator from the sidebar."
                )

    st.divider()

    # --------------------------------------------------------
    # OPERATING MODEL
    # --------------------------------------------------------

    st.subheader(
        "PieroloOS Operating Model"
    )

    st.write(
        "The MVP follows a repeatable professional-service workflow."
    )

    workflow1, workflow2, workflow3, workflow4 = st.columns(4)

    with workflow1:

        st.markdown("**01 — Intake**")

        st.caption(
            "Capture objectives, facts, requirements, and constraints."
        )

    with workflow2:

        st.markdown("**02 — Assess**")

        st.caption(
            "Structure information and evaluate available options."
        )

    with workflow3:

        st.markdown("**03 — Plan**")

        st.caption(
            "Generate formation, compliance, and execution workflows."
        )

    with workflow4:

        st.markdown("**04 — Record**")

        st.caption(
            "Preserve reports, decisions, status, and engagement history."
        )

    st.divider()

    workflow5, workflow6, workflow7, workflow8 = st.columns(4)

    with workflow5:

        st.markdown("**05 — Approve**")

        st.caption(
            "Identify decisions requiring founder or professional approval."
        )

    with workflow6:

        st.markdown("**06 — Execute**")

        st.caption(
            "Coordinate the selected business actions."
        )

    with workflow7:

        st.markdown("**07 — Monitor**")

        st.caption(
            "Track corporate, financial, commercial, and compliance state."
        )

    with workflow8:

        st.markdown("**08 — Improve**")

        st.caption(
            "Convert recurring service work into reusable systems."
        )

    st.divider()

    # --------------------------------------------------------
    # CURRENT SYSTEM STATE
    # --------------------------------------------------------

    st.subheader(
        "Current System State"
    )

    state1, state2 = st.columns(2)

    with state1:

        st.write(
            f"**Client records:** {count_records('clients')}"
        )

        st.write(
            f"**Saved reports:** {count_records('reports')}"
        )

        st.write(
            f"**Engagement records:** {count_records('engagements')}"
        )

    with state2:

        if BACKGROUND_EXISTS:
            st.write(
                "✓ Custom PieroloOS background loaded"
            )
        else:
            st.write(
                "⚠ Custom background not found"
            )

        if LOGO_EXISTS:
            st.write(
                "✓ PieroloCorp official logo loaded"
            )
        else:
            st.write(
                "⚠ PieroloCorp logo not found"
            )

        st.write(
            "✓ Local SQLite operating database ready"
        )


# ============================================================
# 9. CLIENT INTAKE
# ============================================================

elif page == "Client Intake":

    render_page_banner(
        "Client Intake",
    )

    st.title(
        "Client Intake"
    )

    st.caption(
        "Create a structured client record for the PieroloOS workflow."
    )

    st.divider()

    with st.form(
        "client_intake_form",
        clear_on_submit=False,
    ):

        left, right = st.columns(2)

        with left:

            client_name = st.text_input(
                "Client / Founder Name *"
            )

            email = st.text_input(
                "Email"
            )

            phone = st.text_input(
                "Phone"
            )

            country = st.text_input(
                "Current Country / Residence"
            )

            business_name = st.text_input(
                "Proposed Business Name"
            )

        with right:

            business_type = st.selectbox(
                "Business Type",
                [
                    "SaaS / Technology",
                    "Consulting / Professional Services",
                    "E-commerce",
                    "Import / Export",
                    "Real Estate",
                    "Financial / Investment",
                    "Manufacturing",
                    "Other",
                ],
            )

            service = st.selectbox(
                "Requested Service",
                [
                    "Business Formation",
                    "Jurisdiction Analysis",
                    "Compliance Support",
                    "Business Consulting",
                    "Corporate Structuring",
                    "SaaS / Technology Advisory",
                    "Other",
                ],
            )

            status = st.selectbox(
                "Engagement Status",
                [
                    "New",
                    "Qualified",
                    "In Progress",
                    "Awaiting Client",
                    "Closed",
                ],
            )

        notes = st.text_area(
            "Client Objective / Notes",
            height=160,
            placeholder=(
                "Describe the business objective, target market, "
                "constraints, and immediate requirement."
            ),
        )

        submitted = st.form_submit_button(
            "Create Client Record",
            type="primary",
            use_container_width=True,
        )

    if submitted:

        if not client_name.strip():

            st.error(
                "Client / Founder Name is required."
            )

        else:

            execute_write(
                """
                INSERT INTO clients
                (
                    client_name,
                    email,
                    phone,
                    country,
                    business_name,
                    business_type,
                    service,
                    status,
                    notes,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    client_name.strip(),
                    email.strip(),
                    phone.strip(),
                    country.strip(),
                    business_name.strip(),
                    business_type,
                    service,
                    status,
                    notes.strip(),
                    current_timestamp(),
                ),
            )

            st.success(
                "Client record created successfully."
            )

            st.rerun()

    st.divider()

    st.subheader(
        "Recent Clients"
    )

    clients = fetch_all(
        """
        SELECT
            id,
            client_name,
            business_name,
            service,
            status,
            created_at
        FROM clients
        ORDER BY id DESC
        LIMIT 10
        """
    )

    if clients:

        st.dataframe(
            [dict(row) for row in clients],
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No client records have been created yet."
        )


# ============================================================
# 10. BUSINESS PROFILE
# ============================================================

elif page == "Business Profile":

    render_page_banner(
        "Business Profile",
    )

    st.title(
        "Business Profile"
    )

    st.caption(
        "Build a structured commercial and strategic profile."
    )

    st.divider()

    clients = fetch_all(
        """
        SELECT
            id,
            client_name,
            business_name
        FROM clients
        ORDER BY id DESC
        """
    )

    if not clients:

        st.info(
            "Create a client record first."
        )

    else:

        client_map = {
            row["id"]:
                row["client_name"]
                + (
                    f" — {row['business_name']}"
                    if row["business_name"]
                    else ""
                )
            for row in clients
        }

        selected_id = st.selectbox(
            "Select Client",
            list(client_map.keys()),
            format_func=lambda value:
                client_map[value],
        )

        client = fetch_one(
            """
            SELECT *
            FROM clients
            WHERE id = ?
            """,
            (selected_id,),
        )

        if client:

            st.subheader(
                "Client Identity"
            )

            identity1, identity2, identity3 = st.columns(3)

            with identity1:

                st.write(
                    f"**Founder:** {client['client_name']}"
                )

                st.write(
                    f"**Country:** "
                    f"{client['country'] or 'Not specified'}"
                )

            with identity2:

                st.write(
                    f"**Business:** "
                    f"{client['business_name'] or 'Not specified'}"
                )

                st.write(
                    f"**Type:** {client['business_type']}"
                )

            with identity3:

                st.write(
                    f"**Service:** {client['service']}"
                )

                st.write(
                    f"**Status:** {client['status']}"
                )

            st.divider()

            st.subheader(
                "Strategic Profile"
            )

            profile1, profile2 = st.columns(2)

            with profile1:

                target_market = st.text_area(
                    "Target Market",
                    height=120,
                )

                revenue_model = st.selectbox(
                    "Revenue Model",
                    [
                        "Subscription",
                        "Professional Services",
                        "E-commerce",
                        "Transaction Fees",
                        "Advertising",
                        "Licensing",
                        "Mixed",
                        "Other",
                    ],
                )

                funding_stage = st.selectbox(
                    "Funding Stage",
                    [
                        "Bootstrapped",
                        "Pre-revenue",
                        "Revenue-generating",
                        "Seeking external capital",
                        "Funded",
                    ],
                )

            with profile2:

                ownership = st.text_area(
                    "Ownership / Founder Structure",
                    height=120,
                )

                expansion = st.text_area(
                    "Expansion Objectives",
                    height=120,
                )

                key_risks = st.text_area(
                    "Known Constraints / Risks",
                    height=120,
                )

            if st.button(
                "Save Business Profile",
                type="primary",
            ):

                profile_note = (
                    "\n\n"
                    f"BUSINESS PROFILE — {current_timestamp()}\n"
                    f"Target market: {target_market}\n"
                    f"Revenue model: {revenue_model}\n"
                    f"Funding stage: {funding_stage}\n"
                    f"Ownership: {ownership}\n"
                    f"Expansion objectives: {expansion}\n"
                    f"Known risks: {key_risks}\n"
                )

                execute_write(
                    """
                    UPDATE clients
                    SET notes =
                        COALESCE(notes, '') || ?
                    WHERE id = ?
                    """,
                    (
                        profile_note,
                        selected_id,
                    ),
                )

                st.success(
                    "Business profile saved."
                )


# ============================================================
# 11. JURISDICTION LENS
# ============================================================

elif page == "Jurisdiction Lens":

    render_page_banner(
        "Jurisdiction Lens",
    )

    st.title(
        "Jurisdiction Lens"
    )

    st.caption(
        "Structured comparison for decision-support purposes."
    )

    st.warning(
        "The indicators below are internal analytical criteria. "
        "They are not legal, tax, banking, or regulatory conclusions."
    )

    st.divider()

    st.subheader(
        "Business Requirements"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        w_remote = st.slider(
            "Remote Friendliness",
            1,
            5,
            4,
        )

        w_international = st.slider(
            "International Fit",
            1,
            5,
            4,
        )

    with c2:

        w_banking = st.slider(
            "Banking / Payments",
            1,
            5,
            4,
        )

        w_privacy = st.slider(
            "Privacy",
            1,
            5,
            3,
        )

    with c3:

        w_cost = st.slider(
            "Cost Sensitivity",
            1,
            5,
            3,
        )

        w_complexity = st.slider(
            "Formation Simplicity",
            1,
            5,
            3,
        )

    with c4:

        w_compliance = st.slider(
            "Compliance Simplicity",
            1,
            5,
            3,
        )

    def calculate_score(
        item: dict,
    ) -> float:

        score = (
            item["remote_friendliness"] * w_remote
            + item["international_fit"] * w_international
            + item["banking_payment_fit"] * w_banking
            + item["privacy"] * w_privacy
            + (6 - item["cost"]) * w_cost
            + (6 - item["formation_complexity"]) * w_complexity
            + (6 - item["compliance_complexity"]) * w_compliance
        )

        total_weight = (
            w_remote
            + w_international
            + w_banking
            + w_privacy
            + w_cost
            + w_complexity
            + w_compliance
        )

        return round(
            score / total_weight,
            2,
        )

    results = []

    for item in JURISDICTIONS:

        copy = item.copy()

        copy["indicator"] = calculate_score(
            item
        )

        results.append(copy)

    st.divider()

    st.subheader(
        "Comparison"
    )

    st.dataframe(
        [
            {
                "Jurisdiction":
                    item["jurisdiction"],
                "Indicator":
                    item["indicator"],
                "Remote":
                    item["remote_friendliness"],
                "International":
                    item["international_fit"],
                "Banking / Payments":
                    item["banking_payment_fit"],
                "Privacy":
                    item["privacy"],
                "Cost":
                    item["cost"],
                "Formation Complexity":
                    item["formation_complexity"],
                "Compliance Complexity":
                    item["compliance_complexity"],
            }
            for item in results
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader(
        "Jurisdiction Profiles"
    )

    for item in results:

        with st.expander(
            item["jurisdiction"]
        ):

            st.write(
                item["summary"]
            )

            st.caption(
                f"Source family: {item['source']}"
            )


# ============================================================
# 12. FORMATION ROADMAP
# ============================================================

elif page == "Formation Roadmap":

    render_page_banner(
        "Formation Roadmap",
    )

    st.title(
        "Formation Roadmap"
    )

    st.caption(
        "Convert a business objective into an organised formation sequence."
    )

    st.divider()

    left, right = st.columns(2)

    with left:

        founder_country = st.text_input(
            "Founder Residence / Country",
            value="Nigeria",
        )

        target_jurisdiction = st.selectbox(
            "Target Jurisdiction",
            [
                item["jurisdiction"]
                for item in JURISDICTIONS
            ],
        )

        business_model = st.selectbox(
            "Business Model",
            [
                "SaaS",
                "Consulting",
                "E-commerce",
                "Import / Export",
                "Real Estate",
                "Investment",
                "Mixed",
            ],
        )

    with right:

        banking_needed = st.checkbox(
            "Business banking required",
            value=True,
        )

        payment_gateway = st.checkbox(
            "International payment gateway required",
            value=True,
        )

        contractors = st.checkbox(
            "International contractors expected",
            value=False,
        )

        fundraising = st.checkbox(
            "External fundraising expected",
            value=False,
        )

        ip_protection = st.checkbox(
            "Formal IP ownership required",
            value=True,
        )

    st.divider()

    if st.button(
        "Generate Formation Roadmap",
        type="primary",
        use_container_width=True,
    ):

        steps = [
            (
                "01",
                "Define Entity Purpose",
                "Document the business model, customers, ownership, and intended activities.",
            ),
            (
                "02",
                "Validate Jurisdiction",
                f"Verify the current requirements applicable to {target_jurisdiction}.",
            ),
            (
                "03",
                "Prepare Formation Information",
                "Collect founder, ownership, address, and company information.",
            ),
            (
                "04",
                "Form the Entity",
                "Complete the applicable company-registration process.",
            ),
            (
                "05",
                "Establish Governance",
                "Maintain operating agreements, resolutions, ownership records, and governance documents as applicable.",
            ),
            (
                "06",
                "Tax / Identification Setup",
                "Determine and obtain applicable identification and registrations.",
            ),
        ]

        if banking_needed:

            steps.append(
                (
                    "07",
                    "Business Banking",
                    "Establish appropriate business banking subject to provider eligibility.",
                )
            )

        if payment_gateway:

            steps.append(
                (
                    "08",
                    "Payment Infrastructure",
                    "Establish payment processing and invoicing infrastructure subject to provider requirements.",
                )
            )

        steps.append(
            (
                "09",
                "Operational Infrastructure",
                "Set up accounting, contracts, records, security, and document management.",
            )
        )

        if ip_protection:

            steps.append(
                (
                    "10",
                    "IP Ownership",
                    "Confirm ownership or licensing of software, branding, documentation, and contractor-created work.",
                )
            )

        if contractors:

            steps.append(
                (
                    "11",
                    "Contractor Framework",
                    "Implement appropriate contractor agreements, confidentiality, IP, onboarding, and payment controls.",
                )
            )

        if fundraising:

            steps.append(
                (
                    "12",
                    "Capital Readiness",
                    "Organise governance, financial records, ownership records, IP ownership, and investor materials.",
                )
            )

        steps.append(
            (
                "13",
                "Compliance Calendar",
                "Track recurring corporate, tax, filing, licence, and reporting obligations.",
            )
        )

        steps.append(
            (
                "14",
                "Launch and Monitor",
                "Begin operations and continuously monitor the company's corporate, financial, commercial, and compliance state.",
            )
        )

        st.subheader(
            "Formation Sequence"
        )

        for number, title, description in steps:

            with st.container(border=True):

                st.markdown(
                    f"### {number} — {title}"
                )

                st.write(
                    description
                )

    st.caption(
        f"Planning context: founder country = {founder_country}; "
        f"business model = {business_model}."
    )


# ============================================================
# 13. COMPLIANCE
# ============================================================

elif page == "Compliance":

    render_page_banner(
        "Compliance",
    )

    st.title(
        "Compliance Checklist"
    )

    st.caption(
        "High-level operational checklist. Requirements must be verified against current official sources."
    )

    st.divider()

    jurisdiction = st.selectbox(
        "Operating / Formation Jurisdiction",
        [
            item["jurisdiction"]
            for item in JURISDICTIONS
        ],
    )

    checklist = [
        "Maintain formation and governance records",
        "Maintain registered-agent or official-address requirements where applicable",
        "Track annual reports and periodic filings",
        "Track federal, state, or local tax obligations",
        "Maintain accounting and financial records",
        "Reconcile business bank accounts",
        "Review payment-provider requirements",
        "Maintain client contracts and engagement records",
        "Maintain contractor agreements and IP provisions",
        "Review applicable licences and permits",
        "Review data protection and privacy obligations",
        "Review cybersecurity and access controls",
        "Review applicable ownership / reporting requirements",
        "Maintain business continuity and document backups",
    ]

    completed = 0

    for index, item in enumerate(checklist):

        if st.checkbox(
            item,
            key=f"compliance_{index}",
        ):

            completed += 1

    progress = (
        completed / len(checklist)
    )

    st.progress(progress)

    st.write(
        f"{completed} of {len(checklist)} checklist items completed."
    )

    st.info(
        f"Current jurisdiction selected: {jurisdiction}"
    )


# ============================================================
# 14. REPORT GENERATOR
# ============================================================

elif page == "Report Generator":

    render_page_banner(
        "Report Generator",
    )

    st.title(
        "Report Generator"
    )

    st.caption(
        "Generate structured reports from stored client information."
    )

    st.divider()

    clients = fetch_all(
        """
        SELECT
            id,
            client_name,
            business_name,
            country,
            service,
            status,
            notes
        FROM clients
        ORDER BY id DESC
        """
    )

    if not clients:

        st.info(
            "Create a client record first."
        )

    else:

        client_map = {
            row["id"]:
                row["client_name"]
                + (
                    f" — {row['business_name']}"
                    if row["business_name"]
                    else ""
                )
            for row in clients
        }

        selected_id = st.selectbox(
            "Client",
            list(client_map.keys()),
            format_func=lambda value:
                client_map[value],
        )

        client = fetch_one(
            """
            SELECT *
            FROM clients
            WHERE id = ?
            """,
            (selected_id,),
        )

        report_type = st.selectbox(
            "Report Type",
            [
                "Business Profile Report",
                "Jurisdiction Analysis Report",
                "Formation Roadmap Report",
                "Engagement Summary",
            ],
        )

        additional_context = st.text_area(
            "Additional Context",
            height=180,
        )

        if st.button(
            "Generate & Save Report",
            type="primary",
            use_container_width=True,
        ):

            timestamp = current_timestamp()

            report = f"""
# PieroloOS — {report_type}

**PieroloCorp International LLC**

## Client

- Name: {client['client_name']}
- Business: {client['business_name'] or 'Not specified'}
- Country: {client['country'] or 'Not specified'}
- Service: {client['service']}
- Engagement Status: {client['status']}
- Generated: {timestamp}

## Business Information

{client['notes'] or 'No additional business information has been recorded.'}

## Additional Context

{additional_context or 'No additional context provided.'}

## Operating Considerations

1. Verify material facts against primary sources.
2. Confirm jurisdiction-specific legal, tax, banking, and regulatory requirements.
3. Separate facts from assumptions.
4. Record client decisions and approvals.
5. Preserve supporting evidence.
6. Update the engagement record as the matter progresses.

## Disclaimer

This report is generated by PieroloOS as a decision-support and professional-service workflow aid. It is not legal, tax, accounting, financial, immigration, regulatory, or other licensed professional advice.
"""

            filename = safe_filename(
                f"{client['client_name']}_{report_type}_{timestamp}"
            )

            report_path = (
                REPORT_DIR
                / f"{filename}.md"
            )

            report_path.write_text(
                report,
                encoding="utf-8",
            )

            execute_write(
                """
                INSERT INTO reports
                (
                    client_name,
                    report_type,
                    content,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    client["client_name"],
                    report_type,
                    report,
                    timestamp,
                ),
            )

            st.success(
                "Report generated and saved."
            )

            st.download_button(
                "Download Markdown Report",
                data=report,
                file_name=f"{filename}.md",
                mime="text/markdown",
                use_container_width=True,
            )

            with st.expander(
                "Report Preview",
                expanded=True,
            ):

                st.markdown(
                    report
                )

    st.divider()

    st.subheader(
        "Previous Reports"
    )

    reports = fetch_all(
        """
        SELECT
            id,
            client_name,
            report_type,
            created_at
        FROM reports
        ORDER BY id DESC
        LIMIT 20
        """
    )

    if reports:

        st.dataframe(
            [dict(row) for row in reports],
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No reports have been generated yet."
        )


# ============================================================
# 15. ENGAGEMENT RECORDS
# ============================================================

elif page == "Engagement Records":

    render_page_banner(
        "Engagement Records",
    )

    st.title(
        "Engagement Records"
    )

    st.caption(
        "Maintain the operational register for client matters."
    )

    st.divider()

    clients = fetch_all(
        """
        SELECT
            id,
            client_name,
            business_name
        FROM clients
        ORDER BY id DESC
        """
    )

    if clients:

        client_map = {
            row["id"]:
                row["client_name"]
                + (
                    f" — {row['business_name']}"
                    if row["business_name"]
                    else ""
                )
            for row in clients
        }

        with st.form(
            "engagement_form"
        ):

            selected_client = st.selectbox(
                "Client",
                list(client_map.keys()),
                format_func=lambda value:
                    client_map[value],
            )

            service = st.text_input(
                "Engagement / Service"
            )

            status = st.selectbox(
                "Status",
                [
                    "Open",
                    "In Progress",
                    "Awaiting Client",
                    "Awaiting Provider",
                    "Completed",
                    "On Hold",
                    "Closed",
                ],
            )

            next_action = st.text_input(
                "Next Action"
            )

            notes = st.text_area(
                "Engagement Notes",
                height=120,
            )

            create = st.form_submit_button(
                "Create Engagement Record",
                type="primary",
                use_container_width=True,
            )

        if create:

            client = fetch_one(
                """
                SELECT client_name
                FROM clients
                WHERE id = ?
                """,
                (selected_client,),
            )

            if client:

                execute_write(
                    """
                    INSERT INTO engagements
                    (
                        client_name,
                        service,
                        status,
                        next_action,
                        notes,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        client["client_name"],
                        service.strip(),
                        status,
                        next_action.strip(),
                        notes.strip(),
                        current_timestamp(),
                    ),
                )

                st.success(
                    "Engagement record created."
                )

                st.rerun()

    else:

        st.info(
            "Create a client record first."
        )

    st.divider()

    st.subheader(
        "Engagement Register"
    )

    engagements = fetch_all(
        """
        SELECT
            id,
            client_name,
            service,
            status,
            next_action,
            notes,
            updated_at
        FROM engagements
        ORDER BY id DESC
        """
    )

    if engagements:

        st.dataframe(
            [dict(row) for row in engagements],
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "Update Engagement"
        )

        engagement_map = {
            row["id"]:
                f"#{row['id']} — "
                f"{row['client_name']} — "
                f"{row['service'] or 'Service not specified'}"
            for row in engagements
        }

        selected_engagement = st.selectbox(
            "Engagement",
            list(engagement_map.keys()),
            format_func=lambda value:
                engagement_map[value],
        )

        new_status = st.selectbox(
            "New Status",
            [
                "Open",
                "In Progress",
                "Awaiting Client",
                "Awaiting Provider",
                "Completed",
                "On Hold",
                "Closed",
            ],
        )

        new_action = st.text_input(
            "Next Action"
        )

        if st.button(
            "Update Engagement",
            type="primary",
            use_container_width=True,
        ):

            execute_write(
                """
                UPDATE engagements
                SET
                    status = ?,
                    next_action = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    new_status,
                    new_action.strip(),
                    current_timestamp(),
                    selected_engagement,
                ),
            )

            st.success(
                "Engagement updated."
            )

            st.rerun()

    else:

        st.info(
            "No engagement records have been created yet."
        )


# ============================================================
# 16. FOOTER — ABSOLUTE END OF APPLICATION CONTENT
# ============================================================

st.markdown(
    """
    <div class="pieroloos-footer-spacer" aria-hidden="true"></div>
    <footer class="pieroloos-footer" aria-label="PieroloOS footer">
        <div class="footer-orbit"></div>
        <div class="footer-brand">PIEROLOOS</div>
        <div class="footer-company">
            Professional Service Operating System · PieroloCorp International LLC
        </div>
        <div class="footer-disclaimer">
            Decision-support prototype. Verify legal, tax, regulatory, banking,
            and compliance matters with appropriate professionals and official authorities.
        </div>
    </footer>
    <div class="pieroloos-scroll-end" aria-hidden="true"></div>
    """,
    unsafe_allow_html=True,
)
