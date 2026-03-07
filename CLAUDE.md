# BYU GE Optimizer — Claude Code Context

## What This Project Does

A Streamlit web app that helps BYU students find the **minimum number of courses** needed to complete all 13 General Education (GE) requirements. Key features:

- Upload a BYU MyMap degree audit PDF to auto-detect completed GE requirements
- Runs set-cover optimization (ILP or greedy) to find fewest remaining courses
- Maximizes "double-dippers" — courses satisfying multiple GE categories at once
- Enriches results with RateMyProfessors ratings so students can pick the best teachers
- Understands flexible BYU pathways (e.g., AMER H 100 satisfies both American Heritage AND American Civilization)

Deployed on Railway at: https://byu-ge-optimizer.up.railway.app (or similar)

---

## File Structure

```
byu-ge-optimizer/
├── app.py              # Streamlit web UI — main entry point
├── main.py             # CLI interface (same logic, Rich output)
├── optimizer.py        # Set-cover optimization (ILP via PuLP + greedy fallback)
├── pathways.py         # All 13 BYU GE categories defined with flexible pathways
├── scraper.py          # BYU catalog scraper + SQLite caching
├── rmp.py              # RateMyProfessors GraphQL API integration
├── mymap_scraper.py    # BYU CAS login + MyMap degree audit scraper (primary input method)
├── pdf_parser.py       # MyMap degree audit PDF parser (pdfplumber) — fallback
├── display.py          # Rich CLI output formatting
├── test_pathways.py    # 71-test suite (run: python test_pathways.py)
├── ge_courses.db       # SQLite DB — cached courses + professor ratings
├── requirements.txt    # Python dependencies
├── Procfile            # Railway: streamlit run app.py --server.port=$PORT ...
└── railway.toml        # Railway: nixpacks builder, restart on failure
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| Optimization | PuLP (ILP/CBC solver) + greedy fallback |
| PDF parsing | pdfplumber |
| HTML scraping | BeautifulSoup4 + lxml + requests |
| Database | SQLite3 (local file: `ge_courses.db`) |
| CLI output | Rich |
| Data | Pandas |
| Deployment | Railway (nixpacks) |

No external dependencies beyond `requirements.txt`. No environment variables required.

---

## All 13 GE Categories

Defined in `pathways.py` with flexible completion pathways:

1. **American Heritage** — AMER H 100 (also completes American Civilization) or AMER H 200
2. **American Civilization** — AMER H 100 alone OR 2 qualifying courses (ECON 110, HIST 220, etc.)
3. **Religion** — 14 credit hours (7 × 2-credit REL courses) — has explicit course pool
4. **First-Year Writing** — WRTG 150 or approved equivalents
5. **Advanced Written & Oral Communication** — upper-division writing or communication
6. **Languages of Learning (Quantitative)** — Math, Stats, or CS courses
7. **Arts** — standard arts OR ART 201 (double-dips with Comparative Civilization)
8. **Letters** — literature/philosophy OR HIST 201/ENGL 340 (double-dip with Global/Cultural)
9. **Life Sciences** — Biology, Human Biology, or Nutrition
10. **Physical Sciences** — Chemistry, Physics, or Geology
11. **Social & Behavioral Sciences** — 6 options; ECON 110 → also satisfies American Civilization; ANTHR 101 → also satisfies Global Awareness
12. **Global & Cultural Awareness** — 8 options with various synergies
13. **Comparative Civilization** — 5 options, all carry Global/Cultural bonus

Cascade bonuses are handled automatically by `PathwaySolver` — taking one course can mark multiple categories complete.

---

## How the Optimizer Works

```
1. PathwaySolver evaluates all 13 categories given student's taken courses
   → Detects partial completions, applies cascade bonuses

2. Prune BYU catalog to only courses covering remaining categories

3. Inject synthetic "__pathway_<cat>" tags on courses that cheaply complete partial requirements

4. ILP (PuLP/CBC):
   Minimize: Σ selected_courses
   Subject to: For each remaining GE category, ≥1 course covers it
   → Guaranteed minimum course count

   Greedy fallback: Repeatedly pick course covering most uncovered categories

5. Enrich with RateMyProfessors ratings (cached in SQLite)

6. Sort by priority: Most GE categories → highest RMP → easiest
```

---

## Key Modules

### `pathways.py` (707 lines)
- `Pathway` dataclass: `required_courses`, `also_satisfies`, `credit_hours`, `requires_all`
- `PathwaySolver` class — evaluates all 13 categories, detects partials, cascades bonuses
- `SolveResult` dataclass — completed, partial, not_started, recommendations

### `optimizer.py`
- `optimize_courses(catalog, remaining_reqs, taken_courses)` — main entry point
- `_solve_ilp()` — PuLP solver
- `_solve_greedy()` — fallback

### `scraper.py`
- Scrapes `catalog.byu.edu/search` with BeautifulSoup
- Falls back to 45-course seed data if live scrape returns < 10 results
- Caches in SQLite `courses` table

### `rmp.py`
- GraphQL queries to RateMyProfessors
- BYU school ID: `U2Nob29sLTEzNQ==`
- Hardcoded auth: `"Basic dGVzdDp0ZXN0"` (test:test) — may need updating if rate-limited
- 110 dept-prefix → RMP department name mappings
- Caches in SQLite `professors` table

### `mymap_scraper.py` (primary input method)
- `login_and_scrape(netid, password)` — BYU CAS SSO login + full degree audit scrape
- CAS flow: GET mymap.byu.edu → follow redirect to cas.byu.edu → parse form → POST creds → follow redirect back
- Detects Duo 2FA and returns a clear error (can't automate MFA)
- Scrapes multiple MyMap paths to find degree audit content
- `_parse_html_structure()` — tries DOM selectors first (more accurate)
- `_parse_text_lines()` — line-by-line fallback scan
- `format_debug_report()` — full human-readable debug dump shown in UI before optimizer runs
- **Security**: credentials zeroed out immediately after POST; never logged, stored, or serialized

### `pdf_parser.py` (fallback input method)
- Uses pdfplumber to extract text from MyMap PDFs
- Regex pattern matching per GE category
- Returns confidence level: "high" / "medium" / "low"

### `app.py`
- **Step 1** has three tabs: "Log in to MyMap" (primary) | "Upload PDF" (fallback) | "Manual Entry" (fallback)
  - MyMap tab: NetID + password form → calls `login_and_scrape()` → shows full debug expander → shows structured GE status
  - PDF tab: pdfplumber parse → shows summary
  - Manual tab: checkboxes for all 13 categories → "Apply" button
- Prominent privacy notice always visible
- `data_source` session state key: "mymap" | "pdf" | "manual"
- **Results tabs** (after optimizer runs):
  - **Tab 1:** Recommended Courses — sortable table with color-coded RMP ratings
  - **Tab 2:** Full GE Map — visual coverage summary
  - **Tab 3:** Double-Dippers — courses satisfying 2+ GE requirements
- Sort priorities: Balanced / Fewest Classes / Best Professor / Easiest
- CSV export button

---

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run web app
streamlit run app.py

# Run CLI
python main.py              # uses cached DB
python main.py --refresh    # re-scrapes BYU catalog
python main.py --greedy     # skip ILP, use greedy
python main.py --no-rmp     # skip RateMyProfessors lookup

# Run tests
python test_pathways.py     # 71 tests, ~2-3 seconds
```

---

## Known Issues & Limitations

1. **MyMap CAS login / Duo 2FA** — If the user has Duo MFA enabled, automated login fails; detected and shown as a clear error; user falls back to PDF/manual
2. **MyMap HTML structure unknown** — The exact DOM structure of mymap.byu.edu's degree audit is untested; the debug output expander is essential on first run to verify parsing accuracy; HTML selectors and text-scan patterns may need tuning
3. **RMP auth token** — `"Basic dGVzdDp0ZXN0"` is hardcoded; may get rate-limited or blocked
4. **PDF parsing** — Fails on scanned/image PDFs (requires selectable text); low-confidence fallback to manual
5. **BYU catalog scraper** — Multiple CSS selectors tried; falls back to 45-course seed if live scrape fails; seed data has no RMP ratings
6. **Religion course pool** — Explicitly defined; other categories rely on dept_prefix matching which may miss some valid courses
7. **ILP performance** — Slow for catalogs > 100 courses (rare in practice)
8. **Credit-hour estimates** — All Religion courses assumed 2 credits; shown as "~X credits"
9. **No README.md** — Documentation lives in this file + code docstrings + test file

---

## Deployment (Railway)

- Builder: nixpacks (auto-detects Python from `requirements.txt`)
- Start: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
- Restart policy: on_failure
- SQLite DB is ephemeral on Railway (resets on redeploy) — catalog re-scraped on first run

---

## Tests

`test_pathways.py` — 71 unit & integration tests:
- All 13 GE categories individually
- Cascade bonus logic (AMER H 100 → both Heritage + Civilization)
- Partial completion detection (e.g., 3 of 7 Religion courses taken)
- Optimizer never recommends already-completed categories
- Minimum course count verification

Run with: `python test_pathways.py`
