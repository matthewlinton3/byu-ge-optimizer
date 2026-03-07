"""
Comprehensive test suite for PathwaySolver — all 13 BYU GE categories.
Run with: python test_pathways.py
"""

from pathways import PathwaySolver, evaluate_pathways, PATHWAYS, get_remaining_requirements
from scraper import init_db, scrape_catalog_for_ge, GE_CATEGORIES
from optimizer import optimize

solver = PathwaySolver()
PASS = "✅"
FAIL = "❌"
results = []


def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((status, label, detail))
    if not condition:
        print(f"  {FAIL} FAILED: {label}  [{detail}]")


# ══════════════════════════════════════════════════════════════════
# 1. AMERICAN HERITAGE
# ══════════════════════════════════════════════════════════════════
print("\n── 1. American Heritage ──")

r = evaluate_pathways("American Heritage", set())
check("AH: empty → cheapest pathway exists", r is not None)
check("AH: empty → 1 course remaining", r and r.courses_remaining == 1)

r = evaluate_pathways("American Heritage", {"AMER H 100"})
check("AH: AMER H 100 taken → complete", r and r.is_complete)
check("AH: AMER H 100 → also_satisfies AmCiv",
      r and "American Civilization" in r.also_satisfies)

r = evaluate_pathways("American Heritage", {"AMER H 200"})
check("AH: AMER H 200 taken → complete", r and r.is_complete)

# Solver cascade: taking AMER H 100 satisfies BOTH AH and AmCiv
state = solver.solve({"AMER H 100"})
check("AH: AMER H 100 cascades to AmCiv completed",
      "American Civilization" in state.completed)
check("AH: AMER H 100 → AH completed",
      "American Heritage" in state.completed)


# ══════════════════════════════════════════════════════════════════
# 2. AMERICAN CIVILIZATION
# ══════════════════════════════════════════════════════════════════
print("\n── 2. American Civilization ──")

r = evaluate_pathways("American Civilization", {"ECON 110"})
check("AmCiv: ECON 110 → selects 2-course pathway (1 remaining)",
      r and r.courses_remaining == 1)
check("AmCiv: ECON 110 pathway has ECON 110 in already_taken",
      r and "ECON 110" in r.already_taken)

r = evaluate_pathways("American Civilization", {"ECON 110", "HIST 220"})
check("AmCiv: ECON 110 + HIST 220 → complete via 2-course pathway",
      r and r.is_complete)

r = evaluate_pathways("American Civilization", {"AMER H 100"})
check("AmCiv: AMER H 100 → complete (single-course pathway)",
      r and r.is_complete)

# Cheapest pathway: ECON 110 taken means need only 1 more; AMER H 100 needs 0 more
# but student doesn't have it — verify it recommends 1-more route
state = solver.solve({"ECON 110"})
check("AmCiv: ECON 110 via SBS also_satisfies cascade → AmCiv completed",
      "American Civilization" in state.completed)


# ══════════════════════════════════════════════════════════════════
# 3. RELIGION (multi-course / credit-gated)
# ══════════════════════════════════════════════════════════════════
print("\n── 3. Religion ──")

r = evaluate_pathways("Religion", set())
check("Religion: empty → 7 courses remaining", r and r.courses_remaining == 7)

r3 = evaluate_pathways("Religion", {"REL A 121", "REL A 122", "REL A 211"})
check("Religion: 3 taken → 4 remaining", r3 and r3.courses_remaining == 4)

r7 = evaluate_pathways("Religion", {
    "REL A 121", "REL A 122", "REL A 211", "REL A 212",
    "REL C 225", "REL A 250", "REL A 275"
})
check("Religion: 7 taken → complete", r7 and r7.is_complete)

# Credit check: 7 courses × 2 credits = 14 credits
check("Religion: 7 taken → credits_remaining == 0",
      r7 and r7.credits_remaining == 0)

# Partial religion detection
state = solver.solve({"REL A 121", "REL A 122"})
check("Religion: 2 taken → in partial (not complete)",
      "Religion" in state.partial)
check("Religion: 2 taken → 5 still needed",
      state.partial.get("Religion") and
      state.partial["Religion"].courses_remaining == 5)


# ══════════════════════════════════════════════════════════════════
# 4. FIRST-YEAR WRITING
# ══════════════════════════════════════════════════════════════════
print("\n── 4. First-Year Writing ──")

r = evaluate_pathways("First-Year Writing", {"WRTG 150"})
check("FYW: WRTG 150 → complete", r and r.is_complete)

r = evaluate_pathways("First-Year Writing", set())
check("FYW: empty → 1 course remaining", r and r.courses_remaining == 1)

state = solver.solve({"WRTG 150"})
check("FYW: WRTG 150 in courses_taken → completed",
      "First-Year Writing" in state.completed)


# ══════════════════════════════════════════════════════════════════
# 5. LANGUAGES OF LEARNING (QUANTITATIVE) — 3 alternative pathways
# ══════════════════════════════════════════════════════════════════
print("\n── 5. Languages of Learning (Quantitative) ──")

for course, label in [("MATH 112", "Math"), ("STAT 121", "Stats"), ("CS 142", "CS")]:
    r = evaluate_pathways("Languages of Learning (Quantitative)", {course})
    check(f"LoL: {course} ({label}) → complete", r and r.is_complete)

r = evaluate_pathways("Languages of Learning (Quantitative)", set())
check("LoL: empty → 1 course remaining", r and r.courses_remaining == 1)

# Solver confirms
state = solver.solve({"CS 142"})
check("LoL: CS 142 → completed via CS pathway",
      "Languages of Learning (Quantitative)" in state.completed)


# ══════════════════════════════════════════════════════════════════
# 6. ARTS — with ART 201 double-dipper
# ══════════════════════════════════════════════════════════════════
print("\n── 6. Arts ──")

r = evaluate_pathways("Arts", {"ART 201"})
check("Arts: ART 201 → complete", r and r.is_complete)
check("Arts: ART 201 → also_satisfies CompCiv",
      r and "Comparative Civilization" in r.also_satisfies)

r = evaluate_pathways("Arts", {"MUSIC 101"})
check("Arts: MUSIC 101 → complete", r and r.is_complete)

state = solver.solve({"ART 201"})
check("Arts: ART 201 cascade → Comparative Civilization also completed",
      "Comparative Civilization" in state.completed)
check("Arts: ART 201 cascade → Arts completed",
      "Arts" in state.completed)


# ══════════════════════════════════════════════════════════════════
# 7. LETTERS — with double-dipper pathways
# ══════════════════════════════════════════════════════════════════
print("\n── 7. Letters ──")

r = evaluate_pathways("Letters", {"HIST 201"})
check("Letters: HIST 201 → complete", r and r.is_complete)
check("Letters: HIST 201 → also_satisfies Global/Cultural",
      r and "Global and Cultural Awareness" in r.also_satisfies)

r = evaluate_pathways("Letters", {"ENGL 340"})
check("Letters: ENGL 340 → complete with Global bonus",
      r and r.is_complete and "Global and Cultural Awareness" in r.also_satisfies)

r = evaluate_pathways("Letters", {"ENGL 251"})
check("Letters: ENGL 251 → complete (standard pathway)",
      r and r.is_complete)

# Solver cascade
state = solver.solve({"HIST 201"})
check("Letters: HIST 201 cascade → Global/Cultural also completed",
      "Global and Cultural Awareness" in state.completed)


# ══════════════════════════════════════════════════════════════════
# 8. LIFE SCIENCES — 3 alternative pathways
# ══════════════════════════════════════════════════════════════════
print("\n── 8. Life Sciences ──")

for course, label in [("BIO 100", "biology"), ("PDBIO 120", "human bio"), ("NDFS 100", "nutrition")]:
    r = evaluate_pathways(
        "Scientific Principles and Reasoning (Life Sciences)", {course}
    )
    check(f"LifeSci: {course} ({label}) → complete", r and r.is_complete)

r = evaluate_pathways("Scientific Principles and Reasoning (Life Sciences)", set())
check("LifeSci: empty → 1 course remaining", r and r.courses_remaining == 1)


# ══════════════════════════════════════════════════════════════════
# 9. PHYSICAL SCIENCES — 3 alternative pathways
# ══════════════════════════════════════════════════════════════════
print("\n── 9. Physical Sciences ──")

for course, label in [("CHEM 101", "chemistry"), ("PHSCS 100", "physics"), ("GEOL 101", "geology")]:
    r = evaluate_pathways(
        "Scientific Principles and Reasoning (Physical Sciences)", {course}
    )
    check(f"PhysSci: {course} ({label}) → complete", r and r.is_complete)


# ══════════════════════════════════════════════════════════════════
# 10. SOCIAL AND BEHAVIORAL SCIENCES — 6 pathways, 2 with bonuses
# ══════════════════════════════════════════════════════════════════
print("\n── 10. Social and Behavioral Sciences ──")

r = evaluate_pathways("Social and Behavioral Sciences", {"ECON 110"})
check("SBS: ECON 110 → complete + AmCiv bonus",
      r and r.is_complete and "American Civilization" in r.also_satisfies)

r = evaluate_pathways("Social and Behavioral Sciences", {"POLI 110"})
check("SBS: POLI 110 → complete + AmCiv bonus",
      r and r.is_complete and "American Civilization" in r.also_satisfies)

r = evaluate_pathways("Social and Behavioral Sciences", {"ANTHR 101"})
check("SBS: ANTHR 101 → complete + Global bonus",
      r and r.is_complete and "Global and Cultural Awareness" in r.also_satisfies)

r = evaluate_pathways("Social and Behavioral Sciences", {"PSYCH 111"})
check("SBS: PSYCH 111 → complete (no bonus)", r and r.is_complete)

# Solver: ANTHR 101 completes SBS + Global
state = solver.solve({"ANTHR 101"})
check("SBS: ANTHR 101 cascade → Global/Cultural completed",
      "Global and Cultural Awareness" in state.completed)


# ══════════════════════════════════════════════════════════════════
# 11. GLOBAL AND CULTURAL AWARENESS — 8 pathways
# ══════════════════════════════════════════════════════════════════
print("\n── 11. Global and Cultural Awareness ──")

r = evaluate_pathways("Global and Cultural Awareness", {"HIST 202"})
check("Global: HIST 202 → complete + CompCiv bonus",
      r and r.is_complete and "Comparative Civilization" in r.also_satisfies)

r = evaluate_pathways("Global and Cultural Awareness", {"ANTHR 101"})
check("Global: ANTHR 101 → complete + SBS bonus",
      r and r.is_complete and "Social and Behavioral Sciences" in r.also_satisfies)

r = evaluate_pathways("Global and Cultural Awareness", {"GEOG 101"})
check("Global: GEOG 101 → complete (standard, no bonus)", r and r.is_complete)

# Solver prefers bonus-carrying pathway
state = solver.solve({"HIST 202"})
check("Global: HIST 202 cascade → CompCiv completed",
      "Comparative Civilization" in state.completed)


# ══════════════════════════════════════════════════════════════════
# 12. COMPARATIVE CIVILIZATION — 5 pathways, all with Global bonus
# ══════════════════════════════════════════════════════════════════
print("\n── 12. Comparative Civilization ──")

for code, label in [
    ("ART 201", "ART 201→Arts"),
    ("HIST 202", "HIST 202→Global"),
    ("PHIL 202", "PHIL 202→Global"),
    ("ASIAN 101", "ASIAN 101→Global"),
    ("LATIN 101", "LATIN 101→Global"),
]:
    r = evaluate_pathways("Comparative Civilization", {code})
    check(f"CompCiv: {code} ({label}) → complete", r and r.is_complete)

r = evaluate_pathways("Comparative Civilization", {"HIST 202"})
check("CompCiv: HIST 202 → also_satisfies Global",
      r and "Global and Cultural Awareness" in r.also_satisfies)


# ══════════════════════════════════════════════════════════════════
# 13. ADVANCED WRITTEN AND ORAL COMMUNICATION — 2 pathways
# ══════════════════════════════════════════════════════════════════
print("\n── 13. Advanced Written and Oral Communication ──")

r = evaluate_pathways("Advanced Written and Oral Communication", {"WRTG 316"})
check("AWOC: WRTG 316 → complete (writing pathway)", r and r.is_complete)

r = evaluate_pathways("Advanced Written and Oral Communication", {"COMM 101"})
check("AWOC: COMM 101 → complete (comm pathway)", r and r.is_complete)

r = evaluate_pathways("Advanced Written and Oral Communication", set())
check("AWOC: empty → 1 course remaining", r and r.courses_remaining == 1)


# ══════════════════════════════════════════════════════════════════
# CROSS-CATEGORY OPTIMIZER TESTS
# ══════════════════════════════════════════════════════════════════
print("\n── Cross-Category Optimizer Tests ──")

init_db()
courses = scrape_catalog_for_ge()

# Test A: Baseline — no courses taken
baseline, _ = optimize(courses, use_ilp=True)
check(f"Optimizer: baseline selects ≤12 courses (got {len(baseline)})",
      len(baseline) <= 12)

# Test B: 5 courses taken — should need fewer recommendations
taken5 = {"ECON 110", "WRTG 150", "MATH 112", "ART 201", "REL A 121"}
state5 = solver.solve(taken5)
completed5 = state5.completed
sel5, unc5 = optimize(courses, use_ilp=True, courses_taken=taken5)

check("Optimizer: 5 courses taken → fewer recommendations than baseline",
      len(sel5) < len(baseline),
      f"{len(sel5)} vs {len(baseline)}")
check("Optimizer: ECON 110 taken → AmCiv not in selected course tags",
      all("American Civilization" not in c.get("ge_categories", []) for c in sel5))
check("Optimizer: ART 201 taken → Arts not in selected course tags",
      all("Arts" not in c.get("ge_categories", []) for c in sel5))
check("Optimizer: 5 courses taken → nothing from taken set recommended",
      all(c["course_code"] not in taken5 for c in sel5))

# Test C: Cheapest pathway — prefer shorter route given partial work
# ANTHR 101 satisfies SBS + Global; optimizer should NOT separately recommend
# a Global course if ANTHR 101 is being recommended for SBS
# (ILP handles this automatically — no duplicate coverage)
taken_anthr = {"ANTHR 101"}
sel_anthr, _ = optimize(courses, use_ilp=True, courses_taken=taken_anthr)
sbs_courses   = [c for c in sel_anthr if "Social and Behavioral Sciences" in c.get("ge_categories", [])]
global_courses = [c for c in sel_anthr if "Global and Cultural Awareness" in c.get("ge_categories", [])]
check("Optimizer: ANTHR 101 satisfies SBS → no extra SBS course recommended",
      len(sbs_courses) == 0)
check("Optimizer: ANTHR 101 satisfies Global → no extra Global course recommended",
      len(global_courses) == 0)

# Test D: Never recommends a longer pathway when shorter exists
# If HIST 202 is taken (satisfies Global + CompCiv), don't also recommend
# a separate CompCiv course
taken_hist202 = {"HIST 202"}
sel_h, _ = optimize(courses, use_ilp=True, courses_taken=taken_hist202)
compciv_courses = [c for c in sel_h if "Comparative Civilization" in c.get("ge_categories", [])]
check("Optimizer: HIST 202 taken → no redundant CompCiv course recommended",
      len(compciv_courses) == 0)

# Test E: All 13 categories covered with minimum courses
# Without any pre-taken courses, verify all 13 categories are covered
all_covered = set(cat for c in baseline for cat in c.get("ge_categories", []))
check("Optimizer: baseline covers all 13 GE categories",
      len(all_covered) == 13,
      f"covered: {len(all_covered)}")

# Test F: Religion partial — 4 taken, need 3 more
taken_rel4 = {"REL A 121", "REL A 122", "REL A 211", "REL A 212"}
state_rel = solver.solve(taken_rel4)
check("Religion: 4 taken → in partial, 3 remaining",
      "Religion" in state_rel.partial and
      state_rel.partial["Religion"].courses_remaining == 3)


# ══════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════
print("\n" + "═" * 60)
passed = sum(1 for s, _, _ in results if s == PASS)
failed = sum(1 for s, _, _ in results if s == FAIL)
total  = len(results)

print(f"  {PASS} {passed}/{total} tests passed")
if failed:
    print(f"  {FAIL} {failed}/{total} tests FAILED:")
    for status, label, detail in results:
        if status == FAIL:
            print(f"      • {label}  [{detail}]")
else:
    print("  All pathway tests passed — universal pathway logic verified ✅")
print("═" * 60)

# Exit with non-zero status if any failures
if failed:
    import sys
    sys.exit(1)
