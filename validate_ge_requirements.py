#!/usr/bin/env python3
"""
Validate GE Requirements — cross-check transcript course codes against ge_requirements.py.

Usage:
  python validate_ge_requirements.py <path_to_degree_audit.pdf>
  python validate_ge_requirements.py --courses "ECON 110, PHY S 100, REL C 352"

Any course code that appears in the transcript (or --courses list) but is not
listed in any category in GE_REQUIREMENTS is printed as a missing mapping.
Exit code: 0 if no missing mappings, 1 otherwise.
"""

import sys
import re

from ge_requirements import GE_REQUIREMENTS

# Same regex as pdf_parser for normalizing course codes from --courses
COURSE_CODE_RE = re.compile(r"\b([A-Z]{2,6}(?:\s+[A-Z])?\s+\d{3}[A-Z]?)\b")


def all_mapped_codes():
    """Return the set of every course code that appears in GE_REQUIREMENTS."""
    codes = set()
    for cat_codes in GE_REQUIREMENTS.values():
        codes.update(cat_codes)
    return codes


def courses_from_pdf(pdf_path: str) -> set:
    """Extract course codes from a degree audit PDF (same logic as app)."""
    import io
    from pdf_parser import extract_text_from_pdf, extract_courses_taken

    with open(pdf_path, "rb") as f:
        raw = f.read()
    text = extract_text_from_pdf(io.BytesIO(raw))
    return extract_courses_taken(text)


def courses_from_arg(courses_arg: str) -> set:
    """Parse --courses "CODE1, CODE2, ..." into a set of normalized codes."""
    normalized = set()
    for part in courses_arg.split(","):
        part = part.strip()
        # Allow "ECON 110" or "ECON  110" (multiple spaces) -> normalize to single space
        part = re.sub(r"\s+", " ", part).strip()
        if part and COURSE_CODE_RE.match(part):
            normalized.add(part)
        elif part:
            # Try to extract a code from the part
            m = COURSE_CODE_RE.search(part)
            if m:
                normalized.add(re.sub(r"\s+", " ", m.group(1)).strip())
    return normalized


def main():
    mapped = all_mapped_codes()
    transcript_courses = set()

    if len(sys.argv) < 2:
        print("Usage: python validate_ge_requirements.py <degree_audit.pdf>", file=sys.stderr)
        print("   or: python validate_ge_requirements.py --courses \"ECON 110, PHY S 100\"", file=sys.stderr)
        sys.exit(2)

    if sys.argv[1] == "--courses":
        if len(sys.argv) < 3:
            print("Missing argument for --courses", file=sys.stderr)
            sys.exit(2)
        transcript_courses = courses_from_arg(sys.argv[2])
    else:
        pdf_path = sys.argv[1]
        try:
            transcript_courses = courses_from_pdf(pdf_path)
        except Exception as e:
            print(f"Error reading PDF: {e}", file=sys.stderr)
            sys.exit(2)

    missing = sorted(transcript_courses - mapped)
    if missing:
        print("Course codes from transcript not found in ge_requirements.py:")
        for code in missing:
            print(f"  {code}")
        sys.exit(1)

    print("All transcript course codes are mapped in ge_requirements.py.")
    sys.exit(0)


if __name__ == "__main__":
    main()
