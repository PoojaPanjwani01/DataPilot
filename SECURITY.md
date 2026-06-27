# DataPilot Security Model & Hardening Guardrails

This document describes the defense-in-depth security model implemented in DataPilot to protect database storage systems from malicious inputs, SQL injections, and resource-exhaustion attacks.

---

## 🔒 Security Architecture Overview

DataPilot implements security at multiple layers, combining application-level syntax inspection with database-level access exclusions:

```
[User Request] 
      │
      ▼
[API Gateway: Rate Limiting Middleware] ── Blocks DDoS & brute force
      │
      ▼
[LLM Context: Security Directive Prompt] ─ Guides translation to SELECT only
      │
      ▼
[Guard Service: AST parser (SQLGlot)] ── Rejects modifying statements, blocks stacked commands
      │
      ▼
[SQLAlchemy Connection Driver] ──────── Enforces 10-second statement execution timeout
      │
      ▼
[PostgreSQL Database Engine] ────────── Restricts execution to the db_readonly user
```

---

## 🛡️ Key Hardening Safeguards

### 1. Abstract Syntax Tree (AST) Audit Validator
DataPilot does not rely on simple regex checks to parse SQL inputs. Instead, the `guard_service` uses `SQLGlot` to parse generated SQL strings into an Abstract Syntax Tree (AST).
- **SELECT-only Enforcement**: Checks the root node of the AST. The statement must resolve exclusively to a `Select` syntax node. Modifying commands (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `GRANT`) are mathematically blocked and fail-fast before database submission.
- **Stacked Query Blocks**: Ensures that exactly one SELECT statement is parsed. Semicolons are not allowed to separate commands, blocking multi-statement SQL injection attacks.
- **Limit Clause Injection**: If the query lacks a `LIMIT` instruction, the validator automatically rewrites the AST to inject `LIMIT 100`. This safeguards server memory from excessive unbounded row scans.

### 2. Read-only PostgreSQL Accounts (`db_readonly`)
At the storage level, the API backend gateway establishes database sessions utilizing the `db_readonly` credential.
- This role is explicitly stripped of all schema write privileges (`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `ALTER`, `DROP`).
- Even if a request somehow bypassed the AST validator, PostgreSQL would immediately abort the statement execution and throw an access-denied exception, guaranteeing absolute data integrity.

### 3. API Transaction Rate Limiting
To prevent service denial, rate-limiting rules are enforced at the API gateway middleware layer per client IP address:
- **Query Endpoints (`/query`, `/insights`)**: Restricted to a maximum of **30 requests per minute**.
- **Upload Endpoints (`/upload/preview`, `/upload/import`)**: Restricted to a maximum of **10 uploads per hour**.

### 4. Raw File Upload Safeguards
The `file_validator` service screens every dynamic dataset uploaded by users:
- **File Extensions**: Restricts uploads strictly to `.csv` and `.xlsx` MIME-types.
- **Size Limitation**: Rejects files larger than **50 MB**.
- **Structural Sanity**: Prevents duplicate header column names, empty tables, and columns exceeding schema boundaries (max 200 columns, max 100,000 rows).

---

## ⚠️ Known Limitations
* **Complex Subqueries**: Generated queries containing multi-level nested subqueries or recursive common table expressions (CTEs) may occasionally trigger AST complexity flags and be rejected if they resemble union/modify structures.
* **Large Join Queries**: Joins across multiple dynamically uploaded tables and core database tables might struggle to resolve properly if the columns lack foreign key mappings.
