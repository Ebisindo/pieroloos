"""
PIEROLOOS v0.1 — Core MVP
PieroloCorp International LLC

Lean local MVP for:
1. Client Intake
2. Business Profile
3. Jurisdiction Lens
4. Formation Roadmap
5. Compliance Checklist
6. Report Generator
7. Basic Project/Engagement State

Run:
    pip install streamlit
    streamlit run app.py

Notes:
- This MVP intentionally does NOT pretend to provide current legal/tax advice.
- Jurisdiction data is an editable research dataset and must be verified against
  current primary sources before client delivery.
- Generated reports are decision-support drafts, not professional advice.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st


# ---------------------------------------------------------------------------
# APP CONFIGURATION
# ---------------------------------------------------------------------------

APP_NAME = "PieroloOS"
APP_VERSION = "v0.1"
DB_PATH = Path("pieroloos.db")
EXPORT_DIR = Path("reports")
EXPORT_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title=f"{APP_NAME} {APP_VERSION}",
    page_icon="P",
    layout="wide",
)


# ---------------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------------

def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = db()
    cur = conn.cursor()

    cur.execute("""
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
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            engagement_id INTEGER,
            decision_question TEXT,
            decision TEXT,
            rationale TEXT,
            data_json TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------------------------------------------------------------------
# RESEARCH DATASET
# ---------------------------------------------------------------------------
# This is deliberately structured as a research dataset rather than a source
# of legal truth. Replace/expand entries after authoritative verification.

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
        "notes": "Use as an initial research profile only. Verify current federal/state obligations.",
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
        "notes": "Common commercial jurisdiction; current obligations and fees require verification.",
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
        "notes": "Initial comparison profile only; verify Companies House and HMRC requirements.",
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
        "notes": "Initial comparison profile only; verify CAC, FIRS and other applicable requirements.",
        "official_sources": [
            "Corporate Affairs Commission",
            "Federal Inland Revenue Service",
        ],
    },
}


# ---------------------------------------------------------------------------
# GENERIC HELPERS
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def score_label(score: float) -> str:
    if score >= 4.5:
        return "Very strong"
    if score >= 3.5:
        return "Strong"
    if score >= 2.5:
        return "Moderate"
    if score >= 1.5:
        return "Lower"
    return "Very low"


def safe_filename(value: str) -> str:
    cleaned = "".join(
        c if c.isalnum() or c in ("-", "_") else "_"
        for c in value.strip()
    )
    return cleaned[:80] or "engagement"


def save_engagement(data: Dict[str, Any]) -> int:
    conn = db()
    timestamp = now_iso()

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO engagements
        (created_at, updated_at, client_name, business_name, objective,
         service_type, status, data_json)
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
            json.dumps(data, ensure_ascii=False),
        ),
    )

    engagement_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(engagement_id)


def load_engagements() -> List[sqlite3.Row]:
    conn = db()
    rows = conn.execute(
        "SELECT * FROM engagements ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return rows


def build_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "client": data.get("client_name"),
        "business": data.get("business_name"),
        "business_model": data.get("business_model"),
        "industry": data.get("industry"),
        "customer_market": data.get("customer_market"),
        "owner_residence": data.get("owner_residence"),
        "target_jurisdictions": data.get("target_jurisdictions"),
        "capital": data.get("capital"),
        "employees": data.get("employees"),
        "payment_needs": data.get("payment_needs"),
        "service": data.get("service_type"),
        "objective": data.get("objective"),
        "constraints": data.get("constraints"),
    }


def compare_jurisdictions(
    selected: List[str],
    priorities: Dict[str, float],
) -> List[Dict[str, Any]]:
    results = []

    for name in selected:
        item = JURISDICTIONS[name]

        weighted = (
            item["formation_complexity"] * priorities["formation"] +
            (6 - item["cost_index"]) * priorities["cost"] +
            item["remote_friendliness"] * priorities["remote"] +
            item["international_business_fit"] * priorities["international"] +
            item["banking_payment_fit"] * priorities["payments"] +
            (6 - item["compliance_complexity"]) * priorities["compliance"] +
            item["privacy_index"] * priorities["privacy"]
        )

        denominator = sum(priorities.values()) * 5
        normalized = round((weighted / denominator) * 100, 1) if denominator else 0

        results.append({
            "jurisdiction": name,
            "entity": item["entity"],
            "score": normalized,
            "score_label": score_label(normalized / 20),
            "notes": item["notes"],
            "sources": item["official_sources"],
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)


def formation_roadmap(data: Dict[str, Any]) -> List[str]:
    return [
        "1. Confirm business objective, customer, activities and target markets.",
        "2. Confirm proposed entity architecture and jurisdictions for professional review.",
        "3. Confirm name availability and formation requirements.",
        "4. Prepare formation information and required identification/documentation.",
        "5. File formation documents through the appropriate authority/provider.",
        "6. Establish the company's core records and governance documentation.",
        "7. Establish appropriate business banking/payment infrastructure.",
        "8. Set up accounting, invoicing and transaction-record controls.",
        "9. Establish applicable tax/compliance calendar.",
        "10. Establish contracts, IP ownership and confidentiality controls.",
        "11. Complete operational onboarding and launch checklist.",
        "12. Schedule a post-formation review after the first operating period.",
    ]


def compliance_checklist(data: Dict[str, Any]) -> List[Dict[str, str]]:
    return [
        {
            "item": "Entity status",
            "frequency": "As required",
            "status": "Research required",
            "evidence": "Formation/registration record",
        },
        {
            "item": "Registered-agent / registered-office requirement",
            "frequency": "Ongoing",
            "status": "Research required",
            "evidence": "Service agreement / official record",
        },
        {
            "item": "Tax registration and filing obligations",
            "frequency": "Jurisdiction-dependent",
            "status": "Professional verification",
            "evidence": "Tax registrations and filings",
        },
        {
            "item": "Annual / periodic company filing",
            "frequency": "Jurisdiction-dependent",
            "status": "Research required",
            "evidence": "Filed return / confirmation",
        },
        {
            "item": "Business licence / regulated activity review",
            "frequency": "As applicable",
            "status": "Review activity",
            "evidence": "Licence or written determination",
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
            "item": "Data protection / privacy obligations",
            "frequency": "Ongoing",
            "status": "Research required",
            "evidence": "Privacy documentation / controls",
        },
    ]


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
        f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        f"**PieroloOS version:** {APP_VERSION}",
        "",
        "## 1. Executive Summary",
        "",
        f"**Client:** {profile.get('client') or 'Not provided'}",
        f"**Business:** {profile.get('business') or 'Not provided'}",
        f"**Objective:** {profile.get('objective') or 'Not provided'}",
        "",
        "This report is an initial decision-support document generated from "
        "client-provided information and the current PieroloOS research dataset. "
        "Jurisdiction-specific legal, tax, regulatory and payment conclusions "
        "must be verified against current authoritative sources and, where "
        "appropriate, qualified professionals.",
        "",
        "## 2. Business Profile",
        "",
    ]

    for key, value in profile.items():
        if value not in (None, "", []):
            label = key.replace("_", " ").title()
            lines.append(f"- **{label}:** {value}")

    lines.extend(["", "## 3. Jurisdiction Lens", ""])

    if comparison:
        for i, result in enumerate(comparison, start=1):
            lines.extend([
                f"### {i}. {result['jurisdiction']}",
                f"- Entity: {result['entity']}",
                f"- Internal fit score: {result['score']}/100",
                f"- Interpretation: {result['score_label']}",
                f"- Notes: {result['notes']}",
                f"- Primary sources to verify: {', '.join(result['sources'])}",
                "",
            ])
    else:
        lines.append("No jurisdictions selected.")

    lines.extend(["## 4. Formation Roadmap", ""])
    lines.extend(f"- {item}" for item in roadmap)

    lines.extend(["", "## 5. Compliance Checklist", ""])
    for item in checklist:
        lines.append(
            f"- **{item['item']}** — {item['frequency']} — "
            f"{item['status']} — Evidence: {item['evidence']}"
        )

    lines.extend([
        "",
        "## 6. Key Risks and Verification Points",
        "",
        "- Confirm the legal/tax implications of the proposed structure.",
        "- Verify current government fees, filing deadlines and registration rules.",
        "- Verify payment processor eligibility and prohibited/restricted activities.",
        "- Confirm whether the intended services trigger licensing or regulated activity rules.",
        "- Establish written IP/confidentiality arrangements before contractor development.",
        "- Keep company and personal finances appropriately separated.",
        "",
        "## 7. Next Actions",
        "",
        "1. Verify the jurisdiction data against current primary sources.",
        "2. Confirm the proposed entity and operating structure with the appropriate professional.",
        "3. Confirm payment/banking requirements.",
        "4. Establish the company's records, accounting and compliance calendar.",
        "5. Approve the final formation roadmap.",
        "",
        "---",
        "",
        "**PieroloOS:** Operating intelligence and decision-support layer for PieroloCorp International LLC.",
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------

if "intake" not in st.session_state:
    st.session_state.intake = {}

if "comparison" not in st.session_state:
    st.session_state.comparison = []

if "report" not in st.session_state:
    st.session_state.report = ""


# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("PieroloOS")
    st.caption(f"Professional Service Operating System • {APP_VERSION}")

    page = st.radio(
        "Operating module",
        [
            "Command Center",
            "Client Intake",
            "Business Profile",
            "Jurisdiction Lens",
            "Formation Roadmap",
            "Compliance",
            "Report Generator",
            "Engagement Records",
        ],
    )

    st.divider()
    st.caption("MVP control status")
    st.write("Evidence-aware: ✓")
    st.write("Human approval: ✓")
    st.write("SQLite records: ✓")
    st.write("Authoritative-source verification: Required")


# ---------------------------------------------------------------------------
# COMMAND CENTER
# ---------------------------------------------------------------------------

if page == "Command Center":
    st.title("PieroloOS Command Center")
    st.subheader("Operating intelligence layer")

    rows = load_engagements()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Engagements", len(rows))
    c2.metric("Active", sum(1 for r in rows if r["status"] != "Closed"))
    c3.metric("Reports generated", "Session")
    c4.metric("Version", APP_VERSION)

    st.divider()

    st.markdown("### Current operating loop")
    st.info(
        "Intake → Classify → Verify → Assess → Plan → Approve → Execute → "
        "Verify → Record → Close → Learn"
    )

    st.markdown("### Current MVP modules")
    modules = [
        ("Client Intake", "Capture structured customer requirements."),
        ("Business Profile", "Convert intake into a structured business record."),
        ("Jurisdiction Lens", "Compare candidate jurisdictions using editable criteria."),
        ("Formation Roadmap", "Turn the selected structure into implementation steps."),
        ("Compliance", "Create an initial obligation checklist."),
        ("Report Generator", "Produce a reusable client-facing report."),
    ]

    for name, description in modules:
        st.write(f"**{name}** — {description}")

    st.warning(
        "This MVP is a workflow and decision-support prototype. "
        "It does not replace legal, tax, accounting or other professional review."
    )


# ---------------------------------------------------------------------------
# CLIENT INTAKE
# ---------------------------------------------------------------------------

elif page == "Client Intake":
    st.title("Client Intake")
    st.caption("Structured intake → reusable business data")

    with st.form("client_intake_form"):
        client_name = st.text_input("Client / founder name")
        business_name = st.text_input("Proposed business name")

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

        objective = st.text_area(
            "What is the client's primary objective?",
            height=120,
            placeholder="Example: Establish a remote-first technology company that can sell internationally.",
        )

        business_model = st.text_area(
            "Business model",
            height=100,
            placeholder="What will the business sell, to whom, and how?",
        )

        industry = st.text_input("Industry")
        customer_market = st.text_input("Target customers / markets")
        owner_residence = st.text_input("Owner residence / tax residence")
        target_jurisdictions = st.text_input(
            "Candidate jurisdictions",
            placeholder="Example: United States, United Kingdom, Nigeria",
        )

        capital = st.text_input("Initial capital / budget")
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
            placeholder="Budget, timing, documentation, banking, regulatory or operational concerns.",
        )

        submitted = st.form_submit_button("Save Intake", type="primary")

    if submitted:
        data = {
            "client_name": client_name,
            "business_name": business_name,
            "service_type": service_type,
            "objective": objective,
            "business_model": business_model,
            "industry": industry,
            "customer_market": customer_market,
            "owner_residence": owner_residence,
            "target_jurisdictions": target_jurisdictions,
            "capital": capital,
            "employees": employees,
            "payment_needs": payment_needs,
            "constraints": constraints,
        }

        engagement_id = save_engagement(data)
        st.session_state.intake = data
        st.success(f"Intake saved as Engagement #{engagement_id}.")


# ---------------------------------------------------------------------------
# BUSINESS PROFILE
# ---------------------------------------------------------------------------

elif page == "Business Profile":
    st.title("Business Profile")

    data = st.session_state.intake

    if not data:
        st.info("Complete Client Intake first.")
    else:
        profile = build_profile(data)

        for key, value in profile.items():
            label = key.replace("_", " ").title()
            st.markdown(f"**{label}**")
            st.write(value if value not in (None, "", []) else "Not provided")
            st.divider()

        st.download_button(
            "Download Business Profile JSON",
            data=json.dumps(profile, indent=2, ensure_ascii=False),
            file_name="business_profile.json",
            mime="application/json",
        )


# ---------------------------------------------------------------------------
# JURISDICTION LENS
# ---------------------------------------------------------------------------

elif page == "Jurisdiction Lens":
    st.title("Jurisdiction Lens")
    st.caption(
        "Internal comparison model. Scores are not legal recommendations and "
        "must be supported by current research before client delivery."
    )

    selected = st.multiselect(
        "Select jurisdictions",
        list(JURISDICTIONS.keys()),
        default=list(JURISDICTIONS.keys())[:2],
    )

    st.markdown("### Decision priorities")

    p1, p2, p3, p4 = st.columns(4)

    formation = p1.slider("Formation simplicity", 0.0, 5.0, 3.0, 0.5)
    cost = p2.slider("Cost importance", 0.0, 5.0, 3.0, 0.5)
    remote = p3.slider("Remote operation", 0.0, 5.0, 3.0, 0.5)
    international = p4.slider("International business", 0.0, 5.0, 4.0, 0.5)

    p5, p6, p7 = st.columns(3)
    payments = p5.slider("Banking/payment fit", 0.0, 5.0, 4.0, 0.5)
    compliance = p6.slider("Lower compliance burden", 0.0, 5.0, 3.0, 0.5)
    privacy = p7.slider("Privacy importance", 0.0, 5.0, 2.0, 0.5)

    if st.button("Run Jurisdiction Lens", type="primary"):
        priorities = {
            "formation": formation,
            "cost": cost,
            "remote": remote,
            "international": international,
            "payments": payments,
            "compliance": compliance,
            "privacy": privacy,
        }

        st.session_state.comparison = compare_jurisdictions(
            selected,
            priorities,
        )

    if st.session_state.comparison:
        st.markdown("### Comparison")

        for item in st.session_state.comparison:
            st.markdown(f"#### {item['jurisdiction']}")
            st.metric("Internal fit score", f"{item['score']}/100")
            st.write(f"**Entity:** {item['entity']}")
            st.write(f"**Interpretation:** {item['score_label']}")
            st.write(f"**Notes:** {item['notes']}")
            st.write(
                "**Primary sources to verify:** "
                + ", ".join(item["sources"])
            )
            st.divider()

        st.warning(
            "Do not present the score as a legal, tax, banking or investment "
            "conclusion. It is an internal prioritisation mechanism."
        )


# ---------------------------------------------------------------------------
# FORMATION ROADMAP
# ---------------------------------------------------------------------------

elif page == "Formation Roadmap":
    st.title("Formation Roadmap")

    if not st.session_state.intake:
        st.info("Complete Client Intake first.")
    else:
        steps = formation_roadmap(st.session_state.intake)

        for step in steps:
            st.checkbox(step, key=f"roadmap_{steps.index(step)}")

        st.download_button(
            "Download Roadmap",
            data="\n".join(f"- {x}" for x in steps),
            file_name="formation_roadmap.txt",
            mime="text/plain",
        )


# ---------------------------------------------------------------------------
# COMPLIANCE
# ---------------------------------------------------------------------------

elif page == "Compliance":
    st.title("Compliance Checklist")
    st.caption(
        "Checklist generation is not proof of compliance. Each requirement "
        "must be verified for the actual entity, jurisdiction and activity."
    )

    if not st.session_state.intake:
        st.info("Complete Client Intake first.")
    else:
        checklist = compliance_checklist(st.session_state.intake)

        for i, item in enumerate(checklist):
            with st.expander(item["item"]):
                st.write(f"**Frequency:** {item['frequency']}")
                st.write(f"**Status:** {item['status']}")
                st.write(f"**Evidence:** {item['evidence']}")
                st.checkbox("Mark reviewed", key=f"compliance_{i}")

        checklist_json = json.dumps(checklist, indent=2)
        st.download_button(
            "Download Compliance Checklist JSON",
            data=checklist_json,
            file_name="compliance_checklist.json",
            mime="application/json",
        )


# ---------------------------------------------------------------------------
# REPORT GENERATOR
# ---------------------------------------------------------------------------

elif page == "Report Generator":
    st.title("Report Generator")

    if not st.session_state.intake:
        st.info("Complete Client Intake first.")
    else:
        if st.button("Generate Report", type="primary"):
            st.session_state.report = render_markdown_report(
                st.session_state.intake,
                st.session_state.comparison,
            )

        if st.session_state.report:
            st.markdown(st.session_state.report)

            filename = (
                safe_filename(
                    st.session_state.intake.get("business_name")
                    or st.session_state.intake.get("client_name")
                    or "engagement"
                )
                + "_pieroloos_report.md"
            )

            report_path = EXPORT_DIR / filename
            report_path.write_text(
                st.session_state.report,
                encoding="utf-8",
            )

            st.download_button(
                "Download Report",
                data=st.session_state.report,
                file_name=filename,
                mime="text/markdown",
            )


# ---------------------------------------------------------------------------
# ENGAGEMENT RECORDS
# ---------------------------------------------------------------------------

elif page == "Engagement Records":
    st.title("Engagement Records")

    rows = load_engagements()

    if not rows:
        st.info("No engagement records yet.")
    else:
        for row in rows:
            with st.expander(
                f"#{row['id']} — {row['client_name']} — "
                f"{row['business_name'] or 'Unnamed business'}"
            ):
                st.write(f"**Created:** {row['created_at']}")
                st.write(f"**Updated:** {row['updated_at']}")
                st.write(f"**Service:** {row['service_type']}")
                st.write(f"**Status:** {row['status']}")
                st.write(f"**Objective:** {row['objective']}")

                try:
                    record = json.loads(row["data_json"])
                    st.json(record)
                except Exception:
                    st.write("Record data could not be parsed.")

# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------

st.divider()
st.caption(
    f"{APP_NAME} {APP_VERSION} • PieroloCorp International LLC • "
    "Internal MVP / decision-support prototype"
)
