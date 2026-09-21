from pathlib import Path
import base64
import html
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
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ASSET_DIR = BASE_DIR / "assets"
REPORT_DIR = BASE_DIR / "reports"
DB_PATH = BASE_DIR / "pieroloos.db"

BACKGROUND_PATH = ASSET_DIR / "pieroloos_background.svg"

# Supports both possible logo spellings.
LOGO_CANDIDATES = [
    ASSET_DIR / "pierolocorp_logo.png",
    ASSET_DIR / "pierolooscorp_logo.png",
]

LOGO_PATH = next(
    (path for path in LOGO_CANDIDATES if path.exists()),
    None,
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. ASSET FUNCTIONS
# ============================================================

@st.cache_data(show_spinner=False)
def get_background_uri() -> str:
    """Convert the SVG background into a browser-safe data URI."""
    if not BACKGROUND_PATH.exists():
        return ""

    encoded = base64.b64encode(
        BACKGROUND_PATH.read_bytes()
    ).decode("ascii")

    return f"data:image/svg+xml;base64,{encoded}"


BACKGROUND_URI = get_background_uri()


def asset_status() -> tuple[bool, bool]:
    """Return background and logo availability."""
    background_exists = BACKGROUND_PATH.exists()
    logo_exists = LOGO_PATH is not None

    return background_exists, logo_exists


background_ok, logo_ok = asset_status()


# ============================================================
# 3. DATABASE
# ============================================================

def get_connection() -> sqlite3.Connection:
    """Open the local PieroloOS SQLite database."""
    connection = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_database() -> None:
    """Create required database tables."""
    connection = get_connection()
    cursor = connection.cursor()

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

    connection.commit()
    connection.close()


init_database()


# ============================================================
# 4. DATABASE HELPERS
# ============================================================

def execute_write(
    query: str,
    params: tuple = (),
) -> None:
    connection = get_connection()

    connection.execute(
        query,
        params,
    )

    connection.commit()
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


def count_records(table: str) -> int:
    allowed_tables = {
        "clients",
        "reports",
        "engagements",
    }

    if table not in allowed_tables:
        return 0

    row = fetch_one(
        f"SELECT COUNT(*) AS total FROM {table}"
    )

    return int(row["total"]) if row else 0


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


# ============================================================
# 6. GLOBAL CSS
# ============================================================

def inject_css() -> None:

    if BACKGROUND_URI:

        background_rule = f"""
            background-image:
                linear-gradient(
                    rgba(5, 5, 18, 0.72),
                    rgba(5, 5, 18, 0.88)
                ),
                url("{BACKGROUND_URI}");
        """

    else:

        background_rule = """
            background:
                radial-gradient(
                    circle at 70% 15%,
                    rgba(113, 60, 180, 0.30),
                    transparent 30%
                ),
                linear-gradient(
                    135deg,
                    #050512 0%,
                    #100a25 50%,
                    #050512 100%
                );
        """

    hero_background = (
        f'url("{BACKGROUND_URI}")'
        if BACKGROUND_URI
        else "none"
    )

    st.markdown(
        f"""
        <style>

        @import url(
            'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap'
        );

        :root {{
            --navy: #050512;
            --panel: rgba(12, 10, 31, 0.78);
            --panel-strong: rgba(17, 12, 40, 0.92);
            --gold: #d7b45a;
            --gold-light: #f1d98a;
            --violet: #9b6cff;
            --violet-light: #c5a7ff;
            --text: #f6f3ff;
            --muted: #aaa3c2;
            --border: rgba(215, 180, 90, 0.20);
        }}

        html,
        body,
        [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stApp {{
            color: var(--text);
            {background_rule}
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;

            background:
                radial-gradient(
                    circle at 80% 10%,
                    rgba(155,108,255,0.10),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 15% 85%,
                    rgba(215,180,90,0.06),
                    transparent 24%
                );

            z-index: 0;
        }}

        .block-container {{
            position: relative;
            z-index: 1;
            max-width: 1500px;
            padding-top: 1.25rem;
            padding-bottom: 3rem;
        }}

        [data-testid="stSidebar"] {{
            background: rgba(5, 5, 18, 0.96);
            border-right: 1px solid var(--border);
        }}

        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 1rem;
        }}

        [data-testid="stSidebar"] .stRadio label {{
            color: #ddd6f7 !important;
            font-weight: 600;
        }}

        [data-testid="stSidebar"]
        .stRadio
        div[role="radiogroup"] {{
            gap: 0.25rem;
        }}

        h1,
        h2,
        h3,
        h4 {{
            font-family: 'Space Grotesk', sans-serif;
            letter-spacing: -0.02em;
        }}

        h1 {{
            color: var(--gold-light);
        }}

        h2,
        h3 {{
            color: #f4edff;
        }}

        p,
        li {{
            color: #d2cce3;
        }}

        .hero {{
            position: relative;
            overflow: hidden;

            border: 1px solid var(--border);
            border-radius: 24px;

            padding: 2.25rem;
            min-height: 290px;

            margin-bottom: 1.25rem;

            background:
                linear-gradient(
                    135deg,
                    rgba(7,6,21,.90),
                    rgba(27,13,55,.70)
                ),
                {hero_background};

            background-size: cover;
            background-position: center;

            box-shadow:
                0 20px 70px rgba(0,0,0,.35);
        }}

        .hero::after {{
            content: "";

            position: absolute;

            width: 280px;
            height: 280px;

            right: -90px;
            top: -90px;

            border:
                1px solid
                rgba(215,180,90,.28);

            border-radius: 50%;

            box-shadow:
                0 0 70px
                rgba(155,108,255,.18);
        }}

        .eyebrow {{
            color: var(--gold);

            text-transform: uppercase;

            letter-spacing: .18em;

            font-size: .74rem;

            font-weight: 800;

            margin-bottom: .6rem;
        }}

        .hero-title {{
            font-family: 'Space Grotesk', sans-serif;

            font-size:
                clamp(2rem, 5vw, 4.4rem);

            line-height: .98;

            font-weight: 800;

            color: #fff;

            max-width: 820px;

            margin-bottom: 1rem;
        }}

        .hero-title span {{
            color: var(--gold-light);
        }}

        .hero-copy {{
            max-width: 760px;

            color: #c5bddb;

            font-size: 1.02rem;

            line-height: 1.65;
        }}

        .metric-card {{
            background: var(--panel);

            border:
                1px solid
                rgba(215,180,90,.16);

            border-radius: 18px;

            padding: 1.1rem 1.2rem;

            min-height: 112px;

            box-shadow:
                0 12px 35px
                rgba(0,0,0,.20);
        }}

        .metric-label {{
            color: var(--muted);

            font-size: .78rem;

            text-transform: uppercase;

            letter-spacing: .08em;

            font-weight: 700;
        }}

        .metric-value {{
            color: var(--gold-light);

            font-family: 'Space Grotesk', sans-serif;

            font-size: 2rem;

            font-weight: 800;

            margin-top: .35rem;
        }}

        .section-card {{
            background: var(--panel);

            border:
                1px solid
                rgba(155,108,255,.17);

            border-radius: 20px;

            padding: 1.25rem;

            margin-bottom: 1rem;

            box-shadow:
                0 12px 40px
                rgba(0,0,0,.18);
        }}

        .quick-card {{
            background:
                linear-gradient(
                    145deg,
                    rgba(16,12,36,.92),
                    rgba(28,17,57,.76)
                );

            border:
                1px solid
                rgba(215,180,90,.16);

            border-radius: 18px;

            padding: 1.25rem;

            min-height: 150px;
        }}

        .quick-icon {{
            color: var(--gold);

            font-size: 1.6rem;
        }}

        .quick-title {{
            color: #fff;

            font-weight: 800;

            font-size: 1.05rem;

            margin: .45rem 0;
        }}

        .quick-copy {{
            color: var(--muted);

            font-size: .88rem;

            line-height: 1.5;
        }}

        .status-pill {{
            display: inline-block;

            padding: .28rem .65rem;

            border-radius: 999px;

            background:
                rgba(155,108,255,.13);

            border:
                1px solid
                rgba(155,108,255,.25);

            color: var(--violet-light);

            font-size: .74rem;

            font-weight: 800;
        }}

        .footer {{
            margin-top: 3rem;

            padding:
                1.5rem 0 .5rem;

            border-top:
                1px solid
                rgba(215,180,90,.12);

            color: #817a99;

            font-size: .78rem;

            text-align: center;
        }}

        .small-note {{
            color: #928ba8;

            font-size: .78rem;

            line-height: 1.5;
        }}

        div[data-testid="stButton"] > button {{
            border:
                1px solid
                rgba(215,180,90,.24);

            border-radius: 12px;

            background:
                rgba(18,13,40,.82);

            color: #f2eaff;

            font-weight: 700;
        }}

        div[data-testid="stButton"] > button:hover {{
            border-color:
                rgba(215,180,90,.65);

            color: var(--gold-light);
        }}

        div[data-testid="stFormSubmitButton"] > button {{
            border-radius: 12px;

            font-weight: 800;
        }}

        [data-testid="stDataFrame"] {{
            border:
                1px solid
                rgba(215,180,90,.12);

            border-radius: 14px;
        }}

        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"],
        .stNumberInput input {{
            border-radius: 10px;
        }}

        @media (max-width: 768px) {{

            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}

            .hero {{
                padding: 1.4rem;

                min-height: 250px;

                border-radius: 18px;
            }}

            .hero-title {{
                font-size: 2.2rem;
            }}
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# ============================================================
# 7. UI HELPERS
# ============================================================

def page_header(
    title: str,
    subtitle: str = "",
) -> None:

    st.markdown(
        f"## {html.escape(title)}"
    )

    if subtitle:

        st.markdown(
            f"""
            <p class="small-note">
                {html.escape(subtitle)}
            </p>
            """,
            unsafe_allow_html=True,
        )


def metric_card(
    label: str,
    value: str | int,
) -> None:

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                {html.escape(label)}
            </div>

            <div class="metric-value">
                {html.escape(str(value))}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


def section_start(
    title: str,
    description: str = "",
) -> None:

    st.markdown(
        '<div class="section-card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"### {html.escape(title)}"
    )

    if description:

        st.markdown(
            f"""
            <div class="small-note">
                {html.escape(description)}
            </div>
            """,
            unsafe_allow_html=True,
        )


def section_end() -> None:

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


def now_text() -> str:
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def safe_filename(value: str) -> str:

    cleaned = "".join(
        character
        if character.isalnum()
        or character in "-_"
        else "_"
        for character in value
    )

    return cleaned.strip("_") or "report"


# ============================================================
# 8. SIDEBAR / NAVIGATION
# ============================================================

with st.sidebar:

    if logo_ok:

        st.image(
            str(LOGO_PATH),
            width=185,
        )

    else:

        st.markdown(
            """
            <div style="padding:10px 0 18px;">

                <div style="
                    color:#d7b45a;
                    font-size:1.35rem;
                    font-weight:800;
                ">
                    PIEROLOOS
                </div>

                <div style="
                    color:#8f86a7;
                    font-size:.72rem;
                ">
                    PIEROLOCORP INTERNATIONAL LLC
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="status-pill">
            PROFESSIONAL SERVICE OS · v0.1
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    nav_options = [
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
        nav_options,
        label_visibility="collapsed",
    )

    st.markdown("---")

    st.markdown(
        """
        <div class="small-note">

        <b>Operating principle</b><br>

        Prepare → Analyse → Decide → Execute
        → Record → Improve

        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("System Status"):

        st.write(
            f"Background: "
            f"{'✓ Found' if background_ok else '✗ Missing'}"
        )

        st.write(
            f"Logo: "
            f"{'✓ Found' if logo_ok else '✗ Missing'}"
        )

        st.write(
            "Database: ✓ Ready"
        )

        if LOGO_PATH:

            st.caption(
                f"Logo file: {LOGO_PATH.name}"
            )

    st.caption(
        "Decision-support prototype. "
        "Not legal, tax, accounting, or financial advice."
    )


# ============================================================
# 9. COMMAND CENTER
# ============================================================

if page == "Command Center":

    st.markdown(
        """
        <div class="hero">

            <div class="eyebrow">
                PieroloCorp International LLC
            </div>

            <div class="hero-title">
                The operating system for a
                <span>structured business.</span>
            </div>

            <div class="hero-copy">

                PieroloOS brings client intake,
                business intelligence, jurisdiction analysis,
                formation planning, compliance tracking,
                reporting, and engagement management
                into one founder-operated workspace.

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4)

    with cols[0]:
        metric_card(
            "Clients",
            count_records("clients"),
        )

    with cols[1]:
        metric_card(
            "Reports",
            count_records("reports"),
        )

    with cols[2]:
        metric_card(
            "Engagements",
            count_records("engagements"),
        )

    with cols[3]:
        metric_card(
            "Jurisdictions",
            len(JURISDICTIONS),
        )

    st.markdown("### Quick Access")

    qcols = st.columns(4)

    quick_items = [
        (
            "01",
            "Client Intake",
            "Capture and structure a new client engagement.",
        ),
        (
            "02",
            "Jurisdiction Lens",
            "Compare jurisdictions against business criteria.",
        ),
        (
            "03",
            "Formation Roadmap",
            "Turn a business objective into an execution sequence.",
        ),
        (
            "04",
            "Report Generator",
            "Convert structured information into a client-ready report.",
        ),
    ]

    for column, item in zip(
        qcols,
        quick_items,
    ):

        number, title, copy = item

        with column:

            st.markdown(
                f"""
                <div class="quick-card">

                    <div class="quick-icon">
                        {number}
                    </div>

                    <div class="quick-title">
                        {title}
                    </div>

                    <div class="quick-copy">
                        {copy}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### Operating Model")

    section_start(
        "PieroloOS Workflow",
        "The MVP is structured around a repeatable professional-service operating loop.",
    )

    workflow = [
        (
            "01",
            "Intake",
            "Capture the client's objective and facts.",
        ),
        (
            "02",
            "Classify",
            "Structure the business and service requirement.",
        ),
        (
            "03",
            "Assess",
            "Compare jurisdictions, risks, and requirements.",
        ),
        (
            "04",
            "Plan",
            "Generate a practical formation and compliance roadmap.",
        ),
        (
            "05",
            "Approve",
            "Identify decisions requiring client or professional approval.",
        ),
        (
            "06",
            "Execute",
            "Coordinate the selected actions.",
        ),
        (
            "07",
            "Record",
            "Preserve reports, status, and engagement history.",
        ),
        (
            "08",
            "Improve",
            "Convert recurring work into reusable systems.",
        ),
    ]

    workflow_columns = st.columns(4)

    for index, item in enumerate(workflow):

        number, title, description = item

        with workflow_columns[index % 4]:

            st.markdown(
                f"""
                <div style="padding:.8rem 0 1rem;">

                    <div style="
                        color:#d7b45a;
                        font-weight:800;
                    ">
                        {number}
                    </div>

                    <div style="
                        color:#fff;
                        font-weight:800;
                        margin:.2rem 0;
                    ">
                        {title}
                    </div>

                    <div class="small-note">
                        {description}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    section_end()


# ============================================================
# 10. CLIENT INTAKE
# ============================================================

elif page == "Client Intake":

    page_header(
        "Client Intake",
        "Create a structured client record that can feed the remaining PieroloOS modules.",
    )

    with st.form(
        "client_intake_form",
        clear_on_submit=False,
    ):

        column1, column2 = st.columns(2)

        with column1:

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

        with column2:

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
            placeholder=(
                "Describe the business objective, target market, "
                "constraints, and immediate requirement."
            ),
            height=160,
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
                    now_text(),
                ),
            )

            st.success(
                "Client record created successfully."
            )

            st.rerun()

    st.markdown("### Recent Clients")

    rows = fetch_all(
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

    if rows:

        st.dataframe(
            [dict(row) for row in rows],
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No client records have been created yet."
        )


# ============================================================
# 11. BUSINESS PROFILE
# ============================================================

elif page == "Business Profile":

    page_header(
        "Business Profile",
        "Create a structured profile from the client's commercial, operational, and strategic context.",
    )

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
            "Create a client record first in Client Intake."
        )

    else:

        labels = {
            row["id"]:
                f"{row['client_name']}"
                + (
                    f" — {row['business_name']}"
                    if row["business_name"]
                    else ""
                )
            for row in clients
        }

        selected_id = st.selectbox(
            "Select Client",
            list(labels.keys()),
            format_func=lambda value: labels[value],
        )

        client = fetch_one(
            "SELECT * FROM clients WHERE id = ?",
            (selected_id,),
        )

        if client:

            section_start(
                "Client Identity",
                "Information currently stored in the client intake record.",
            )

            column1, column2, column3 = st.columns(3)

            with column1:

                st.write(
                    "**Founder:**",
                    client["client_name"],
                )

                st.write(
                    "**Country:**",
                    client["country"]
                    or "Not specified",
                )

            with column2:

                st.write(
                    "**Business:**",
                    client["business_name"]
                    or "Not specified",
                )

                st.write(
                    "**Type:**",
                    client["business_type"],
                )

            with column3:

                st.write(
                    "**Service:**",
                    client["service"],
                )

                st.write(
                    "**Status:**",
                    client["status"],
                )

            section_end()

            section_start(
                "Strategic Profile",
                "Complete this assessment as part of the engagement analysis.",
            )

            column1, column2 = st.columns(2)

            with column1:

                target_market = st.text_area(
                    "Target Market",
                    placeholder=(
                        "Countries, regions, customer segments, "
                        "or industries."
                    ),
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

            with column2:

                ownership = st.text_area(
                    "Ownership / Founder Structure",
                    placeholder=(
                        "Founder ownership, partners, investors, "
                        "or expected ownership."
                    ),
                    height=120,
                )

                expansion = st.text_area(
                    "Expansion Objectives",
                    placeholder=(
                        "Markets, hiring, fundraising, banking, "
                        "payments, IP, subsidiaries, etc."
                    ),
                    height=120,
                )

                key_risks = st.text_area(
                    "Known Constraints / Risks",
                    placeholder=(
                        "Budget, residency, regulation, tax, "
                        "banking, operational, or timing constraints."
                    ),
                    height=120,
                )

            section_end()

            if st.button(
                "Save Business Profile",
                type="primary",
            ):

                profile_note = (
                    f"\n\n"
                    f"BUSINESS PROFILE — {now_text()}\n"
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
# 12. JURISDICTION LENS
# ============================================================

elif page == "Jurisdiction Lens":

    page_header(
        "Jurisdiction Lens",
        (
            "A structured comparison tool. Scores are internal "
            "decision-support indicators, not legal or tax conclusions."
        ),
    )

    section_start(
        "Business Requirements",
        "Adjust the importance of each criterion for the current client.",
    )

    column1, column2, column3, column4 = st.columns(4)

    with column1:

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

    with column2:

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

    with column3:

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

    with column4:

        w_compliance = st.slider(
            "Compliance Simplicity",
            1,
            5,
            3,
        )

    section_end()

    def calculate_score(
        jurisdiction: dict,
    ) -> float:

        positive_score = (
            jurisdiction["remote_friendliness"]
            * w_remote
            +
            jurisdiction["international_fit"]
            * w_international
            +
            jurisdiction["banking_payment_fit"]
            * w_banking
            +
            jurisdiction["privacy"]
            * w_privacy
            +
            (6 - jurisdiction["cost"])
            * w_cost
            +
            (6 - jurisdiction["formation_complexity"])
            * w_complexity
            +
            (6 - jurisdiction["compliance_complexity"])
            * w_compliance
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
            positive_score / total_weight,
            2,
        )

    results = []

    for jurisdiction in JURISDICTIONS:

        item = jurisdiction.copy()

        item["weighted_indicator"] = (
            calculate_score(jurisdiction)
        )

        results.append(item)

    results.sort(
        key=lambda item:
        item["weighted_indicator"],
        reverse=True,
    )

    st.markdown("### Comparison")

    st.dataframe(
        [
            {
                "Jurisdiction":
                    result["jurisdiction"],

                "Indicator":
                    result["weighted_indicator"],

                "Remote":
                    result["remote_friendliness"],

                "International":
                    result["international_fit"],

                "Banking / Payments":
                    result["banking_payment_fit"],

                "Privacy":
                    result["privacy"],

                "Cost":
                    result["cost"],

                "Formation Complexity":
                    result["formation_complexity"],

                "Compliance Complexity":
                    result["compliance_complexity"],
            }
            for result in results
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Higher indicator values reflect stronger alignment "
        "with the selected internal criteria. This does not "
        "constitute a legal, tax, banking, or regulatory recommendation."
    )

    st.markdown("### Jurisdiction Profiles")

    for result in results:

        with st.expander(
            f"{result['jurisdiction']} "
            f"— indicator {result['weighted_indicator']}"
        ):

            st.write(
                result["summary"]
            )

            st.write(
                f"**Primary source family:** "
                f"{result['source']}"
            )

            st.write(
                f"**Remote friendliness:** "
                f"{result['remote_friendliness']}/5 · "
                f"**International fit:** "
                f"{result['international_fit']}/5 · "
                f"**Banking/payment fit:** "
                f"{result['banking_payment_fit']}/5"
            )

            st.write(
                f"**Formation complexity:** "
                f"{result['formation_complexity']}/5 · "
                f"**Compliance complexity:** "
                f"{result['compliance_complexity']}/5 · "
                f"**Privacy:** "
                f"{result['privacy']}/5"
            )


# ============================================================
# 13. FORMATION ROADMAP
# ============================================================

elif page == "Formation Roadmap":

    page_header(
        "Formation Roadmap",
        "Generate a practical sequence from business objective to operating company.",
    )

    section_start(
        "Formation Planning Inputs",
        (
            "This is a planning framework. Exact legal, tax, "
            "banking, and regulatory requirements must be verified "
            "for the selected jurisdiction."
        ),
    )

    column1, column2 = st.columns(2)

    with column1:

        founder_country = st.text_input(
            "Founder Residence / Country",
            value="Nigeria",
        )

        target_jurisdiction = st.selectbox(
            "Target Jurisdiction",
            [
                jurisdiction["jurisdiction"]
                for jurisdiction in JURISDICTIONS
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

    with column2:

        banking_needed = st.checkbox(
            "Business banking required",
            True,
        )

        payment_gateway = st.checkbox(
            "International payment gateway required",
            True,
        )

        contractors = st.checkbox(
            "International contractors expected",
            False,
        )

        fundraising = st.checkbox(
            "External fundraising expected",
            False,
        )

        ip_protection = st.checkbox(
            "Formal IP protection / ownership required",
            True,
        )

    section_end()

    if st.button(
        "Generate Formation Roadmap",
        type="primary",
    ):

        steps = [
            (
                "01",
                "Define entity purpose",
                (
                    "Document business model, target customers, "
                    "ownership, and intended activities."
                ),
            ),
            (
                "02",
                "Validate jurisdiction",
                (
                    f"Verify the suitability of "
                    f"{target_jurisdiction} against current legal, "
                    "tax, banking, and operational requirements."
                ),
            ),
            (
                "03",
                "Prepare formation information",
                (
                    "Collect founder identity information, "
                    "registered-agent details where applicable, "
                    "ownership information, and company purpose."
                ),
            ),
            (
                "04",
                "Form the entity",
                (
                    "Complete the applicable company registration "
                    "process and retain official formation records."
                ),
            ),
            (
                "05",
                "Establish governance records",
                (
                    "Maintain operating agreement, resolutions, "
                    "ownership records, and other core corporate "
                    "documents as applicable."
                ),
            ),
            (
                "06",
                "Tax / identification setup",
                (
                    "Determine and obtain applicable tax "
                    "identification and registrations."
                ),
            ),
            (
                "07",
                "Banking and payments",
                (
                    "Apply for business banking and payment "
                    "infrastructure, subject to provider eligibility "
                    "and compliance review."
                ),
            ),
            (
                "08",
                "Operational infrastructure",
                (
                    "Set up accounting, contracts, invoicing, "
                    "document storage, security, and internal controls."
                ),
            ),
            (
                "09",
                "Compliance calendar",
                (
                    "Create recurring filing, tax, reporting, "
                    "licence, and registered-agent obligations."
                ),
            ),
            (
                "10",
                "Launch and monitor",
                (
                    "Begin operations and continuously monitor "
                    "corporate, financial, commercial, and "
                    "compliance state."
                ),
            ),
        ]

        if contractors:

            steps.insert(
                8,
                (
                    "09A",
                    "Contractor framework",
                    (
                        "Create contractor agreements, onboarding "
                        "controls, IP assignment terms, confidentiality "
                        "provisions, and payment processes as appropriate."
                    ),
                ),
            )

        if fundraising:

            steps.insert(
                9,
                (
                    "09B",
                    "Capital-readiness",
                    (
                        "Organise cap table, financial records, "
                        "governance documents, IP ownership, and "
                        "investor materials."
                    ),
                ),
            )

        if ip_protection:

            steps.insert(
                8,
                (
                    "08A",
                    "IP ownership",
                    (
                        "Confirm that software, branding, documentation, "
                        "designs, and contractor-created work are properly "
                        "owned or licensed by the company."
                    ),
                ),
            )

        st.markdown(
            "### Recommended Planning Sequence"
        )

        for number, title, description in steps:

            st.markdown(
                f"""
                <div class="section-card">

                    <div style="
                        display:flex;
                        gap:16px;
                        align-items:flex-start;
                    ">

                        <div style="
                            color:#d7b45a;
                            font-size:1.3rem;
                            font-weight:800;
                            min-width:42px;
                        ">
                            {number}
                        </div>

                        <div>

                            <div style="
                                font-weight:800;
                                color:#fff;
                                font-size:1.05rem;
                            ">
                                {title}
                            </div>

                            <div
                                class="small-note"
                                style="margin-top:.3rem;"
                            >
                                {description}
                            </div>

                        </div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# 14. COMPLIANCE
# ============================================================

elif page == "Compliance":

    page_header(
        "Compliance Checklist",
        "Track recurring operational and corporate obligations at a high level.",
    )

    jurisdiction = st.selectbox(
        "Operating / Formation Jurisdiction",
        [
            item["jurisdiction"]
            for item in JURISDICTIONS
        ],
    )

    checklist = [
        "Maintain formation and governance records",
        "Maintain registered agent / official address requirements where applicable",
        "Track annual reports / periodic company filings",
        "Track federal, state, or local tax obligations",
        "Maintain accounting and financial records",
        "Reconcile business bank accounts",
        "Review payment-provider compliance requirements",
        "Maintain client contracts and engagement records",
        "Maintain contractor agreements and IP provisions",
        "Review licences / permits relevant to business activity",
        "Review data protection and privacy obligations",
        "Review cybersecurity and access controls",
        "Review beneficial ownership / reporting requirements where applicable",
        "Maintain business continuity and document backups",
    ]

    st.markdown(
        f"### Checklist — {jurisdiction}"
    )

    completed = []

    for index, item in enumerate(checklist):

        if st.checkbox(
            item,
            key=f"compliance_{index}",
        ):

            completed.append(item)

    progress = (
        len(completed) / len(checklist)
    )

    st.progress(progress)

    st.caption(
        f"{len(completed)} of "
        f"{len(checklist)} items marked complete."
    )

    st.warning(
        "Compliance requirements vary by jurisdiction, entity type, "
        "activity, ownership, residency, and changes in law. "
        "Verify current obligations with appropriate professionals "
        "and official authorities."
    )


# ============================================================
# 15. REPORT GENERATOR
# ============================================================

elif page == "Report Generator":

    page_header(
        "Report Generator",
        "Generate and save a structured client-facing or internal advisory report.",
    )

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
            "Create a client record first in Client Intake."
        )

    else:

        labels = {
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
            list(labels.keys()),
            format_func=lambda value: labels[value],
        )

        client = fetch_one(
            "SELECT * FROM clients WHERE id = ?",
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
            placeholder=(
                "Add findings, assumptions, questions, "
                "or recommendations that should appear in the report."
            ),
        )

        if st.button(
            "Generate & Save Report",
            type="primary",
        ):

            timestamp = now_text()

            report = f"""# PieroloOS — {report_type}

**PieroloCorp International LLC**

## Client

- **Name:** {client['client_name']}
- **Business:** {client['business_name'] or 'Not specified'}
- **Country:** {client['country'] or 'Not specified'}
- **Service:** {client['service']}
- **Engagement Status:** {client['status']}
- **Generated:** {timestamp}

## Business Information

{client['notes'] or 'No additional business information has been recorded.'}

## Additional Context

{additional_context or 'No additional context provided.'}

## Operating Considerations

1. Verify material facts against primary sources.
2. Confirm jurisdiction-specific legal, tax, banking, and regulatory requirements.
3. Separate factual findings from assumptions.
4. Record client decisions and approvals.
5. Preserve supporting documents and evidence.
6. Update the engagement record as the matter progresses.

## Disclaimer

This report is generated by PieroloOS as a decision-support and professional-service workflow aid. It is not legal, tax, accounting, financial, immigration, regulatory, or other licensed professional advice. Current requirements should be independently verified with the appropriate qualified professional or official authority.
"""

            safe_name = safe_filename(
                f"{client['client_name']}_"
                f"{report_type}_"
                f"{timestamp}"
            )

            report_path = (
                REPORT_DIR
                / f"{safe_name}.md"
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
                file_name=f"{safe_name}.md",
                mime="text/markdown",
                use_container_width=True,
            )

            with st.expander(
                "Preview Report",
                expanded=True,
            ):

                st.markdown(report)

    st.markdown("### Previous Reports")

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
# 16. ENGAGEMENT RECORDS
# ============================================================

elif page == "Engagement Records":

    page_header(
        "Engagement Records",
        "Maintain a lightweight operational register for active client matters.",
    )

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

        labels = {
            row["id"]:
                row["client_name"]
                + (
                    f" — {row['business_name']}"
                    if row["business_name"]
                    else ""
                )
            for row in clients
        }

        with st.form("engagement_form"):

            selected_client = st.selectbox(
                "Client",
                list(labels.keys()),
                format_func=lambda value:
                    labels[value],
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

            create_engagement = st.form_submit_button(
                "Create Engagement Record",
                type="primary",
                use_container_width=True,
            )

        if create_engagement:

            client_row = fetch_one(
                """
                SELECT client_name
                FROM clients
                WHERE id = ?
                """,
                (selected_client,),
            )

            if client_row:

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
                        client_row["client_name"],
                        service.strip(),
                        status,
                        next_action.strip(),
                        notes.strip(),
                        now_text(),
                    ),
                )

                st.success(
                    "Engagement record created."
                )

                st.rerun()

    else:

        st.info(
            "Create a client record first in Client Intake."
        )

    st.markdown("### Engagement Register")

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

        st.markdown(
            "### Update Engagement Status"
        )

        engagement_ids = [
            row["id"]
            for row in engagements
        ]

        def engagement_label(
            engagement_id: int,
        ) -> str:

            for row in engagements:

                if row["id"] == engagement_id:

                    return (
                        f"#{row['id']} — "
                        f"{row['client_name']} — "
                        f"{row['service'] or 'Service not specified'}"
                    )

            return str(engagement_id)

        selected_engagement = st.selectbox(
            "Select Engagement",
            engagement_ids,
            format_func=engagement_label,
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

        new_next_action = st.text_input(
            "Next Action",
            key="engagement_next_action",
        )

        if st.button(
            "Update Engagement",
            type="primary",
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
                    new_next_action.strip(),
                    now_text(),
                    selected_engagement,
                ),
            )

            st.success(
                "Engagement updated."
            )

            st.rerun()

    else:

        st.info(
            "No engagement records yet."
        )


# ============================================================
# 17. FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        <b>PIEROLOOS v0.1</b>
        · Professional Service Operating System
        · PieroloCorp International LLC

        <br>

        Decision-support prototype · Verify legal, tax,
        regulatory, banking, and compliance matters with
        appropriate professionals and official authorities.

    </div>
    """,
    unsafe_allow_html=True,
)
