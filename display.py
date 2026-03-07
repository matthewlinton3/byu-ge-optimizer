"""
Rich CLI display for BYU GE Optimizer output.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich import box
from scraper import GE_CATEGORIES

console = Console()


def rating_color(rating):
    if rating >= 4.0:
        return "bright_green"
    elif rating >= 3.0:
        return "yellow"
    elif rating > 0:
        return "red"
    else:
        return "dim"


def difficulty_color(diff):
    if diff <= 2.5:
        return "bright_green"
    elif diff <= 3.5:
        return "yellow"
    elif diff > 0:
        return "red"
    else:
        return "dim"


def format_categories(categories):
    short_names = {
        "American Heritage": "Amer Heritage",
        "Religion": "Religion",
        "First-Year Writing": "FY Writing",
        "Advanced Written and Oral Communication": "Adv Writing",
        "Languages of Learning (Quantitative)": "Quantitative",
        "Arts": "Arts",
        "Letters": "Letters",
        "Scientific Principles and Reasoning (Life Sciences)": "Life Sci",
        "Scientific Principles and Reasoning (Physical Sciences)": "Phys Sci",
        "Social and Behavioral Sciences": "Social/Behav",
        "American Civilization": "Amer Civ",
        "Global and Cultural Awareness": "Global/Cultural",
        "Comparative Civilization": "Comp Civ",
    }
    return ", ".join(short_names.get(c, c) for c in categories)


def print_header():
    console.print()
    console.print(Panel.fit(
        "[bold bright_blue]🎓 BYU GE Optimizer[/bold bright_blue]\n"
        "[dim]Find the fewest courses to fulfill all GE requirements[/dim]",
        border_style="bright_blue",
    ))
    console.print()


def print_results(selected_courses, uncovered_categories):
    print_header()

    # ── Course Table ──────────────────────────────────────────────
    table = Table(
        title="📚 Recommended GE Courses",
        box=box.ROUNDED,
        border_style="bright_blue",
        header_style="bold bright_blue",
        show_lines=True,
    )

    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Course", style="bold", width=14)
    table.add_column("Name", width=28)
    table.add_column("Cr", justify="center", width=3)
    table.add_column("GE Categories", width=30)
    table.add_column("Top Professor", width=20)
    table.add_column("Rating", justify="center", width=7)
    table.add_column("Diff", justify="center", width=5)
    table.add_column("WTA%", justify="center", width=6)

    for i, course in enumerate(selected_courses, 1):
        profs = course.get("professors", [])
        top_prof = profs[0] if profs else None

        prof_name = top_prof["name"] if top_prof else "[dim]N/A[/dim]"

        rating = top_prof["rating"] if top_prof else 0
        difficulty = top_prof["difficulty"] if top_prof else 0
        wta = top_prof["would_take_again"] if top_prof else -1

        rating_str = f"[{rating_color(rating)}]{rating:.1f}[/{rating_color(rating)}]" if rating else "[dim]N/A[/dim]"
        diff_str = f"[{difficulty_color(difficulty)}]{difficulty:.1f}[/{difficulty_color(difficulty)}]" if difficulty else "[dim]N/A[/dim]"
        wta_str = f"[bright_green]{wta:.0f}%[/bright_green]" if wta >= 0 else "[dim]N/A[/dim]"

        cats = course.get("ge_categories", [])
        cat_str = format_categories(cats)

        # Highlight courses that double-dip
        row_style = "bold" if len(cats) > 1 else ""

        table.add_row(
            str(i),
            f"[cyan]{course['course_code']}[/cyan]",
            course["course_name"],
            str(course.get("credit_hours", 3)),
            f"[bright_yellow]{cat_str}[/bright_yellow]" if len(cats) > 1 else cat_str,
            prof_name,
            rating_str,
            diff_str,
            wta_str,
            style=row_style,
        )

    console.print(table)
    console.print()

    # ── Summary Panel ─────────────────────────────────────────────
    all_categories = set(GE_CATEGORIES.keys())
    covered = all_categories - set(uncovered_categories)
    total_credits = sum(c.get("credit_hours", 3) for c in selected_courses)

    summary_lines = []
    summary_lines.append(f"[bold]Total courses:[/bold] {len(selected_courses)}")
    summary_lines.append(f"[bold]Total credits:[/bold] ~{total_credits}")
    summary_lines.append(f"[bold]GE categories covered:[/bold] {len(covered)}/{len(all_categories)}")
    summary_lines.append("")

    summary_lines.append("[bold underline]✅ Covered:[/bold underline]")
    for cat in sorted(covered):
        summary_lines.append(f"  [bright_green]✓[/bright_green] {cat}")

    if uncovered_categories:
        summary_lines.append("")
        summary_lines.append("[bold underline]❌ Not covered (no courses found):[/bold underline]")
        for cat in sorted(uncovered_categories):
            summary_lines.append(f"  [red]✗[/red] {cat}")

    console.print(Panel(
        "\n".join(summary_lines),
        title="[bold]📋 GE Requirement Summary[/bold]",
        border_style="green" if not uncovered_categories else "yellow",
    ))

    # ── Double-dip highlight ───────────────────────────────────────
    double_dip = [c for c in selected_courses if len(c.get("ge_categories", [])) > 1]
    if double_dip:
        console.print()
        console.print(Panel(
            "\n".join(
                f"  [bright_yellow]★[/bright_yellow] [cyan]{c['course_code']}[/cyan] — {c['course_name']} "
                f"([bright_yellow]{len(c['ge_categories'])} categories[/bright_yellow])"
                for c in double_dip
            ),
            title="[bold bright_yellow]⚡ Multi-Requirement Courses (Double-Dippers)[/bold bright_yellow]",
            border_style="bright_yellow",
        ))

    console.print()
