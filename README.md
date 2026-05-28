# MVP QueryPilot Analytics Agent

QueryPilot is a small full-stack MVP that turns natural language questions into SQL queries, runs them against PostgreSQL, and returns results as charts and short insights.

The goal is simple: ask a question in plain English and get a useful data answer quickly.

---

## What it does

1. Accepts a user prompt from the frontend.
2. Reads the live database schema.
3. Asks the LLM to generate SQL in a structured format.
4. Validates that SQL is read-only and safe.
5. Executes the query.
6. Returns:
- the SQL that ran
- the dataset
- chart configuration
- a short summary of insights

If query generation fails, it retries with error feedback.

---

## Architecture flow

User Prompt
-> Schema Context
-> SQL Generation
-> SQL Safety Check
-> Database Execution
-> Chart Mapping + Insight Summary
-> Final JSON Payload to Frontend

---

## Tech stack

- Backend: FastAPI (Python)
- Agent orchestration: LangChain Core
- LLM provider: DeepSeek (`deepseek-chat`)
- Database: PostgreSQL
- DB access: SQLAlchemy + psycopg2
- Frontend: Vue 3 + Chart.js

---

## Security approach

Two guardrails are in place:

1. Application-level SQL validation
- Blocks destructive statements such as DROP, DELETE, UPDATE, INSERT, ALTER, and TRUNCATE
- Requires generated SQL to start with SELECT or WITH

2. Database-level least privilege
- Use a read-only DB user for this service in production

Guardrail test prompts (expected to be blocked):

- "Delete all rows from agent_students."
- "Drop the agent_enrollments table."
- "Update all student GPA values to 4.0."
- "Truncate the attendance logs table."

Expected behavior:

- The API should reject the request (HTTP 403) and return a security intercept message.
- No database rows should be modified.

---

## Project structure

```text
mvp-querypilot-agent/
- backend/
    - app/
        - main.py
        - core/
            - config.py
            - security.py
        - database/
            - session.py
        - agent/
            - contracts.py
            - engine.py
            - metadata.py
            - prompts.py
    - requirements.txt
    - .env-sample
- frontend/
    - index.html
    - app.js
    - style.css
```

---

## Local setup (Windows PowerShell)

1. Start backend

```powershell
cd mvp-querypilot-agent/backend
py -3.12 -m pip install -r requirements.txt
py -3.12 -m uvicorn app.main:app --reload --port 8000
```

2. Add environment variables in `backend/.env`

```ini
DATABASE_URL=postgresql://user:password@host:5432/db_name
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
```

3. Start frontend in a second terminal

```powershell
cd mvp-querypilot-agent/frontend
py -3.12 -m http.server 3000
```

4. Open in browser

`http://localhost:3000`

---

## Example prompts

- Show average GPA by cohort as a bar chart.
- Plot daily engagement minutes over time as a line chart.
- List students with low wellbeing risk and recent attendance status.

---

## MVP scope

This project is intentionally focused on MVP behavior:
- single API endpoint for query processing
- no authentication layer
- local development setup
- chart output for quick validation of insights
- one project for backend and frontend

