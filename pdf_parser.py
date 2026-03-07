"""
BYU MyMap Degree Audit PDF Parser
Parses a BYU degree audit PDF to detect which GE requirements are already completed.
"""

import re
from scraper import GE_CATEGORIES

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

# ── Keyword patterns for each GE category ────────────────────────────────────
# Each category maps to a list of regex patterns that might appear in the PDF.
# BYU MyMap uses various labels depending on the year/major, so we cast a wide net.

GE_PATTERNS = {
    "American Heritage": [
        r"american heritage",
        r"amer\s*h\s*\d+",
        r"american heritage.*satisfied",
        r"american heritage.*complete",
    ],
    "Religion": [
        r"religion requirement",
        r"religious education",
        r"rel\s*[ac]\s*\d+.*complete",
        r"14.*religion.*credit",
        r"religion.*14.*credit",
        r"religion courses.*satisfied",
    ],
    "First-Year Writing": [
        r"first.year writing",
        r"wrtg\s*150",
        r"writing 150",
        r"freshman writing",
        r"first year writing.*satisfied",
        r"first year writing.*complete",
    ],
    "Advanced Written and Oral Communication": [
        r"advanced written",
        r"oral communication",
        r"adv.*written.*oral",
        r"written.*oral.*comm",
        r"wrtg\s*3\d\d",
        r"comm\s*\d+.*satisfied",
        r"advanced writing.*complete",
    ],
    "Languages of Learning (Quantitative)": [
        r"languages of learning",
        r"quantitative reasoning",
        r"quantitative literacy",
        r"math\s*\d+.*satisfied",
        r"stat\s*\d+.*satisfied",
        r"languages of learning.*satisfied",
        r"lol.*quantitative",
    ],
    "Arts": [
        r"\barts\b.*ge",
        r"ge.*\barts\b",
        r"arts distribution",
        r"creative arts",
        r"arts.*satisfied",
        r"arts.*complete",
        r"fine arts",
    ],
    "Letters": [
        r"\bletters\b.*ge",
        r"ge.*\bletters\b",
        r"letters distribution",
        r"letters.*satisfied",
        r"letters.*complete",
        r"humanities.*letters",
    ],
    "Scientific Principles and Reasoning (Life Sciences)": [
        r"life sciences?",
        r"biological sciences?",
        r"life sci.*satisfied",
        r"scientific.*life",
        r"bio\s*\d+.*satisfied",
        r"pdbio\s*\d+.*satisfied",
    ],
    "Scientific Principles and Reasoning (Physical Sciences)": [
        r"physical sciences?",
        r"phys sci.*satisfied",
        r"scientific.*physical",
        r"chem\s*\d+.*satisfied",
        r"phscs\s*\d+.*satisfied",
        r"geol\s*\d+.*satisfied",
    ],
    "Social and Behavioral Sciences": [
        r"social and behavioral",
        r"social.*behavioral.*satisfied",
        r"behavioral sciences?",
        r"social sciences?.*satisfied",
        r"psych\s*\d+.*satisfied",
        r"soc\s*\d+.*satisfied",
    ],
    "American Civilization": [
        r"american civilization",
        r"amer.*civ.*satisfied",
        r"american civ.*complete",
        r"hist\s*2[12]\d.*satisfied",
    ],
    "Global and Cultural Awareness": [
        r"global.*cultural",
        r"cultural awareness",
        r"global awareness.*satisfied",
        r"global.*satisfied",
        r"multicultural",
    ],
    "Comparative Civilization": [
        r"comparative civilization",
        r"comp.*civ.*satisfied",
        r"comparative civ.*complete",
    ],
}

# Phrases that indicate a requirement is COMPLETED in MyMap output
COMPLETION_SIGNALS = [
    r"satisfied",
    r"complete[d]?",
    r"fulfilled",
    r"met\b",
    r"earned",
    r"passed",
    r"\[x\]",
    r"✓",
    r"✔",
]

COMPLETION_PATTERN = re.compile(
    "|".join(COMPLETION_SIGNALS), re.IGNORECASE
)


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract all text from an uploaded PDF using pdfplumber."""
    if not HAS_PDFPLUMBER:
        raise ImportError("pdfplumber is not installed.")

    import io
    raw_bytes = uploaded_file.read()
    text_pages = []

    with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text)

    return "\n".join(text_pages)


def find_completed_categories(text: str) -> dict:
    """
    Scan PDF text and return a dict of:
      { category_name: True/False }
    True = likely completed, False = not detected as complete.
    """
    text_lower = text.lower()
    results = {}

    for category, patterns in GE_PATTERNS.items():
        category_found = False
        for pattern in patterns:
            matches = list(re.finditer(pattern, text_lower))
            if not matches:
                continue

            # Check a window of text around each match for completion signals
            for match in matches:
                start = max(0, match.start() - 120)
                end = min(len(text_lower), match.end() + 120)
                window = text_lower[start:end]

                if COMPLETION_PATTERN.search(window):
                    category_found = True
                    break

            if category_found:
                break

        results[category] = category_found

    return results


def parse_degree_audit(uploaded_file) -> dict:
    """
    Main entry point. Takes a Streamlit UploadedFile object.
    Returns a dict with keys:
      - completed: set of category names already done
      - remaining: set of category names still needed
      - raw_text: the extracted PDF text (for debug)
      - parse_confidence: "high" | "medium" | "low"
      - error: None or error string
    """
    result = {
        "completed": set(),
        "remaining": set(GE_CATEGORIES.keys()),
        "raw_text": "",
        "parse_confidence": "low",
        "error": None,
    }

    if not HAS_PDFPLUMBER:
        result["error"] = "pdfplumber is not installed on this server."
        return result

    try:
        raw_text = extract_text_from_pdf(uploaded_file)
        result["raw_text"] = raw_text

        if not raw_text or len(raw_text.strip()) < 100:
            result["error"] = "PDF appears to be empty or image-based (scanned). Cannot extract text."
            return result

        category_results = find_completed_categories(raw_text)

        completed = {cat for cat, done in category_results.items() if done}
        remaining = set(GE_CATEGORIES.keys()) - completed

        result["completed"] = completed
        result["remaining"] = remaining

        # Estimate confidence based on how much BYU-like text we found
        byu_signals = len(re.findall(
            r"byu|brigham young|mymap|degree audit|ge requirement|general education",
            raw_text.lower()
        ))

        if byu_signals >= 5:
            result["parse_confidence"] = "high"
        elif byu_signals >= 2:
            result["parse_confidence"] = "medium"
        else:
            result["parse_confidence"] = "low"

    except Exception as e:
        result["error"] = f"Failed to parse PDF: {str(e)}"

    return result
