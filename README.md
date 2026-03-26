# BYU GE Optimizer

Finds the **minimum number of courses** needed to complete all 13 BYU General Education requirements, with RateMyProfessors ratings so you can pick the best professors.

**Live app:** https://byu-ge-optimizer.up.railway.app

---

## What it does

1. **Import your degree audit** — upload your MyMap PDF, or manually check off completed categories.
2. **Optimizer runs** — uses Integer Linear Programming (ILP) to find the fewest remaining courses that cover every unfulfilled GE category.
3. **Results with professor ratings** — each recommended course shows RateMyProfessors scores for current instructors.
4. **Double-dippers highlighted** — courses that satisfy two or more GE categories at once.
5. **Schedule generator** — lock courses you want, set your availability (blackout times), and get conflict-free section options.

---

## Running locally

```bash
# 1. Clone
git clone https://github.com/matthewlinton3/byu-ge-optimizer.git
cd byu-ge-optimizer

# 2. Install Python dependencies (Python 3.11+ recommended)
pip install -r requirements.txt

# 3. Run the web app
streamlit run app.py
```

The app opens at http://localhost:8501.

Optional CLI (outputs to terminal with Rich formatting):
```bash
python main.py              # uses cached DB
python main.py --refresh    # re-scrapes BYU catalog
python main.py --greedy     # faster greedy algorithm instead of ILP
python main.py --no-rmp     # skip RateMyProfessors lookup
```

Run the test suite:
```bash
python test_pathways.py     # 71 unit tests, ~2-3 seconds
```

---

## How to get your degree audit PDF

1. Go to [mymap.byu.edu](https://mymap.byu.edu) and log in with your NetID.
2. Open **Degree Audit** from the left sidebar.
3. In your browser, go to **Print → Save as PDF**.
4. Upload the saved PDF in the app's Step 1.

The app processes the PDF entirely in-memory and never stores it.

---

## All 13 GE categories

| Category | Notes |
|----------|-------|
| American Heritage | AMER H 100 also satisfies American Civilization |
| American Civilization | AMER H 100, or HIST 220/221 + others |
| Religion | 14 credit hours (~7 × 2-credit REL courses) |
| First-Year Writing | WRTG 150 or equivalent |
| Advanced Written & Oral Communication | Upper-division writing or COMM |
| Languages of Learning (Quantitative) | Math, Stats, or CS |
| Arts | Includes ART 201 (also Comparative Civ) |
| Letters | Literature, philosophy; HIST 201 double-dips with Global |
| Life Sciences | BIO, PDBIO, NDFS, MMBIO |
| Physical Sciences | CHEM, PHSCS, GEOL, GEOG 111 |
| Social & Behavioral Sciences | PSYCH, SOC, ECON 110, POLI 110, ANTHR 101 |
| Global & Cultural Awareness | GEOG, ANTHR, HIST 201/202, ENGL 340 |
| Comparative Civilization | HIST 202, PHIL 202, ASIAN 101, LATIN 101 |

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| Optimization | PuLP (ILP/CBC solver) + greedy fallback |
| PDF parsing | pdfplumber + Tesseract OCR (for scanned PDFs) |
| HTML scraping | BeautifulSoup4 + lxml + requests |
| Database | SQLite (ephemeral on Railway, re-seeded each deploy) |
| Professor ratings | RateMyProfessors GraphQL API |
| Schedule data | BYU class schedule API (commtech.byu.edu) |
| Deployment | Railway (nixpacks) |

---

## Known limitations

- **Duo 2FA** — the MyMap login flow can't automate Duo MFA. Use the PDF upload instead.
- **Scanned PDFs** — OCR fallback is available if Tesseract is installed; quality depends on scan resolution.
- **Religion credit hours** — all REL courses are assumed to be 2 credits. The optimizer counts 7 courses (14 credit hours) as completion.
- **RMP ratings** — only available for professors currently listed in the BYU class schedule. New or rarely-scheduled professors may show no rating.
- **ILP performance** — slightly slow for very large catalogs (> 150 courses). Use the greedy toggle in the sidebar for faster results.

---

## Deployment (Railway)

The app is deployed to Railway using nixpacks (auto-detected Python). Key settings in `railway.toml`:

```toml
startCommand = "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless true"
healthcheckPath = "/_stcore/health"
```

`nixpacks.toml` installs Tesseract for OCR support.

To redeploy, push to `main`:
```bash
git push origin main
```
