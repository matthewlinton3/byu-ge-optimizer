#!/usr/bin/env python3
"""
BYU GE Optimizer
Find the fewest courses that fulfill all GE requirements, cross-referenced with RMP ratings.

Usage:
    python main.py                  # Run with cached data
    python main.py --refresh        # Re-scrape BYU catalog and RMP
    python main.py --greedy         # Use greedy algorithm instead of ILP
    python main.py --no-rmp         # Skip RateMyProfessors lookup
"""

import argparse
import sys
from scraper import scrape_catalog_for_ge
from optimizer import optimize
from rmp import enrich_with_rmp
from display import print_results, console


def main():
    parser = argparse.ArgumentParser(
        description="BYU GE Optimizer — find the fewest courses to fulfill all GE requirements"
    )
    parser.add_argument("--refresh", action="store_true", help="Re-scrape BYU catalog and RMP data")
    parser.add_argument("--greedy", action="store_true", help="Use greedy algorithm instead of ILP")
    parser.add_argument("--no-rmp", action="store_true", help="Skip RateMyProfessors lookup")
    args = parser.parse_args()

    use_ilp = not args.greedy
    skip_rmp = args.no_rmp
    refresh = args.refresh

    console.print("\n[bold bright_blue]🎓 BYU GE Optimizer[/bold bright_blue] — starting up...\n")

    # Step 1: Scrape / load courses
    courses = scrape_catalog_for_ge(refresh=refresh)
    console.print(f"[green]✓[/green] Loaded [bold]{len(courses)}[/bold] GE courses\n")

    # Step 2: Optimize
    selected, uncovered = optimize(courses, use_ilp=use_ilp)
    console.print(f"[green]✓[/green] Optimizer selected [bold]{len(selected)}[/bold] courses\n")

    # Step 3: RMP enrichment
    if not skip_rmp:
        selected = enrich_with_rmp(selected, refresh=refresh)
        console.print(f"[green]✓[/green] RMP ratings fetched\n")
    else:
        for c in selected:
            c["professors"] = []
            c["rmp_rating"] = 0

    # Step 4: Display
    print_results(selected, uncovered)


if __name__ == "__main__":
    main()
