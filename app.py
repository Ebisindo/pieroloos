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



def render_page_banner(page_name: str, title: str, subtitle: str) -> None:
    """Render a page-specific graphical hero with a branded overlay."""
    banner_path = PAGE_BANNER_CANDIDATES.get(page_name)
    image_uri = load_image_data_uri(str(banner_path)) if banner_path and asset_exists(banner_path) else ""

    if image_uri:
        st.markdown(
            f"""
            <section class="page-banner">
                <img class="page-banner-image" src="{image_uri}" alt="{title} graphical header" />
                <div class="page-banner-overlay"></div>
                <div class="page-banner-content">
                    <div class="page-banner-eyebrow">PIEROLOOS · PIEROLOCORP INTERNATIONAL LLC</div>
                    <div class="page-banner-title">{title}</div>
                    <div class="page-banner-subtitle">{subtitle}</div>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <section class="page-banner page-banner-fallback">
                <div class="page-banner-content">
                    <div class="page-banner-eyebrow">PIEROLOOS · PIEROLOCORP INTERNATIONAL LLC</div>
                    <div class="page-banner-title">{title}</div>
                    <div class="page-banner-subtitle">{subtitle}</div>
                    <div class="page-banner-missing">GRAPHICAL ASSET NOT FOUND · CHECK /assets/{banner_path.name if banner_path else ''}</div>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# 6. VISUAL DESIGN
# ============================================================

def inject_styles() -> None:
    """Inject the responsive PieroloOS visual system without f-string CSS errors."""
    if BACKGROUND_URI:
        background_css = (
            "background-image: "
            "linear-gradient(rgba(5,5,18,0.78), rgba(5,5,18,0.92)), "
            f"url('{BACKGROUND_URI}');"
        )
    else:
        background_css = (
            "background: radial-gradient(circle at 80% 10%, "
            "rgba(155,108,255,0.20), transparent 30%), "
            "linear-gradient(135deg, #050512, #110a28, #050512);"
        )

    css = """
    <style>
    :root {
        --gold: #d7b45a;
        --gold-light: #f1d98a;
        --violet: #9b6cff;
        --violet-light: #c5a7ff;
        --navy: #050512;
        --panel: rgba(12, 10, 31, 0.82);
        --border: rgba(215, 180, 90, 0.20);
        --text: #f6f3ff;
        --muted: #aaa3c2;
    }

    .stApp {
        BACKGROUND_CSS_PLACEHOLDER
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: var(--text);
    }

    [data-testid="stSidebar"] {
        background: rgba(5, 5, 18, 0.97);
        border-right: 1px solid rgba(215, 180, 90, 0.20);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.25rem;
        padding-bottom: 4rem;
    }

    h1 { color: var(--gold-light); }
    h2 { color: #f6f0ff; }
    h3 { color: #f1eaff; }
    p { color: #d0c9df; }
    .stCaption { color: #9991ac; }

    .page-banner {
        position: relative;
        width: 100%;
        min-height: 290px;
        margin: 0 0 1.5rem 0;
        overflow: hidden;
        border-radius: 24px;
        border: 1px solid rgba(215, 180, 90, 0.28);
        background: rgba(8, 7, 24, 0.90);
        box-shadow: 0 24px 70px rgba(0,0,0,0.35);
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
        background: linear-gradient(90deg, rgba(5,5,18,0.94) 0%, rgba(5,5,18,0.68) 42%, rgba(5,5,18,0.24) 100%);
    }

    .page-banner-content {
        position: relative;
        z-index: 2;
        min-height: 290px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 2rem 3rem;
        max-width: 850px;
    }

    .page-banner-eyebrow {
        color: var(--gold-light);
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
    }

    .page-banner-title {
        color: #ffffff;
        font-size: clamp(2rem, 4vw, 3.6rem);
        line-height: 1.05;
        font-weight: 850;
        letter-spacing: -0.035em;
        text-shadow: 0 5px 25px rgba(0,0,0,0.55);
    }

    .page-banner-subtitle {
        color: #d9d2e9;
        font-size: 1rem;
        line-height: 1.55;
        margin-top: 0.9rem;
        max-width: 680px;
    }

    .page-banner-missing {
        margin-top: 1rem;
        color: #e5c66d;
        font-size: 0.7rem;
        letter-spacing: 0.08em;
    }

    .page-banner-fallback {
        background: radial-gradient(circle at 80% 20%, rgba(155,108,255,0.25), transparent 34%), linear-gradient(135deg, #090718, #17102e, #050512);
    }

    div[data-testid="stMetric"] {
        background: rgba(12, 10, 31, 0.78);
        border: 1px solid rgba(215, 180, 90, 0.18);
        border-radius: 18px;
        padding: 1rem;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.20);
    }

    div[data-testid="stMetricLabel"] { color: #aaa3c2; }
    div[data-testid="stMetricValue"] { color: #f1d98a; }

    div[data-testid="stButton"] > button {
        border: 1px solid rgba(215, 180, 90, 0.25);
        border-radius: 12px;
        background: rgba(15, 11, 35, 0.90);
        color: #f4edff;
        font-weight: 700;
    }

    div[data-testid="stButton"] > button:hover {
        border-color: rgba(215, 180, 90, 0.70);
        color: #f1d98a;
    }

    div[data-testid="stFormSubmitButton"] > button {
        border-radius: 12px;
        font-weight: 800;
    }

    [data-testid="stExpander"] {
        background: rgba(12, 10, 31, 0.72);
        border: 1px solid rgba(155, 108, 255, 0.18);
        border-radius: 15px;
    }

    [data-testid="stDataFrame"] { border-radius: 14px; }

    .asset-status {
        padding: 0.75rem 0.9rem;
        margin: 0.35rem 0;
        border-radius: 12px;
        background: rgba(12,10,31,0.72);
        border: 1px solid rgba(155,108,255,0.14);
        font-size: 0.78rem;
    }

    @media (max-width: 768px) {
        .block-container { padding-left: 0.85rem; padding-right: 0.85rem; }
        .page-banner { min-height: 220px; border-radius: 18px; }
        .page-banner-content { min-height: 220px; padding: 1.35rem 1.25rem; }
        .page-banner-title { font-size: 2rem; }
        .page-banner-subtitle { font-size: 0.86rem; }
        .page-banner-overlay { background: linear-gradient(90deg, rgba(5,5,18,0.94), rgba(5,5,18,0.55)); }
    }
    </style>
    """

    st.markdown(
        css.replace("BACKGROUND_CSS_PLACEHOLDER", background_css),
        unsafe_allow_html=True,
    )


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
# ============================================================

if page == "Command Center":

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    render_page_banner(
        "Command Center",
        "PieroloOS Command Center",
        "Executive visibility across the professional-service operating environment.",
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
        "Client Intake",
        "Capture a structured client and business brief.",
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
        "Business Profile",
        "Build a decision-ready commercial and strategic profile.",
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
        "Jurisdiction Lens",
        "Structured jurisdiction intelligence for business decisions.",
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
        "Formation Roadmap",
        "Translate business intent into an executable formation sequence.",
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
        "Compliance Control",
        "Keep recurring corporate and operational obligations visible.",
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
        "Report Generator",
        "Turn structured client information into professional outputs.",
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
        "Engagement Control",
        "Track client matters, actions, status and operational history.",
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
# 16. FOOTER
# ============================================================

st.divider()

st.caption(
    "PIEROLOOS v0.1 · Professional Service Operating System · "
    "PieroloCorp International LLC"
)

st.caption(
    "Decision-support prototype. Verify legal, tax, regulatory, "
    "banking, and compliance matters with appropriate professionals "
    "and official authorities."
)
