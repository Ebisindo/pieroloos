"""
PIEROLOOS v0.1 — Core MVP + Premium UX/UI
PieroloCorp International LLC

============================================================
PURPOSE
============================================================

PieroloOS is a professional-service operating system MVP for:

1. Client Intake
2. Business Profile
3. Jurisdiction Lens
4. Formation Roadmap
5. Compliance Checklist
6. Report Generator
7. Engagement Records
8. Basic engagement-state management

============================================================
RUN
============================================================

pip install -r requirements.txt
streamlit run app.py

============================================================
EXPECTED REPOSITORY STRUCTURE
============================================================

pieroloos/
│
├── app.py
├── requirements.txt
│
└── assets/
    ├── pieroloos_background.svg
    └── pierolocorp_logo.png

============================================================
IMPORTANT
============================================================

This is an MVP and decision-support prototype.

Jurisdiction information is an editable research dataset and
must be verified against current authoritative sources before
client delivery.

Generated reports are decision-support drafts and do not
constitute legal, tax, accounting, regulatory, investment,
or other professional advice.
"""

from __future__ import annotations

import base64
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_NAME = "PieroloOS"
APP_VERSION = "v0.1"

DB_PATH = Path("pieroloos.db")

ASSET_DIR = Path("assets")
EXPORT_DIR = Path("reports")

EXPORT_DIR.mkdir(exist_ok=True)


st.set_page_config(
    page_title=f"{APP_NAME} {APP_VERSION}",
    page_icon="P",
    layout="wide",
    initial_sidebar_state="auto",
)


# ============================================================
# ASSET HELPERS
# ============================================================

def asset_uri(path: Path) -> str:
    """
    Convert an image/SVG file into a Base64 data URI.

    This makes the background work reliably on Streamlit Cloud
    without requiring an external URL.
    """

    if not path.exists():
        return ""

    try:
        if path.suffix.lower() == ".svg":
            mime = "image/svg+xml"
        elif path.suffix.lower() in [".jpg", ".jpeg"]:
            mime = "image/jpeg"
        else:
            mime = "image/png"

        encoded = base64.b64encode(path.read_bytes()).decode("ascii")

        return f"data:{mime};base64,{encoded}"

    except Exception:
        return ""


BACKGROUND_PATH = ASSET_DIR / "pieroloos_background.svg"
LOGO_PATH = ASSET_DIR / "pierolocorp_logo.png"

BG_URI = asset_uri(BACKGROUND_PATH)


# ============================================================
# DATABASE
# ============================================================

def db() -> sqlite3.Connection:
    """
    Open SQLite database connection.
    """

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


def init_db() -> None:
    """
    Create MVP database tables.
    """

    conn = db()

    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS engagements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            client_name TEXT NOT NULL,
            business_name TEXT,
            objective TEXT,
            service_type TEXT,
            status TEXT DEFAULT 'Intake',
            data_json TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            engagement_id INTEGER,
            decision_question TEXT,
            decision TEXT,
            rationale TEXT,
            data_json TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            engagement_id INTEGER,
            filename TEXT,
            report_type TEXT,
            data_json TEXT
        )
        """
    )

    conn.commit()

    conn.close()


init_db()


# ============================================================
# TIME / GENERAL HELPERS
# ============================================================

def now_iso() -> str:
    """
    Return UTC timestamp.
    """

    return datetime.utcnow().replace(
        microsecond=0
    ).isoformat() + "Z"


def safe_filename(value: str) -> str:
    """
    Convert text into a safe filename.
    """

    cleaned = "".join(
        character
        if character.isalnum() or character in ("-", "_")
        else "_"
        for character in value.strip()
    )

    return cleaned[:80] or "engagement"


def score_label(score: float) -> str:
    """
    Convert a 1–5 score to a readable label.
    """

    if score >= 4.5:
        return "Very strong"

    if score >= 3.5:
        return "Strong"

    if score >= 2.5:
        return "Moderate"

    if score >= 1.5:
        return "Lower"

    return "Very low"


# ============================================================
# DATABASE OPERATIONS
# ============================================================

def save_engagement(data: Dict[str, Any]) -> int:
    """
    Create a new engagement.
    """

    conn = db()

    timestamp = now_iso()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO engagements
        (
            created_at,
            updated_at,
            client_name,
            business_name,
            objective,
            service_type,
            status,
            data_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            timestamp,
            data.get("client_name", ""),
            data.get("business_name", ""),
            data.get("objective", ""),
            data.get("service_type", ""),
            "Intake",
            json.dumps(
                data,
                ensure_ascii=False,
            ),
        ),
    )

    engagement_id = int(cursor.lastrowid)

    conn.commit()

    conn.close()

    return engagement_id


def load_engagements() -> List[sqlite3.Row]:
    """
    Return all engagements.
    """

    conn = db()

    rows = conn.execute(
        """
        SELECT *
        FROM engagements
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return rows


def load_engagement(
    engagement_id: int,
) -> Optional[sqlite3.Row]:
    """
    Load a single engagement.
    """

    conn = db()

    row = conn.execute(
        """
        SELECT *
        FROM engagements
        WHERE id = ?
        """,
        (engagement_id,),
    ).fetchone()

    conn.close()

    return row


def update_engagement_status(
    engagement_id: int,
    status: str,
) -> None:
    """
    Update engagement status.
    """

    conn = db()

    conn.execute(
        """
        UPDATE engagements
        SET status = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            status,
            now_iso(),
            engagement_id,
        ),
    )

    conn.commit()

    conn.close()


def save_report_record(
    engagement_id: Optional[int],
    filename: str,
    report_type: str,
) -> None:
    """
    Record report generation.
    """

    conn = db()

    conn.execute(
        """
        INSERT INTO reports
        (
            created_at,
            engagement_id,
            filename,
            report_type,
            data_json
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            now_iso(),
            engagement_id,
            filename,
            report_type,
            json.dumps(
                {
                    "application": APP_NAME,
                    "version": APP_VERSION,
                }
            ),
        ),
    )

    conn.commit()

    conn.close()


def report_count() -> int:
    """
    Return total generated reports.
    """

    conn = db()

    result = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM reports
        """
    ).fetchone()

    conn.close()

    return int(result["total"])


# ============================================================
# BUSINESS PROFILE
# ============================================================

def build_profile(
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert raw intake into structured business profile.
    """

    return {
        "client": data.get("client_name"),
        "business": data.get("business_name"),
        "business_model": data.get("business_model"),
        "industry": data.get("industry"),
        "customer_market": data.get("customer_market"),
        "owner_residence": data.get("owner_residence"),
        "target_jurisdictions": data.get(
            "target_jurisdictions"
        ),
        "capital": data.get("capital"),
        "employees": data.get("employees"),
        "payment_needs": data.get("payment_needs"),
        "service": data.get("service_type"),
        "objective": data.get("objective"),
        "constraints": data.get("constraints"),
    }


# ============================================================
# JURISDICTION RESEARCH DATASET
# ============================================================

JURISDICTIONS: Dict[str, Dict[str, Any]] = {

    "United States — New Mexico": {
        "code": "US-NM",
        "entity": "LLC",
        "currency": "USD",

        "formation_complexity": 2,
        "cost_index": 2,
        "remote_friendliness": 5,
        "international_business_fit": 4,
        "banking_payment_fit": 4,
        "compliance_complexity": 3,
        "privacy_index": 4,

        "notes": (
            "Initial research profile only. "
            "Verify current federal and state obligations."
        ),

        "official_sources": [
            "New Mexico Secretary of State",
            "IRS",
        ],
    },

    "United States — Delaware": {
        "code": "US-DE",
        "entity": "LLC",
        "currency": "USD",

        "formation_complexity": 3,
        "cost_index": 3,
        "remote_friendliness": 5,
        "international_business_fit": 5,
        "banking_payment_fit": 5,
        "compliance_complexity": 3,
        "privacy_index": 4,

        "notes": (
            "Common commercial jurisdiction. "
            "Current obligations and fees require verification."
        ),

        "official_sources": [
            "Delaware Division of Corporations",
            "IRS",
        ],
    },

    "United Kingdom": {
        "code": "GB",
        "entity": "Private limited company",
        "currency": "GBP",

        "formation_complexity": 2,
        "cost_index": 2,
        "remote_friendliness": 4,
        "international_business_fit": 4,
        "banking_payment_fit": 4,
        "compliance_complexity": 4,
        "privacy_index": 3,

        "notes": (
            "Initial comparison profile only. "
            "Verify Companies House and HMRC requirements."
        ),

        "official_sources": [
            "Companies House",
            "HM Revenue & Customs",
        ],
    },

    "Nigeria": {
        "code": "NG",
        "entity": "Limited Liability Company",
        "currency": "NGN",

        "formation_complexity": 2,
        "cost_index": 1,
        "remote_friendliness": 3,
        "international_business_fit": 3,
        "banking_payment_fit": 3,
        "compliance_complexity": 4,
        "privacy_index": 3,

        "notes": (
            "Initial comparison profile only. "
            "Verify CAC, FIRS and other applicable requirements."
        ),

        "official_sources": [
            "Corporate Affairs Commission",
            "Federal Inland Revenue Service",
        ],
    },
}


# ============================================================
# JURISDICTION ENGINE
# ============================================================

def compare_jurisdictions(
    selected: List[str],
    priorities: Dict[str, float],
) -> List[Dict[str, Any]]:

    results = []

    for name in selected:

        item = JURISDICTIONS[name]

        weighted = (
            item["formation_complexity"]
            * priorities["formation"]

            + (6 - item["cost_index"])
            * priorities["cost"]

            + item["remote_friendliness"]
            * priorities["remote"]

            + item["international_business_fit"]
            * priorities["international"]

            + item["banking_payment_fit"]
            * priorities["payments"]

            + (6 - item["compliance_complexity"])
            * priorities["compliance"]

            + item["privacy_index"]
            * priorities["privacy"]
        )

        denominator = (
            sum(priorities.values())
            * 5
        )

        normalized = (
            round(
                (weighted / denominator)
                * 100,
                1,
            )
            if denominator
            else 0
        )

        results.append(
            {
                "jurisdiction": name,
                "entity": item["entity"],
                "score": normalized,
                "score_label": score_label(
                    normalized / 20
                ),
                "notes": item["notes"],
                "sources": item["official_sources"],
            }
        )

    return sorted(
        results,
        key=lambda x: x["score"],
        reverse=True,
    )


# ============================================================
# FORMATION ROADMAP
# ============================================================

def formation_roadmap(
    _: Dict[str, Any],
) -> List[str]:

    return [
        "Confirm business objective, customer, activities and target markets.",

        "Confirm proposed entity architecture and jurisdictions "
        "for professional review.",

        "Confirm name availability and formation requirements.",

        "Prepare formation information and required "
        "identification/documentation.",

        "File formation documents through the appropriate "
        "authority/provider.",

        "Establish the company's core records and governance "
        "documentation.",

        "Establish appropriate business banking/payment infrastructure.",

        "Set up accounting, invoicing and transaction-record controls.",

        "Establish applicable tax/compliance calendar.",

        "Establish contracts, IP ownership and confidentiality controls.",

        "Complete operational onboarding and launch checklist.",

        "Schedule a post-formation review after the first "
        "operating period.",
    ]


# ============================================================
# COMPLIANCE CHECKLIST
# ============================================================

def compliance_checklist(
    _: Dict[str, Any],
) -> List[Dict[str, str]]:

    return [

        {
            "item": "Entity status",
            "frequency": "As required",
            "status": "Research required",
            "evidence": "Formation/registration record",
        },

        {
            "item": (
                "Registered-agent / "
                "registered-office requirement"
            ),
            "frequency": "Ongoing",
            "status": "Research required",
            "evidence": (
                "Service agreement / official record"
            ),
        },

        {
            "item": (
                "Tax registration and "
                "filing obligations"
            ),
            "frequency": "Jurisdiction-dependent",
            "status": "Professional verification",
            "evidence": (
                "Tax registrations and filings"
            ),
        },

        {
            "item": "Annual / periodic company filing",
            "frequency": "Jurisdiction-dependent",
            "status": "Research required",
            "evidence": (
                "Filed return / confirmation"
            ),
        },

        {
            "item": (
                "Business licence / "
                "regulated activity review"
            ),
            "frequency": "As applicable",
            "status": "Review activity",
            "evidence": (
                "Licence or written determination"
            ),
        },

        {
            "item": "Accounting records",
            "frequency": "Ongoing",
            "status": "Set up",
            "evidence": "Accounting system",
        },

        {
            "item": "Contract and IP records",
            "frequency": "Ongoing",
            "status": "Set up",
            "evidence": "Contract/IP register",
        },

        {
            "item": (
                "Data protection / "
                "privacy obligations"
            ),
            "frequency": "Ongoing",
            "status": "Research required",
            "evidence": (
                "Privacy documentation / controls"
            ),
        },
    ]


# ============================================================
# REPORT GENERATOR
# ============================================================

def render_markdown_report(
    data: Dict[str, Any],
    comparison: List[Dict[str, Any]],
) -> str:

    profile = build_profile(data)

    roadmap = formation_roadmap(data)

    checklist = compliance_checklist(data)

    lines = [

        "# PieroloOS Client Business Formation & Operating Report",

        "",

        (
            f"**Generated:** "
            f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
        ),

        f"**PieroloOS version:** {APP_VERSION}",

        "",

        "## 1. Executive Summary",

        "",

        (
            f"**Client:** "
            f"{profile.get('client') or 'Not provided'}"
        ),

        (
            f"**Business:** "
            f"{profile.get('business') or 'Not provided'}"
        ),

        (
            f"**Objective:** "
            f"{profile.get('objective') or 'Not provided'}"
        ),

        "",

        (
            "This report is an initial decision-support document "
            "generated from client-provided information and the "
            "PieroloOS research dataset. Jurisdiction-specific "
            "legal, tax, regulatory and payment conclusions must "
            "be verified against current authoritative sources "
            "and, where appropriate, qualified professionals."
        ),

        "",

        "## 2. Business Profile",

        "",
    ]

    for key, value in profile.items():

        if value not in (
            None,
            "",
            [],
        ):

            label = (
                key
                .replace("_", " ")
                .title()
            )

            lines.append(
                f"- **{label}:** {value}"
            )

    lines.extend(
        [
            "",
            "## 3. Jurisdiction Lens",
            "",
        ]
    )

    if comparison:

        for index, result in enumerate(
            comparison,
            start=1,
        ):

            lines.extend(
                [
                    f"### {index}. "
                    f"{result['jurisdiction']}",

                    (
                        f"- Entity: "
                        f"{result['entity']}"
                    ),

                    (
                        f"- Internal fit score: "
                        f"{result['score']}/100"
                    ),

                    (
                        f"- Interpretation: "
                        f"{result['score_label']}"
                    ),

                    (
                        f"- Notes: "
                        f"{result['notes']}"
                    ),

                    (
                        "- Primary sources to verify: "
                        + ", ".join(
                            result["sources"]
                        )
                    ),

                    "",
                ]
            )

    else:

        lines.append(
            "No jurisdictions selected."
        )

    lines.extend(
        [
            "## 4. Formation Roadmap",
            "",
        ]
    )

    for item in roadmap:

        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            "## 5. Compliance Checklist",
            "",
        ]
    )

    for item in checklist:

        lines.append(
            f"- **{item['item']}** — "
            f"{item['frequency']} — "
            f"{item['status']} — "
            f"Evidence: {item['evidence']}"
        )

    lines.extend(
        [
            "",
            "## 6. Key Risks and Verification Points",
            "",

            "- Confirm the legal/tax implications of the proposed structure.",

            "- Verify current government fees, filing deadlines "
            "and registration rules.",

            "- Verify payment processor eligibility and "
            "prohibited/restricted activities.",

            "- Confirm whether intended services trigger "
            "licensing or regulated activity rules.",

            "- Establish written IP/confidentiality arrangements "
            "before contractor development.",

            "- Keep company and personal finances appropriately separated.",

            "",
            "## 7. Next Actions",
            "",

            "1. Verify jurisdiction data against current primary sources.",

            "2. Confirm the proposed entity and operating structure "
            "with the appropriate professional.",

            "3. Confirm payment/banking requirements.",

            "4. Establish company records, accounting and "
            "compliance calendar.",

            "5. Approve the final formation roadmap.",

            "",
            "---",
            "",

            "**PieroloOS:** Operating intelligence and "
            "decision-support layer for PieroloCorp International LLC.",
        ]
    )

    return "\n".join(lines)


# ============================================================
# UX/UI THEME
# ============================================================

def inject_theme() -> None:

    bg = BG_URI

    st.markdown(
        f"""
        <style>

        /* =====================================================
           ROOT DESIGN SYSTEM
           ===================================================== */

        :root {{

            --po-navy:
                #050817;

            --po-navy-2:
                #0b1028;

            --po-navy-3:
                #101735;

            --po-purple:
                #8b5cf6;

            --po-purple-2:
                #6d28d9;

            --po-purple-soft:
                #a855f7;

            --po-gold:
                #f4c64e;

            --po-gold-light:
                #ffe9a3;

            --po-text:
                #f7f7fb;

            --po-muted:
                #a9aec7;

            --po-border:
                rgba(139, 92, 246, .25);

            --po-border-gold:
                rgba(244, 198, 78, .35);

        }}


        /* =====================================================
           APPLICATION BACKGROUND
           ===================================================== */

        [data-testid="stAppViewContainer"] {{

            background:
                linear-gradient(
                    rgba(2, 5, 18, .80),
                    rgba(2, 5, 18, .94)
                ),
                url('{bg}') center top / cover fixed no-repeat;

            color:
                var(--po-text);

        }}


        /* =====================================================
           MAIN CONTENT
           ===================================================== */

        .main .block-container {{

            max-width:
                1500px;

            padding-top:
                1.4rem;

            padding-bottom:
                2rem;

        }}


        /* =====================================================
           STREAMLIT HEADER
           ===================================================== */

        [data-testid="stHeader"] {{

            background:
                rgba(3, 6, 18, .78);

            border-bottom:
                1px solid
                rgba(139, 92, 246, .20);

        }}


        /* =====================================================
           SIDEBAR
           ===================================================== */

        [data-testid="stSidebar"] {{

            background:
                linear-gradient(
                    180deg,
                    rgba(8, 12, 36, .99),
                    rgba(3, 6, 22, .99)
                );

            border-right:
                1px solid
                rgba(139, 92, 246, .25);

        }}


        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{

            gap:
                .35rem;

        }}


        /* =====================================================
           BRAND
           ===================================================== */

        .po-brand {{

            padding:
                .5rem
                .25rem
                1rem;

            text-align:
                center;

            border-bottom:
                1px solid
                rgba(139, 92, 246, .24);

            margin-bottom:
                .75rem;

        }}


        .po-brand img {{

            max-width:
                90%;

            width:
                185px;

            filter:
                drop-shadow(
                    0 0 16px
                    rgba(139, 92, 246, .38)
                );

        }}


        /* =====================================================
           TYPOGRAPHY
           ===================================================== */

        .po-kicker {{

            color:
                var(--po-gold);

            font-size:
                .72rem;

            letter-spacing:
                .28em;

            text-transform:
                uppercase;

            font-weight:
                750;

        }}


        .po-section-title {{

            color:
                #ffffff;

            font-size:
                1.45rem;

            font-weight:
                800;

            margin-top:
                1.2rem;

            margin-bottom:
                .15rem;

        }}


        .po-section-sub {{

            color:
                var(--po-muted);

            font-size:
                .92rem;

            margin-bottom:
                1rem;

        }}


        /* =====================================================
           HERO
           ===================================================== */

        .po-hero {{

            position:
                relative;

            overflow:
                hidden;

            border:
                1px solid
                var(--po-border);

            border-radius:
                24px;

            padding:
                2.5rem;

            margin:
                .2rem
                0
                1.4rem;

            min-height:
                365px;

            background:
                linear-gradient(
                    90deg,
                    rgba(4, 7, 22, .97) 0%,
                    rgba(4, 7, 22, .84) 40%,
                    rgba(4, 7, 22, .45) 75%,
                    rgba(4, 7, 22, .25) 100%
                ),
                url('{bg}') center / cover no-repeat;

            box-shadow:
                0 28px 90px
                rgba(0, 0, 0, .38);

        }}


        .po-hero::after {{

            content:
                "";

            position:
                absolute;

            inset:
                0;

            pointer-events:
                none;

            background:
                linear-gradient(
                    135deg,
                    rgba(139, 92, 246, .08),
                    transparent 40%,
                    rgba(244, 198, 78, .05)
                );

        }}


        .po-hero-content {{

            position:
                relative;

            z-index:
                2;

        }}


        .po-hero h1 {{

            font-family:
                Georgia,
                "Times New Roman",
                serif;

            font-size:
                clamp(
                    3rem,
                    7vw,
                    5.8rem
                );

            line-height:
                .92;

            margin:
                .35rem
                0
                .8rem;

            color:
                #ffffff;

            letter-spacing:
                -.045em;

            text-shadow:
                0 5px 30px
                rgba(0, 0, 0, .4);

        }}


        .po-hero .tagline {{

            color:
                var(--po-gold);

            font-size:
                1.22rem;

            font-weight:
                750;

            max-width:
                650px;

            line-height:
                1.4;

        }}


        .po-hero .copy {{

            color:
                #c8cce0;

            max-width:
                680px;

            line-height:
                1.7;

            margin-top:
                .8rem;

            font-size:
                .98rem;

        }}


        .po-rule {{

            height:
                1px;

            max-width:
                620px;

            background:
                linear-gradient(
                    90deg,
                    transparent,
                    var(--po-gold),
                    transparent
                );

            margin:
                1.35rem
                0;

            opacity:
                .65;

        }}


        /* =====================================================
           KPI CARDS
           ===================================================== */

        div[data-testid="stMetric"] {{

            background:
                linear-gradient(
                    145deg,
                    rgba(20, 25, 55, .86),
                    rgba(8, 12, 31, .92)
                );

            border:
                1px solid
                rgba(139, 92, 246, .22);

            border-radius:
                18px;

            padding:
                1rem;

            min-height:
                115px;

            box-shadow:
                0 16px 45px
                rgba(0, 0, 0, .18);

        }}


        div[data-testid="stMetric"] label {{

            color:
                #aeb3ca;

        }}


        div[data-testid="stMetricValue"] {{

            color:
                #ffffff;

        }}


        /* =====================================================
           MODULE CARDS
           ===================================================== */

        .po-card {{

            background:
                linear-gradient(
                    145deg,
                    rgba(20, 25, 55, .86),
                    rgba(8, 12, 31, .92)
                );

            border:
                1px solid
                rgba(139, 92, 246, .22);

            border-radius:
                18px;

            padding:
                1.25rem;

            min-height:
                150px;

            box-shadow:
                0 14px 40px
                rgba(0, 0, 0, .18);

            transition:
                transform .2s ease,
                border-color .2s ease,
                box-shadow .2s ease;

        }}


        .po-card:hover {{

            transform:
                translateY(-3px);

            border-color:
                rgba(244, 198, 78, .45);

            box-shadow:
                0 20px 55px
                rgba(80, 45, 150, .18);

        }}


        .po-card .icon {{

            font-size:
                1.7rem;

            margin-bottom:
                .5rem;

        }}


        .po-card .title {{

            color:
                #ffffff;

            font-weight:
                800;

            font-size:
                1rem;

        }}


        .po-card .desc {{

            color:
                var(--po-muted);

            font-size:
                .84rem;

            line-height:
                1.45;

            margin-top:
                .35rem;

        }}


        /* =====================================================
           BUTTONS
           ===================================================== */

        .stButton > button,
        .stDownloadButton > button {{

            border-radius:
                12px !important;

            border:
                1px solid
                rgba(139, 92, 246, .45) !important;

            background:
                rgba(18, 22, 52, .90) !important;

            color:
                #ffffff !important;

            min-height:
                2.65rem;

            font-weight:
                700 !important;

            transition:
                all .2s ease;

        }}


        .stButton > button:hover,
        .stDownloadButton > button:hover {{

            border-color:
                var(--po-gold) !important;

            box-shadow:
                0 0 22px
                rgba(139, 92, 246, .20);

            transform:
                translateY(-1px);

        }}


        .stButton > button[kind="primary"] {{

            background:
                linear-gradient(
                    135deg,
                    #f7d15b,
                    #d99a1e
                ) !important;

            color:
                #090b18 !important;

            border-color:
                #f7d15b !important;

        }}


        /* =====================================================
           FORM CONTROLS
           ===================================================== */

        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea {{

            background:
                rgba(9, 13, 33, .82) !important;

            color:
                #ffffff !important;

            border-color:
                rgba(139, 92, 246, .30) !important;

            border-radius:
                10px !important;

        }}


        /* =====================================================
           EXPANDERS
           ===================================================== */

        [data-testid="stExpander"] {{

            background:
                rgba(10, 15, 36, .72);

            border:
                1px solid
                rgba(139, 92, 246, .20);

            border-radius:
                14px;

        }}


        /* =====================================================
           ALERTS
           ===================================================== */

        [data-testid="stAlert"] {{

            border-radius:
                14px;

        }}


        /* =====================================================
           FOOTER
           ===================================================== */

        .po-footer {{

            margin-top:
                2.5rem;

            padding:
                1.3rem
                0
                .5rem;

            border-top:
                1px solid
                rgba(139, 92, 246, .18);

            color:
                #9da2bd;

            font-size:
                .82rem;

        }}


        .po-footer-right {{

            float:
                right;

            color:
                #b7bad0;

        }}


        /* =====================================================
           MOBILE / TABLET
           ===================================================== */

        @media (max-width: 768px) {{

            .main .block-container {{

                padding-left:
                    .8rem;

                padding-right:
                    .8rem;

                padding-top:
                    .8rem;

            }}


            .po-hero {{

                padding:
                    1.45rem;

                min-height:
                    330px;

                border-radius:
                    18px;

            }}


            .po-hero h1 {{

                font-size:
                    3rem;

            }}


            .po-hero .tagline {{

                font-size:
                    1rem;

            }}


            .po-hero .copy {{

                font-size:
                    .88rem;

            }}


            .po-card {{

                min-height:
                    120px;

            }}


            .po-footer-right {{

                float:
                    none;

                display:
                    block;

                margin-top:
                    .6rem;

            }}

        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


inject_theme()


# ============================================================
# SESSION STATE
# ============================================================

if "intake" not in st.session_state:
    st.session_state.intake = {}

if "comparison" not in st.session_state:
    st.session_state.comparison = []

if "report" not in st.session_state:
    st.session_state.report = ""

if "current_engagement_id" not in st.session_state:
    st.session_state.current_engagement_id = None

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Command Center"


# ============================================================
# NAVIGATION
# ============================================================

PAGES = [
    "Command Center",
    "Client Intake",
    "Business Profile",
    "Jurisdiction Lens",
    "Formation Roadmap",
    "Compliance",
    "Report Generator",
    "Engagement Records",
]


def go_to(page: str) -> None:
    """
    Dashboard quick-access callback.
    """

    st.session_state.nav_page = page


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    if LOGO_PATH.exists():

        st.markdown(
            '<div class="po-brand">',
            unsafe_allow_html=True,
        )

        st.image(
            str(LOGO_PATH),
            width=185,
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="po-brand">
                <div class="po-kicker">
                    PIEROLO
                </div>
                <h2 style="color:white;">
                    PieroloOS
                </h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(
        "Professional Service Operating System "
        f"• {APP_VERSION}"
    )

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    st.session_state.nav_page = st.radio(
        "Operating module",
        PAGES,
        key="navigation_radio",
        index=PAGES.index(
            st.session_state.nav_page
        ),
    )

    st.divider()

    # --------------------------------------------------------
    # MVP CONTROL STATUS
    # --------------------------------------------------------

    st.caption(
        "MVP CONTROL STATUS"
    )

    st.write(
        "Evidence-aware: ✓"
    )

    st.write(
        "Human approval: ✓"
    )

    st.write(
        "SQLite records: ✓"
    )

    st.write(
        "Responsive UI: ✓"
    )

    st.write(
        "Authoritative-source verification: Required"
    )

    st.divider()

    st.caption(
        "On tablet/mobile, use the native "
        "☰ Streamlit menu to open or close "
        "the operating system navigation."
    )


# ============================================================
# CURRENT PAGE
# ============================================================

page = st.session_state.nav_page


# ============================================================
# COMMAND CENTER
# ============================================================

if page == "Command Center":

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.markdown(
        """
        <section class="po-hero">

            <div class="po-hero-content">

                <div class="po-kicker">
                    Welcome to
                </div>

                <h1>
                    PieroloOS
                </h1>

                <div class="tagline">
                    Turn Global Opportunity into Real
                    Business Structures.
                </div>

                <div class="copy">
                    Your operating system for business
                    formation, jurisdiction intelligence,
                    compliance planning and global expansion.
                </div>

                <div class="po-rule"></div>

                <div class="po-kicker">
                    FORMATION
                    &nbsp; | &nbsp;
                    COMPLIANCE
                    &nbsp; | &nbsp;
                    INTELLIGENCE
                    &nbsp; | &nbsp;
                    EXECUTION
                </div>

            </div>

        </section>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # DASHBOARD DATA
    # --------------------------------------------------------

    rows = load_engagements()

    active_count = sum(
        1
        for row in rows
        if row["status"] != "Closed"
    )

    total_reports = report_count()

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    st.markdown(
        '<div class="po-section-title">'
        'Operating Overview'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="po-section-sub">'
        'A high-level view of the current engagement environment.'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Engagements",
        len(rows),
    )

    c2.metric(
        "Active Engagements",
        active_count,
    )

    c3.metric(
        "Reports Generated",
        total_reports,
    )

    c4.metric(
        "Jurisdictions Available",
        len(JURISDICTIONS),
    )

    # --------------------------------------------------------
    # QUICK ACCESS
    # --------------------------------------------------------

    st.markdown(
        '<div class="po-section-title">'
        'Quick Access'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="po-section-sub">'
        'Move from idea to execution — all in one place.'
        '</div>',
        unsafe_allow_html=True,
    )

    cards = [

        (
            "👤",
            "Client Intake",
            "Capture client requirements.",
            "Client Intake",
        ),

        (
            "▣",
            "Business Profile",
            "Structure business information.",
            "Business Profile",
        ),

        (
            "◎",
            "Jurisdiction Lens",
            "Compare and analyse jurisdictions.",
            "Jurisdiction Lens",
        ),

        (
            "☷",
            "Formation Roadmap",
            "Plan implementation steps.",
            "Formation Roadmap",
        ),

        (
            "◈",
            "Compliance",
            "Track obligations.",
            "Compliance",
        ),

        (
            "▤",
            "Report Generator",
            "Create professional reports.",
            "Report Generator",
        ),
    ]

    cols = st.columns(3)

    for index, (
        icon,
        title,
        description,
        target,
    ) in enumerate(cards):

        with cols[index % 3]:

            st.markdown(
                f"""
                <div class="po-card">

                    <div class="icon">
                        {icon}
                    </div>

                    <div class="title">
                        {title}
                    </div>

                    <div class="desc">
                        {description}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            st.button(
                f"Open {title} →",
                key=f"quick_{index}",
                on_click=go_to,
                args=(target,),
            )

    # --------------------------------------------------------
    # OPERATING LOOP
    # --------------------------------------------------------

    st.markdown(
        '<div class="po-section-title">'
        'Operating Loop'
        '</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "Intake → Classify → Verify → Assess → "
        "Plan → Approve → Execute → Verify → "
        "Record → Close → Learn"
    )

    # --------------------------------------------------------
    # DISCLAIMER
    # --------------------------------------------------------

    st.warning(
        "This MVP is a workflow and decision-support "
        "prototype. It does not replace legal, tax, "
        "accounting, regulatory or other professional review."
    )


# ============================================================
# CLIENT INTAKE
# ============================================================

elif page == "Client Intake":

    st.title(
        "Client Intake"
    )

    st.caption(
        "Structured intake → reusable business data"
    )

    with st.form(
        "client_intake_form"
    ):

        st.markdown(
            "### Client Identity"
        )

        client_name = st.text_input(
            "Client / founder name",
        )

        business_name = st.text_input(
            "Proposed business name",
        )

        service_type = st.selectbox(
            "Primary service",
            [
                "Business formation",
                "Business structure review",
                "Jurisdiction comparison",
                "Compliance setup",
                "Business consulting",
                "PieroloOS SaaS",
                "Other",
            ],
        )

        st.markdown(
            "### Business Context"
        )

        objective = st.text_area(
            "Primary business objective",
            height=120,
            placeholder=(
                "Example: Establish a remote-first "
                "technology company serving international "
                "customers."
            ),
        )

        business_model = st.text_area(
            "Business model",
            height=100,
            placeholder=(
                "What will the business sell, to whom, "
                "and how?"
            ),
        )

        industry = st.text_input(
            "Industry",
        )

        customer_market = st.text_input(
            "Target customers / markets",
        )

        owner_residence = st.text_input(
            "Owner residence / tax residence",
        )

        target_jurisdictions = st.text_input(
            "Candidate jurisdictions",
            placeholder=(
                "Example: United States, "
                "United Kingdom, Nigeria"
            ),
        )

        st.markdown(
            "### Operating Requirements"
        )

        capital = st.text_input(
            "Initial capital / budget",
        )

        employees = st.number_input(
            "Initial employees / contractors",
            min_value=0,
            max_value=10000,
            value=0,
        )

        payment_needs = st.multiselect(
            "Payment requirements",
            [
                "International card payments",
                "Bank transfers",
                "Subscription billing",
                "Marketplace payments",
                "Local Nigerian payments",
                "Other",
            ],
        )

        constraints = st.text_area(
            "Constraints / concerns",
            height=100,
            placeholder=(
                "Budget, timing, documentation, "
                "banking, regulatory or operational concerns."
            ),
        )

        submitted = st.form_submit_button(
            "Save Intake",
            type="primary",
        )

    if submitted:

        if not client_name.strip():

            st.error(
                "Client / founder name is required."
            )

        else:

            data = {

                "client_name":
                    client_name.strip(),

                "business_name":
                    business_name.strip(),

                "service_type":
                    service_type,

                "objective":
                    objective.strip(),

                "business_model":
                    business_model.strip(),

                "industry":
                    industry.strip(),

                "customer_market":
                    customer_market.strip(),

                "owner_residence":
                    owner_residence.strip(),

                "target_jurisdictions":
                    target_jurisdictions.strip(),

                "capital":
                    capital.strip(),

                "employees":
                    employees,

                "payment_needs":
                    payment_needs,

                "constraints":
                    constraints.strip(),
            }

            engagement_id = save_engagement(
                data
            )

            st.session_state.intake = data

            st.session_state.current_engagement_id = (
                engagement_id
            )

            st.success(
                f"Intake saved as Engagement "
                f"#{engagement_id}."
            )

            st.info(
                "Next recommended step: "
                "review the Business Profile."
            )


# ============================================================
# BUSINESS PROFILE
# ============================================================

elif page == "Business Profile":

    st.title(
        "Business Profile"
    )

    st.caption(
        "Structured representation of the client's business."
    )

    data = st.session_state.intake

    if not data:

        st.info(
            "Complete Client Intake first."
        )

        st.button(
            "Go to Client Intake →",
            on_click=go_to,
            args=("Client Intake",),
        )

    else:

        profile = build_profile(
            data
        )

        st.markdown(
            "### Profile Summary"
        )

        columns = st.columns(2)

        profile_items = list(
            profile.items()
        )

        for index, (
            key,
            value,
        ) in enumerate(profile_items):

            with columns[index % 2]:

                label = (
                    key
                    .replace("_", " ")
                    .title()
                )

                st.markdown(
                    f"""
                    <div class="po-card">

                        <div class="title">
                            {label}
                        </div>

                        <div class="desc">
                            {value
                             if value not in (None, "", [])
                             else "Not provided"}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.divider()

        st.download_button(
            "Download Business Profile JSON",
            data=json.dumps(
                profile,
                indent=2,
                ensure_ascii=False,
            ),
            file_name="business_profile.json",
            mime="application/json",
        )


# ============================================================
# JURISDICTION LENS
# ============================================================

elif page == "Jurisdiction Lens":

    st.title(
        "Jurisdiction Lens"
    )

    st.caption(
        "Internal comparison model. Scores are not legal "
        "recommendations and must be supported by current "
        "research before client delivery."
    )

    selected = st.multiselect(
        "Select jurisdictions",
        list(
            JURISDICTIONS.keys()
        ),
        default=list(
            JURISDICTIONS.keys()
        )[:2],
    )

    st.markdown(
        "### Decision Priorities"
    )

    p1, p2, p3, p4 = st.columns(4)

    formation = p1.slider(
        "Formation simplicity",
        0.0,
        5.0,
        3.0,
        0.5,
    )

    cost = p2.slider(
        "Cost importance",
        0.0,
        5.0,
        3.0,
        0.5,
    )

    remote = p3.slider(
        "Remote operation",
        0.0,
        5.0,
        3.0,
        0.5,
    )

    international = p4.slider(
        "International business",
        0.0,
        5.0,
        4.0,
        0.5,
    )

    p5, p6, p7 = st.columns(3)

    payments = p5.slider(
        "Banking/payment fit",
        0.0,
        5.0,
        4.0,
        0.5,
    )

    compliance = p6.slider(
        "Lower compliance burden",
        0.0,
        5.0,
        3.0,
        0.5,
    )

    privacy = p7.slider(
        "Privacy importance",
        0.0,
        5.0,
        2.0,
        0.5,
    )

    if st.button(
        "Run Jurisdiction Lens",
        type="primary",
    ):

        priorities = {

            "formation":
                formation,

            "cost":
                cost,

            "remote":
                remote,

            "international":
                international,

            "payments":
                payments,

            "compliance":
                compliance,

            "privacy":
                privacy,
        }

        st.session_state.comparison = (
            compare_jurisdictions(
                selected,
                priorities,
            )
        )

    if st.session_state.comparison:

        st.markdown(
            "### Comparison Results"
        )

        for item in st.session_state.comparison:

            st.markdown(
                f"""
                <div class="po-card">

                    <div class="po-kicker">
                        Jurisdiction
                    </div>

                    <div class="title"
                         style="font-size:1.2rem;">
                        {item['jurisdiction']}
                    </div>

                    <div class="desc">

                        <strong>
                            Entity:
                        </strong>
                        {item['entity']}

                        <br><br>

                        <strong>
                            Internal fit score:
                        </strong>
                        {item['score']}/100

                        <br><br>

                        <strong>
                            Interpretation:
                        </strong>
                        {item['score_label']}

                        <br><br>

                        <strong>
                            Notes:
                        </strong>
                        {item['notes']}

                        <br><br>

                        <strong>
                            Primary sources to verify:
                        </strong>
                        {", ".join(item["sources"])}

                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            st.write("")

        st.warning(
            "Do not present the internal score as a "
            "legal, tax, banking or investment conclusion. "
            "It is an internal prioritisation mechanism."
        )


# ============================================================
# FORMATION ROADMAP
# ============================================================

elif page == "Formation Roadmap":

    st.title(
        "Formation Roadmap"
    )

    st.caption(
        "Convert the proposed structure into an actionable "
        "implementation sequence."
    )

    if not st.session_state.intake:

        st.info(
            "Complete Client Intake first."
        )

        st.button(
            "Go to Client Intake →",
            on_click=go_to,
            args=("Client Intake",),
        )

    else:

        steps = formation_roadmap(
            st.session_state.intake
        )

        st.markdown(
            "### Implementation Sequence"
        )

        for index, step in enumerate(
            steps
        ):

            st.checkbox(
                step,
                key=f"roadmap_{index}",
            )

        st.divider()

        roadmap_text = "\n".join(
            f"- {item}"
            for item in steps
        )

        st.download_button(
            "Download Formation Roadmap",
            data=roadmap_text,
            file_name="formation_roadmap.txt",
            mime="text/plain",
        )


# ============================================================
# COMPLIANCE
# ============================================================

elif page == "Compliance":

    st.title(
        "Compliance Checklist"
    )

    st.caption(
        "Checklist generation is not proof of compliance. "
        "Each requirement must be verified for the actual "
        "entity, jurisdiction and activity."
    )

    if not st.session_state.intake:

        st.info(
            "Complete Client Intake first."
        )

        st.button(
            "Go to Client Intake →",
            on_click=go_to,
            args=("Client Intake",),
        )

    else:

        checklist = compliance_checklist(
            st.session_state.intake
        )

        reviewed_count = 0

        for index, item in enumerate(
            checklist
        ):

            with st.expander(
                item["item"]
            ):

                st.write(
                    f"**Frequency:** "
                    f"{item['frequency']}"
                )

                st.write(
                    f"**Status:** "
                    f"{item['status']}"
                )

                st.write(
                    f"**Evidence:** "
                    f"{item['evidence']}"
                )

                reviewed = st.checkbox(
                    "Mark reviewed",
                    key=f"compliance_{index}",
                )

                if reviewed:
                    reviewed_count += 1

        st.progress(
            reviewed_count / len(checklist)
        )

        st.caption(
            f"{reviewed_count} of "
            f"{len(checklist)} checklist items reviewed."
        )

        st.download_button(
            "Download Compliance Checklist JSON",
            data=json.dumps(
                checklist,
                indent=2,
            ),
            file_name="compliance_checklist.json",
            mime="application/json",
        )


# ============================================================
# REPORT GENERATOR
# ============================================================

elif page == "Report Generator":

    st.title(
        "Report Generator"
    )

    st.caption(
        "Generate a professional decision-support report "
        "from the current engagement data."
    )

    if not st.session_state.intake:

        st.info(
            "Complete Client Intake first."
        )

        st.button(
            "Go to Client Intake →",
            on_click=go_to,
            args=("Client Intake",),
        )

    else:

        if st.button(
            "Generate Report",
            type="primary",
        ):

            st.session_state.report = (
                render_markdown_report(
                    st.session_state.intake,
                    st.session_state.comparison,
                )
            )

        if st.session_state.report:

            st.markdown(
                st.session_state.report
            )

            business_name = (
                st.session_state.intake.get(
                    "business_name"
                )
                or
                st.session_state.intake.get(
                    "client_name"
                )
                or
                "engagement"
            )

            filename = (
                safe_filename(
                    business_name
                )
                + "_pieroloos_report.md"
            )

            report_path = (
                EXPORT_DIR / filename
            )

            report_path.write_text(
                st.session_state.report,
                encoding="utf-8",
            )

            engagement_id = (
                st.session_state.current_engagement_id
            )

            save_report_record(
                engagement_id,
                filename,
                "Client Business Formation & Operating Report",
            )

            st.download_button(
                "Download Report",
                data=st.session_state.report,
                file_name=filename,
                mime="text/markdown",
            )

            st.success(
                "Report generated and recorded."
            )


# ============================================================
# ENGAGEMENT RECORDS
# ============================================================

elif page == "Engagement Records":

    st.title(
        "Engagement Records"
    )

    st.caption(
        "Central record of client engagements created "
        "through the PieroloOS MVP."
    )

    rows = load_engagements()

    if not rows:

        st.info(
            "No engagement records yet."
        )

        st.button(
            "Create First Engagement →",
            on_click=go_to,
            args=("Client Intake",),
        )

    else:

        st.markdown(
            f"### {len(rows)} Engagement"
            f"{'s' if len(rows) != 1 else ''}"
        )

        for row in rows:

            business_display = (
                row["business_name"]
                or "Unnamed business"
            )

            with st.expander(
                f"#{row['id']} — "
                f"{row['client_name']} — "
                f"{business_display}"
            ):

                c1, c2 = st.columns(2)

                with c1:

                    st.write(
                        f"**Created:** "
                        f"{row['created_at']}"
                    )

                    st.write(
                        f"**Updated:** "
                        f"{row['updated_at']}"
                    )

                    st.write(
                        f"**Service:** "
                        f"{row['service_type']}"
                    )

                with c2:

                    st.write(
                        f"**Current status:** "
                        f"{row['status']}"
                    )

                    new_status = st.selectbox(
                        "Change engagement status",
                        [
                            "Intake",
                            "Research",
                            "Planning",
                            "Awaiting Approval",
                            "Execution",
                            "Review",
                            "Closed",
                        ],
                        index=[
                            "Intake",
                            "Research",
                            "Planning",
                            "Awaiting Approval",
                            "Execution",
                            "Review",
                            "Closed",
                        ].index(
                            row["status"]
                        )
                        if row["status"]
                        in [
                            "Intake",
                            "Research",
                            "Planning",
                            "Awaiting Approval",
                            "Execution",
                            "Review",
                            "Closed",
                        ]
                        else 0,
                        key=f"status_{row['id']}",
                    )

                    if st.button(
                        "Update Status",
                        key=f"update_{row['id']}",
                    ):

                        update_engagement_status(
                            row["id"],
                            new_status,
                        )

                        st.success(
                            "Engagement status updated."
                        )

                        st.rerun()

                st.write(
                    f"**Objective:** "
                    f"{row['objective']}"
                )

                try:

                    record = json.loads(
                        row["data_json"]
                    )

                    with st.expander(
                        "View structured record"
                    ):

                        st.json(
                            record
                        )

                except (
                    TypeError,
                    json.JSONDecodeError,
                ):

                    st.write(
                        "Record data could not be parsed."
                    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="po-footer">

        <strong>
            PieroloCorp International LLC
        </strong>

        <br>

        Professional Services for a More
        Connected Global Economy.

        <span class="po-footer-right">

            PieroloOS v0.1
            &nbsp; • &nbsp;
            Build
            &nbsp; • &nbsp;
            Structure
            &nbsp; • &nbsp;
            Scale
            &nbsp; • &nbsp;
            Globally

        </span>

    </div>
    """,
    unsafe_allow_html=True,
    )
