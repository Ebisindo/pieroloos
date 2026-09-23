# PieroloOS v0.1

## Professional Service Operating System for PieroloCorp International LLC

PieroloOS is the internal digital operating environment being developed for **PieroloCorp International LLC**.

The v0.1 MVP converts core business-formation and professional-service workflows into a structured, repeatable software experience. It is designed to help organize client information, evaluate jurisdictions, generate formation roadmaps, track compliance tasks, produce reports, and maintain engagement records.

> **Status:** MVP / Prototype  
> **Version:** v0.1  
> **Organization:** PieroloCorp International LLC  
> **Primary Interface:** Streamlit  
> **Data Layer:** SQLite  
> **Deployment Target:** Streamlit Community Cloud

---

## 1. Product Vision

PieroloOS is intended to evolve from a simple business-formation workflow into a broader **Corporate Intelligence & Formation Platform**.

The long-term concept includes:

- Jurisdiction Intelligence
- Entity Architecture
- Business Formation Workflows
- Compliance Autopilot
- Corporate Lifecycle Management
- Capital Flow Mapping
- Risk Simulation
- Document Generation
- Provider Coordination
- Business Intelligence
- Client Dashboards
- Professional-Provider Networks
- Corporate Knowledge Management

The v0.1 release deliberately focuses on a smaller operational core so that the system can be tested, improved, and expanded incrementally.

---

# 2. v0.1 MVP Scope

The current MVP contains seven principal functional areas.

### 2.1 Client Intake

Captures structured client information including:

- Client name
- Email
- Country
- Business name
- Business activity
- Objectives
- Capital information
- Preferred jurisdiction
- Additional notes

Client information is stored in the SQLite database.

---

### 2.2 Business Profile

Organizes information associated with a client and provides a place for additional business-profile notes.

The objective is to create a structured business context that can later become the foundation for automated analysis and recommendations.

---

### 2.3 Jurisdiction Lens

Provides a structured comparison of jurisdictions using defined evaluation criteria.

The current MVP uses an internal indicator model based on factors such as:

- Formation simplicity
- Compliance burden
- Cost considerations
- Banking considerations
- Tax considerations
- Operational considerations

The Jurisdiction Lens is a decision-support component rather than a substitute for legal, tax, accounting, or other licensed professional advice.

---

### 2.4 Formation Roadmap

Generates an ordered formation workflow based on the client's selected jurisdiction and business context.

Typical stages include:

1. Define the business structure
2. Confirm jurisdiction
3. Prepare formation information
4. File formation documents
5. Obtain required identification or registrations
6. Establish banking/payment infrastructure
7. Address compliance obligations
8. Complete operational setup

The roadmap is designed to become progressively more jurisdiction-specific as the underlying intelligence dataset develops.

---

### 2.5 Compliance Checklist

Provides a structured checklist for recurring or one-time obligations.

The MVP includes:

- Compliance task tracking
- Completion status
- Progress visibility
- Basic obligation organization

This component is intended to become the foundation for the future **Compliance Autopilot** module.

---

### 2.6 Report Generator

Creates a professional Markdown report from the information captured within PieroloOS.

Reports can include:

- Client information
- Business profile
- Jurisdiction analysis
- Formation roadmap
- Compliance considerations
- General observations
- Professional-service disclaimer

Generated reports are stored in the application's reports directory and recorded in the database.

---

### 2.7 Engagement Records

Provides a lightweight engagement register for tracking active client work.

Records can contain:

- Client
- Service
- Status
- Next action
- Notes
- Updated timestamp

The register supports basic creation, viewing, and updating of engagement records.

---

# 3. System Architecture

The current MVP follows a deliberately simple architecture.

```text
                    ┌──────────────────────────┐
                    │       PieroloOS UI       │
                    │        Streamlit         │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       Client Services      Intelligence       Operations
              │                  │                  │
              ▼                  ▼                  ▼
       Client Intake       Jurisdiction Lens   Engagements
       Business Profile   Roadmap              Compliance
       Reports             Research Data        Workflow
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 ▼
                    ┌──────────────────────────┐
                    │       SQLite Database    │
                    └──────────────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      Markdown Reports    │
                    └──────────────────────────┘
```

---

# 4. Technology Stack

## Application

- Python
- Streamlit

## Database

- SQLite
- Python `sqlite3`

## Interface

- Native Streamlit components
- Responsive Streamlit layout
- Custom CSS for branding
- Native Streamlit sidebar/navigation

## Branding

- PieroloCorp / PieroloOS logo
- Cosmic visual background
- Midnight/navy-oriented interface
- Gold and violet accent system

## Output

- Markdown reports
- Downloadable report files

---

# 5. Repository Structure

The recommended repository structure is:

```text
pieroloos/
│
├── app.py
├── requirements.txt
├── README.md
│
├── assets/
│   ├── pieroloos_background.svg
│   └── pierolocorp_logo.png
│
├── reports/
│   └── generated reports
│
└── pieroloos.db
```

The application also supports the alternative logo filename:

```text
assets/pierolooscorp_logo.png
```

The application checks for the available supported logo filename automatically.

---

# 6. Local Installation

## Requirements

Recommended:

- Python 3.10+
- pip
- Git

Clone the repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd pieroloos
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
streamlit run app.py
```

The application will open in the local browser.

---

# 7. Requirements

The current application requires Streamlit.

A minimal `requirements.txt` can contain:

```text
streamlit
```

If additional dependencies are introduced in future versions, they should be added to `requirements.txt` and documented here.

---

# 8. Database

PieroloOS v0.1 uses SQLite for the MVP data layer.

The database contains the principal application records:

```text
clients
reports
engagements
```

The application includes schema-management and migration logic intended to accommodate older database structures.

## Important MVP consideration

SQLite is appropriate for the current prototype and early testing.

For production-scale deployment, the data layer should eventually move to a managed relational database such as PostgreSQL.

Potential future architecture:

```text
Streamlit / Web Application
            │
            ▼
       Application API
            │
            ▼
        PostgreSQL
            │
      ┌─────┼─────┐
      ▼     ▼     ▼
   Clients Reports Engagements
```

---

# 9. Streamlit Community Cloud Deployment

PieroloOS can be deployed through Streamlit Community Cloud.

Typical deployment flow:

1. Push the project to GitHub.
2. Confirm `app.py` is in the repository root.
3. Confirm `requirements.txt` is present.
4. Confirm the `assets/` directory is committed.
5. Connect the GitHub repository to Streamlit Community Cloud.
6. Select `app.py` as the main application file.
7. Deploy.

After deployment, Streamlit provides a public application URL.

---

# 10. Mobile and Tablet UX

The MVP is designed to work within Streamlit's responsive environment.

The interface uses:

- Native Streamlit navigation
- Native hamburger sidebar
- Wide desktop layout
- Responsive columns
- Bordered containers
- Compact metrics
- Mobile-friendly form controls
- Minimal custom HTML
- CSS branding without replacing Streamlit's application structure

This approach reduces the risk of fragile custom front-end components while keeping the interface visually aligned with the PieroloCorp identity.

---

# 11. Design System

PieroloOS uses a professional technology/corporate aesthetic built around a cosmic visual identity.

### Visual language

- Deep navy / space-inspired background
- Metallic-gold primary accents
- Violet secondary accents
- High-contrast typography
- Structured cards and panels
- Minimal visual clutter
- Executive dashboard presentation

The visual language is intended to communicate:

```text
Intelligence
    +
Structure
    +
Precision
    +
Professionalism
    +
Technology
```

---

# 12. Data Flow

A typical client workflow is:

```text
Client Intake
     │
     ▼
Business Profile
     │
     ▼
Jurisdiction Lens
     │
     ▼
Formation Roadmap
     │
     ▼
Compliance Checklist
     │
     ▼
Report Generator
     │
     ▼
Engagement Record
     │
     ▼
Ongoing Service Management
```

This creates the initial operational loop for PieroloOS.

---

# 13. Professional-Service Boundary

PieroloOS is a decision-support and workflow-organization system.

It is **not** intended to replace:

- Lawyers
- Tax professionals
- Accountants
- Corporate-service professionals
- Licensed financial professionals
- Government authorities
- Other regulated professional advisers

Outputs should be reviewed by the appropriate professional or authority whenever the matter requires professional or jurisdiction-specific advice.

---

# 14. Security Considerations

The v0.1 MVP is an early prototype and should not yet be treated as a fully hardened production system.

Future security work should include:

- Authentication
- Authorization
- Role-based access control
- Secure session management
- Encryption
- Secrets management
- Audit logging
- Database backups
- Input validation
- File-access controls
- Data-retention policies
- Privacy controls
- Client-data isolation
- Security monitoring

Sensitive credentials and API keys must never be committed to GitHub.

---

# 15. Current MVP Limitations

The current version intentionally has limitations.

### Data persistence

SQLite and local files are suitable for prototyping but are not the preferred architecture for a multi-user production SaaS.

### Authentication

The MVP does not yet implement a complete user/account system.

### Multi-tenancy

Client/company data is not yet isolated through a production-grade tenant architecture.

### Jurisdiction intelligence

The current jurisdiction model is an MVP framework and should not be interpreted as comprehensive legal or tax research.

### Compliance intelligence

The compliance checklist is a workflow foundation, not a complete regulatory monitoring service.

### Payments

Payment processing is outside the core v0.1 application and should be integrated through a secure production payment architecture.

### Auditability

A comprehensive immutable audit trail is a future requirement.

---

# 16. Product Roadmap

## Phase 1 — MVP Foundation

Current focus:

- Client Intake
- Business Profile
- Jurisdiction Lens
- Formation Roadmap
- Compliance Checklist
- Report Generator
- Engagement Records
- SQLite persistence
- Basic migration handling
- Branded interface

---

## Phase 2 — Operational Intelligence

Potential additions:

- Better jurisdiction datasets
- Source tracking
- Evidence levels
- Research notes
- Document templates
- Client dashboard
- Task management
- Engagement timelines
- Advanced reporting
- Search
- Filtering
- Activity history

---

## Phase 3 — Compliance Autopilot

Potential capabilities:

- Obligation registers
- Filing calendars
- Deadline monitoring
- Recurring reminders
- Compliance status
- Jurisdiction-specific obligations
- Automated notifications
- Evidence/document storage

---

## Phase 4 — Corporate Intelligence

Potential capabilities:

- Entity architecture
- Jurisdiction comparison engine
- Entity relationship mapping
- Corporate lifecycle tracking
- Capital-flow mapping
- Risk simulation
- Provider intelligence
- Corporate knowledge graph

---

## Phase 5 — SaaS Platform

Potential capabilities:

- User accounts
- Organizations/workspaces
- Multi-tenancy
- Subscription billing
- Client portals
- Role-based permissions
- API integrations
- Managed PostgreSQL
- Background jobs
- Notifications
- Document storage
- Production-grade security

---

# 17. Long-Term PieroloOS Architecture

The broader operating concept is built around interconnected layers:

```text
1. Company State
2. Control Plane
3. Service Engine
4. Knowledge System
5. Workflow Engine
6. Tool Orchestration
7. Performance System
8. Continuous Improvement
```

These layers are intended to transform PieroloOS from a collection of forms into an integrated professional-service operating system.

---

# 18. Development Principles

PieroloOS development should follow these principles:

### Source of Truth

Important business information should have a defined authoritative location.

### Evidence First

Research-driven outputs should distinguish between:

- User-provided information
- Secondary evidence
- Primary evidence
- Cross-verified information

### Structured Workflows

Business processes should be represented as repeatable workflows rather than informal conversations.

### Human Approval

Automation should prepare and organize work while preserving appropriate human decision authority.

### Proportionality

Controls should match the importance and risk of the activity.

### Auditability

Important actions should eventually be traceable.

### Incremental Development

New functionality should be added without unnecessarily destabilizing working functionality.

---

# 19. Development Workflow

Recommended workflow:

```text
Idea
  │
  ▼
Define Requirement
  │
  ▼
Design Workflow
  │
  ▼
Implement Small Change
  │
  ▼
Test
  │
  ▼
Deploy
  │
  ▼
Observe
  │
  ▼
Improve
```

Avoid introducing major architectural complexity before the workflow has been validated in real use.

---

# 20. Testing Checklist

Before considering a release stable, verify:

### Application

- [ ] App starts successfully
- [ ] Sidebar loads
- [ ] Logo displays
- [ ] Background displays
- [ ] Dashboard loads
- [ ] Navigation works

### Client Management

- [ ] Client can be created
- [ ] Client information is stored
- [ ] Business Profile loads
- [ ] Business Profile updates correctly

### Jurisdiction

- [ ] Jurisdiction data loads
- [ ] Comparison works
- [ ] Indicator calculation works

### Formation

- [ ] Roadmap generates
- [ ] Steps display correctly

### Compliance

- [ ] Checklist loads
- [ ] Progress calculates correctly

### Reports

- [ ] Report generates
- [ ] Report is saved
- [ ] Report appears in Previous Reports
- [ ] Report download works

### Engagements

- [ ] Engagement record can be created
- [ ] Engagement register loads
- [ ] Engagement can be updated
- [ ] Updated record is displayed correctly

### Deployment

- [ ] GitHub repository is up to date
- [ ] Streamlit deployment succeeds
- [ ] Assets are available
- [ ] No secrets are committed

---

# 21. Contribution / Change Management

For each meaningful change:

1. Identify the affected module.
2. Preserve existing functionality.
3. Make the smallest practical change.
4. Test the affected workflow.
5. Test adjacent workflows.
6. Commit the change.
7. Deploy.
8. Verify the live application.

Recommended commit style:

```text
feat: add client engagement tracking
fix: repair engagement database migration
fix: correct sidebar status indentation
feat: add jurisdiction comparison
style: improve PieroloOS dashboard
docs: update README
```

---

# 22. License

The licensing model for PieroloOS has not yet been specified.

Until a formal license is added, the source code should be treated as proprietary project material belonging to the project owner/company.

---

# 23. Disclaimer

PieroloOS v0.1 is a software prototype for organizing information, workflows, research, and professional-service processes.

Information generated by the system should be independently reviewed where appropriate.

Nothing in PieroloOS should be interpreted as legal, tax, accounting, financial, regulatory, or other professional advice.

---

# 24. Project Direction

PieroloOS v0.1 is intentionally small.

The objective is not to build every feature immediately.

The objective is to establish the operational foundation upon which the larger PieroloOS system can be built:

```text
Organize
   ↓
Standardize
   ↓
Document
   ↓
Analyze
   ↓
Automate
   ↓
Monitor
   ↓
Improve
```

The long-term goal is to turn professional-service knowledge and workflows into a structured, scalable operating system for PieroloCorp International LLC.

---

**PieroloOS v0.1**  
**PieroloCorp International LLC**

---
