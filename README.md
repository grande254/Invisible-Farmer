# Invisible Farmer Credit Review Agent

**We help lenders review thin-file farmers.**

Invisible Farmer Credit Review Agent is an AgriFin decision-support system for rural SACCOs, MFIs, cooperatives, and agri-finance lenders. It helps loan officers prepare faster, clearer, and more auditable credit-readiness review packs for smallholder farmers who may lack formal credit history, land collateral, payslips, or traditional bank records.

The system combines:

* ML credit-readiness scoring
* Neo4j relationship intelligence
* Featherless AI business explanations
* Masumi-compatible workflow and audit records
* Farmer-safe SMS/USSD communication
* Lovable-built loan officer dashboard
* Human loan-officer outcome recording

The agent does **not** approve loans, reject farmers, or disburse funds. It prepares decision support for a human loan officer or credit committee.

---

## Table of Contents

* [Project Summary](#project-summary)
* [Problem](#problem)
* [Solution](#solution)
* [Who Uses It](#who-uses-it)
* [Core Workflow](#core-workflow)
* [System Architecture](#system-architecture)
* [What the Agent Does](#what-the-agent-does)
* [What the Agent Cannot Do](#what-the-agent-cannot-do)
* [Technology Stack](#technology-stack)
* [Main Modules](#main-modules)
* [Masumi Integration](#masumi-integration)
* [Featherless Integration](#featherless-integration)
* [Neo4j Integration](#neo4j-integration)
* [ML Scoring](#ml-scoring)
* [Lovable Frontend](#lovable-frontend)
* [USSD Simulation](#ussd-simulation)
* [API Endpoints](#api-endpoints)
* [Local Setup](#local-setup)
* [Environment Variables](#environment-variables)
* [Running the Backend](#running-the-backend)
* [Running with Ngrok](#running-with-ngrok)
* [Example API Requests](#example-api-requests)
* [Demo Flow](#demo-flow)
* [Responsible AI Boundary](#responsible-ai-boundary)
* [Measurable Value](#measurable-value)
* [Repository Safety](#repository-safety)
* [Current Status](#current-status)
* [Future Work](#future-work)

---

## Project Summary

Invisible Farmer Credit Review Agent helps rural lenders review smallholder farmers who are often excluded by traditional credit assessment methods.

Many farmers do not have formal credit histories, payslips, bank statements, or land titles. However, they often have repayment evidence in alternative places such as savings groups, cooperatives, buyer relationships, input supplier records, mobile money consistency, extension officer support, and community networks.

This agent turns those scattered signals into a structured credit-readiness review pack for a human loan officer.

---

## Problem

Smallholder farmers are often financially invisible.

Traditional credit reviews usually depend on:

* Formal credit history
* Payslips
* Bank statements
* Land title
* Collateral
* Formal business records

Many rural farmers do not have these documents, even when they are active, reliable, and connected to trusted agricultural networks.

At the same time, loan officers must manually verify farmer information through:

* Phone calls
* WhatsApp messages
* Paper forms
* Spreadsheets
* Cooperative leaders
* Buyer records
* Savings group records
* Input supplier receipts
* Field officer notes

This process is slow, inconsistent, hard to audit, and difficult to scale.

---

## Solution

Invisible Farmer Credit Review Agent converts scattered farmer evidence into a structured review workflow.

A loan officer selects a farmer and starts a credit-readiness review. The backend creates a Masumi-compatible job, runs a scoring process, checks relationship evidence using Neo4j, generates business explanations using Featherless AI, prepares farmer-safe communication, and records the final human outcome.

The output is a review pack containing:

* Credit-readiness score
* Credit-readiness tier
* Recommended support range
* Positive evidence
* Risk signals
* Relationship evidence
* Verification checklist
* Officer memo
* Credit committee brief
* Farmer-safe SMS/USSD message
* Audit explanation
* Masumi-compatible job status
* Payment metadata
* Human loan-officer outcome

---

## Who Uses It

### Primary Users

* Rural loan officers
* SACCO officers
* MFI field officers
* Cooperative finance teams
* Branch managers
* Credit analysts

### Organisations That Benefit

* SACCOs
* MFIs
* Agricultural cooperatives
* Rural banks
* Agri-input financiers
* Digital lenders serving farmers
* Donor-backed financial inclusion programs
* NGOs supporting smallholder finance

### Buyers or Adoption Decision-Makers

* Head of Credit
* Chief Operations Officer
* Digital Transformation Lead
* CEO or General Manager of a SACCO/MFI
* Cooperative leadership
* Donor or NGO program manager
* Financial inclusion program lead

---

## Core Workflow

```text
Loan officer selects farmer
        ↓
Performs credit-readiness review
        ↓
Masumi-compatible workflow job is created
        ↓
ML scoring engine produces credit-readiness score
        ↓
Neo4j reveals relationship evidence and verification paths
        ↓
Featherless generates business explanations
        ↓
Review pack appears in Lovable dashboard
        ↓
Farmer-safe SMS/USSD message is prepared
        ↓
Loan officer records final human outcome
        ↓
Audit trail is stored
```

---

## System Architecture

```text
Users & Channels
    |
    |-- Loan Officer Web Dashboard
    |-- Farmer USSD/SMS Interface
    |
    v
Lovable Frontend
    |
    v
FastAPI Backend
    |
    |-- Review Orchestrator
    |-- Farmer Repository
    |-- Human Review Service
    |-- Export Service
    |-- Audit Builder
    |
    |-- ML Scoring Engine
    |-- Neo4j Graph Intelligence
    |-- Featherless Explanation Agent
    |-- Masumi-Compatible Job Agent
    |-- Farmer USSD Agent
    |-- Officer USSD Agent
    |
    v
Outputs
    |
    |-- Credit-readiness review pack
    |-- Score and tier
    |-- Recommended support range
    |-- Officer memo
    |-- Committee brief
    |-- Farmer-safe SMS/USSD
    |-- Verification checklist
    |-- Human outcome
    |-- Audit trail
```

---

## What the Agent Does

The agent performs real workflow tasks. It does not simply chat.

It can:

* Analyse farmer profile data
* Classify credit-readiness tier
* Generate a credit-readiness score
* Identify positive repayment evidence
* Identify risk signals
* Analyse relationship evidence through Neo4j
* Surface verification paths
* Generate officer memos
* Generate credit committee briefs
* Generate farmer-safe SMS and USSD summaries
* Generate verification checklists
* Record workflow job status
* Record mocked payment metadata
* Record audit events
* Record final human outcome
* Prepare review data for export

---

## What the Agent Cannot Do

The agent cannot:

* Approve loans
* Reject farmers automatically
* Disburse money
* Replace a licensed loan officer
* Replace a credit committee
* Guarantee repayment
* Make legally binding lending decisions
* Treat protected characteristics as negative scoring factors

Human review is required before any final lending decision.

---

## Technology Stack

### Backend

* Python
* FastAPI
* Pydantic
* Uvicorn

### Frontend

* Lovable-built web dashboard
* React-style interface
* Dashboard analytics
* Review workflow
* Activity records
* Workflow audit views
* USSD simulators
* Human outcome capture

### Intelligence and Integrations

* ML scoring engine
* Neo4j graph database
* Featherless AI API
* Masumi-compatible workflow endpoints
* Local mocked 50 ADA payment metadata
* USSD/SMS-style communication simulation

---

## Main Modules

### Backend API

The backend exposes APIs for:

* Farmer review creation
* Masumi-compatible service requests
* Job status checking
* Graph intelligence
* Featherless explanations
* USSD simulation
* Officer USSD simulation
* Human outcome recording
* Export and audit records

### Review Orchestrator

The review orchestrator coordinates the full credit-readiness workflow.

It handles:

1. Farmer lookup
2. Scoring
3. Graph intelligence
4. Explanation generation
5. Farmer message generation
6. Audit building
7. Review pack assembly

### Human Review Service

The human review service records the final loan-officer or credit-committee outcome.

Allowed human outcomes include:

* Proceed to loan processing
* Request more information
* Adjust recommended amount
* Defer for record building
* Manual decline

“Proceed to loan processing” is not an approval. It means the officer may continue the normal lender process.

---

## Masumi Integration

Masumi appears in this project as the workflow, service-request, payment-status, job-status, and audit layer.

The backend exposes Masumi-style endpoints:

```text
GET  /availability
GET  /input_schema
POST /start_job
GET  /status?job_id={job_id}
```

When a loan officer performs a credit-readiness review, the backend creates a Masumi-compatible job with:

* Job ID
* Farmer ID
* Requesting officer
* Purpose
* Job status
* Timestamp
* Payment metadata
* Review result
* Audit events
* Human outcome record

For this prototype, payment confirmation is mocked locally as a 50 ADA workflow payment. This is clearly labelled as local demo payment metadata, not a live on-chain payment.

### Masumi Evidence Level

Current evidence level: **intermediate prototype integration**.

Implemented:

* Agent registration/configuration
* Masumi-compatible service-request flow
* Masumi-style API endpoints
* Job status tracking
* Mocked 50 ADA payment metadata
* Audit event recording
* Human outcome linked to job record
* Review result storage

Future work:

* Live/testnet Masumi payment verification
* Wallet transaction verification
* Explorer link or transaction ID
* Agent-to-agent payment/service flow

---

## Featherless Integration

Featherless powers the business explanation layer.

The backend uses the Featherless API with an open-weight model such as:

```text
unsloth/Qwen2.5-14B-Instruct
```

Featherless is not used to approve or reject loans. It converts structured review data into human-readable business outputs.

### Input Sent to Featherless

The backend sends structured input including:

* Farmer profile
* ML credit-readiness score
* Recommended support range
* Positive signals
* Risk signals
* Neo4j relationship evidence
* Verification paths
* Responsible lending constraints
* Human-review boundary

### Output Returned by Featherless

Featherless returns:

* Officer decision memo
* Credit committee brief
* Branch action plan
* Farmer-safe SMS message
* Farmer USSD summary
* Data collection checklist
* Risk mitigation notes
* Inclusion note
* Audit explanation
* Model limitations

### Where Output Appears

The Lovable dashboard displays Featherless outputs inside the Review Pack.

Loan officers can:

* Read the officer memo
* View the committee brief
* Copy farmer-safe SMS/USSD messages
* Review the verification checklist
* Read risk mitigation notes
* Export or copy the audit pack

---

## Neo4j Integration

Neo4j is the relationship intelligence layer.

It helps reveal hidden repayment evidence by mapping relationships between farmers and:

* Cooperatives
* Savings groups
* Buyers
* Input suppliers
* Extension officers
* Crops
* Counties
* Similar farmer profiles
* Risk context

Neo4j helps transform a thin credit file into a richer evidence map.

### Example Relationship Types

```text
Farmer → MEMBER_OF → Cooperative
Farmer → SAVES_WITH → Savings Group
Farmer → SELLS_TO → Buyer
Farmer → BUYS_FROM → Input Supplier
Farmer → ADVISED_BY → Extension Officer
Farmer → GROWS → Crop
Farmer → LOCATED_IN → County
Farmer → SIMILAR_TO → Similar Farmer
```

### Neo4j Output

Neo4j can return:

* Relationship evidence
* Verification paths
* Trusted relationship signals
* Network risk signals
* Similar farmer context
* Graph support level
* Relationship map data

---

## ML Scoring

The ML scoring engine produces the main credit-readiness score in the current prototype.

It returns:

* Score
* Tier
* Recommended support range
* Confidence
* Positive signals
* Risk signals
* Missing data
* Reason codes

Current positioning:

```text
ML produces the credit-readiness score.
Neo4j strengthens the review with relationship evidence.
Featherless explains the score and evidence.
Masumi records the workflow and audit trail.
Human officer makes the final decision.
```

The ML model is used for prototype decision support and should be validated with real lender data before production deployment.

---

## Lovable Frontend

The Lovable-built frontend is the loan officer experience.

It includes:

* Dashboard
* New Review page
* Farmer selection
* Credit-readiness review action
* Review Pack
* Relationship Evidence view
* Activity records
* Workflow Audit powered by Masumi
* Farmer USSD simulator
* Officer USSD simulator
* System Status
* Human outcome recording

### Recommended Dashboard Analytics

The dashboard can show:

* Review Progress Overview
* Credit-Readiness Tier Distribution
* Completed Reviews
* Relationship Evidence Found
* Recent Review Activity
* Agent Module Status

The dashboard should avoid terms such as “approval rate” or “AI decision.”

---

## USSD Simulation

The project includes farmer and officer USSD simulation.

### Farmer USSD

Farmers can:

* Check review status
* Receive safe messages
* View simple review summaries

### Officer USSD

Loan officers can:

* Start a review
* View compact review summary
* Copy farmer-safe message
* Record final human outcome

This is useful for low-bandwidth rural environments where full web dashboard access may not always be available.

---

## API Endpoints

### Health

```http
GET /health
```

Checks whether the backend is running.

---

### Reviews

```http
POST /v1/reviews/{farmer_id}
```

Creates a full credit-readiness review pack for the selected farmer.

---

### Masumi-Compatible Endpoints

```http
GET /availability
GET /input_schema
POST /start_job
GET /status?job_id={job_id}
```

Used to expose the agent as a Masumi-compatible service workflow.

---

### Masumi Job Records

```http
GET /v1/masumi/jobs
GET /v1/masumi/jobs/{job_id}
POST /v1/masumi/jobs/{job_id}/human-outcome
```

Used for job history, detailed job records, and human outcome capture.

---

### Graph Intelligence

```http
GET /v1/graph/status
POST /v1/graph/import-demo
POST /v1/graph/{farmer_id}
```

Used to check Neo4j status, import demo graph data, and retrieve farmer relationship evidence.

---

### Featherless Explanations

```http
POST /v1/explanations/{farmer_id}
```

Generates business explanation outputs for a farmer review.

---

### Farmer USSD

```http
GET /v1/ussd/status
POST /v1/ussd
POST /v1/ussd/simulate
```

---

### Officer USSD

```http
GET /v1/officer-ussd/status
POST /v1/officer-ussd
POST /v1/officer-ussd/simulate
```

---

### Exports

```http
GET /v1/exports/status
GET /v1/exports/review/{farmer_id}/summary
GET /v1/exports/portfolio.csv
GET /v1/exports/demo-evidence-pack
```

---

## Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the backend project.

```env
APP_NAME=Invisible Farmer Credit Review Agent
APP_ENV=local
APP_DEBUG=true

FEATHERLESS_API_KEY=your_featherless_api_key
FEATHERLESS_BASE_URL=https://api.featherless.ai/v1
FEATHERLESS_MODEL=unsloth/Qwen2.5-14B-Instruct

NEO4J_URI=neo4j+s://your-neo4j-uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-neo4j-password
NEO4J_DATABASE=neo4j

MASUMI_MODE=local
MASUMI_PAYMENT_TYPE=local_mocked
MASUMI_ENFORCE_PAYMENT=false
MASUMI_SERVICE_PRICE_AMOUNT=50
MASUMI_SERVICE_PRICE_CURRENCY=ADA
MASUMI_REGISTRY_SERVICE_URL=http://localhost:3000
MASUMI_PAYMENT_SERVICE_URL=http://localhost:3001
MASUMI_AGENT_IDENTIFIER=local-invisible-farmer-credit-review-agent
MASUMI_AGENT_NAME=Invisible Farmer Credit Review Agent
MASUMI_AGENT_VERSION=v2
```

Never commit `.env` to GitHub.

---

## Running the Backend

From the backend directory:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend URL:

```text
http://localhost:8000
```

Swagger/OpenAPI docs are usually available at:

```text
http://localhost:8000/docs
```

---

## Running with Ngrok

If the frontend is hosted on Lovable and your backend is local, expose the backend using ngrok:

```bash
ngrok http 8000
```

Then set the Lovable frontend API base URL to:

```env
VITE_API_BASE_URL=https://your-ngrok-url.ngrok-free.app
```

For ngrok browser warning issues, requests can include:

```http
ngrok-skip-browser-warning: true
```

---

## Example API Requests

### Check Agent Availability

```bash
curl http://localhost:8000/availability
```

---

### Start a Masumi-Compatible Review Job

```bash
curl -X POST http://localhost:8000/start_job \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "F015",
    "requested_by": "Demo Loan Officer - Kakamega Branch",
    "purpose": "Credit-readiness review for input finance"
  }'
```

Expected response includes:

```json
{
  "status": "completed",
  "payment_status": "mocked_confirmed",
  "result_available": true
}
```

---

### Check Job Status

```bash
curl "http://localhost:8000/status?job_id=YOUR_JOB_ID"
```

---

### Run a Direct Review

```bash
curl -X POST http://localhost:8000/v1/reviews/F015
```

---

### Record Human Outcome

```bash
curl -X POST http://localhost:8000/v1/masumi/jobs/YOUR_JOB_ID/human-outcome \
  -H "Content-Type: application/json" \
  -d '{
    "outcome": "Proceed to loan processing",
    "recorded_by": "Demo Loan Officer - Kakamega Branch",
    "notes": "Relationship evidence reviewed. Proceeding to normal lender processing."
  }'
```

---

## Demo Flow

Recommended live demo path:

```text
1. Open Lovable dashboard
2. Show responsible AI banner
3. Select a farmer
4. Click “Perform Credit-Readiness Review”
5. Show the generated Review Pack
6. Show Credit-Readiness Score and support range
7. Show Neo4j Relationship Evidence
8. Show Featherless officer memo and farmer SMS
9. Open Workflow Audit powered by Masumi
10. Record Human Outcome
11. Show Activity or Completed Reviews
12. Export or copy the review pack
```

---

## Responsible AI Boundary

This project is decision support only.

The agent:

* Does not approve loans
* Does not reject farmers
* Does not disburse funds
* Does not replace human loan officers
* Does not replace lender policy
* Does not treat protected characteristics as negative scoring factors

Recommended UI statement:

```text
The agent does not approve, reject, or disburse loans. It prepares decision support for human loan officer review.
```

---

## Measurable Value

A manual thin-file farmer review can take 2–4 hours because officers must collect records, verify relationships, assess risk, prepare internal memos, and document outcomes.

This agent can prepare a structured review pack in about 10–20 minutes.

Estimated savings:

```text
Time saved per farmer review: 1.5–3.5 hours
Reviews per branch per week: 30
Staff hours saved weekly: 45–105 hours
Estimated staff cost: KES 300/hour
Weekly operational value: KES 13,500–31,500
Monthly operational value: KES 54,000–126,000
```

Additional value:

* Faster review turnaround
* Better evidence completeness
* Fewer missing verification steps
* More consistent officer memos
* Stronger audit trail
* Better support for thin-file farmers
* Lower operational review cost
* Better branch-level visibility

---

## Repository Safety

Before pushing to GitHub, ensure your `.gitignore` includes:

```gitignore
.env
.env.local
__pycache__/
*.pyc
node_modules/
dist/
build/
.venv/
venv/
.DS_Store
*.log
*.sqlite3
```

Check what will be committed:

```bash
git status
```

If `.env` was accidentally added:

```bash
git rm --cached .env
git commit -m "Remove env file from tracking"
```

---

## Current Status

Current prototype includes:

* FastAPI backend
* Lovable frontend workflow
* Farmer review creation
* ML credit-readiness scoring
* Neo4j relationship intelligence
* Featherless API explanation layer
* Masumi-compatible job endpoints
* Mocked 50 ADA payment metadata
* Job status tracking
* Audit event recording
* Human outcome recording
* Farmer USSD simulation
* Officer USSD simulation
* Export service
* Dashboard analytics

---

## Future Work

Planned improvements:

* Live Masumi wallet/testnet payment verification
* Real transaction ID and explorer link
* Production lender authentication
* Full SMS gateway integration
* SACCO/MFI pilot deployment
* Real repayment dataset validation
* Expanded fairness testing
* Role-based access control
* Portfolio analytics
* Committee approval workflow
* Farmer consent management
* More robust monitoring and observability

---

## Project Positioning

Invisible Farmer Credit Review Agent is a hybrid AgriFin agent that helps rural lenders review thin-file farmers by combining:

```text
ML credit-readiness scoring
+ Neo4j relationship evidence
+ Featherless business explanations
+ Masumi-compatible workflow audit
+ Farmer-safe SMS/USSD
+ Human loan-officer decision making
```

The goal is not to automate lending decisions. The goal is to make farmer credit review faster, clearer, more auditable, and more inclusive.

---

## License


```text

```

---

## Contact

Project: Invisible Farmer Credit Review Agent
Team: Regenerative Organic Outcomes through Technology
Use case: AgriFin credit-readiness review for thin-file farmers
