"""Xing Profile API: A Quick Start Example

See more at: https://apify.com/johnvc/xing-profile-api?fpr=9n7kx3
Input schema: https://apify.com/johnvc/xing-profile-api/input-schema?fpr=9n7kx3

This script shows how to call the Xing Profile API on Apify from Python and read
its structured JSON output. You bring the profile URLs (or bare handles); the
Actor returns one row per member with name, job title, city, country, skills,
languages, employment history, and education.

There is no discovery endpoint, so this API does not search for people. It reads
profiles you already have URLs or handles for.

Get your free Apify API key at: https://apify.com?fpr=9n7kx3

Examples:
  uv run python xing-profile-api-example.py
  uv run python xing-profile-api-example.py --example default
  uv run python xing-profile-api-example.py --example career
"""

from __future__ import annotations

import argparse
import os
from typing import Any

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

ACTOR_ID = "johnvc/xing-profile-api"


def _fetch(client: ApifyClient, run_input: dict[str, Any]) -> list[dict[str, Any]]:
    """Run the Actor and return every row from its default dataset.

    apify-client 3.x returns a typed Run object (not a dict), so the dataset is
    read from run.default_dataset_id.
    """
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    if run is None:
        raise SystemExit("The Actor run did not return a result.")
    return list(client.dataset(run.default_dataset_id).iterate_items())


def _split(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Separate profile rows from error rows.

    Every row carries a result_type of either "profile" or "error", so an input
    that could not be collected never disappears silently.
    """
    profiles = [row for row in items if row.get("result_type") == "profile"]
    errors = [row for row in items if row.get("result_type") == "error"]
    return profiles, errors


def _report_errors(errors: list[dict[str, Any]]) -> None:
    """Print any input that produced no profile."""
    for row in errors:
        print(f"  no result for {row.get('sourceUrl')}: {row.get('error_message')}")


def run_default(client: ApifyClient) -> None:
    """Cheap general quick-start: one profile, key fields printed."""
    # Billing is per profile returned, so this first run asks for a single
    # profile to keep it inexpensive. Add more URLs (up to 1000 per run) once
    # you have your own API key and know your budget.
    run_input: dict[str, Any] = {
        "profileUrls": [
            "https://www.xing.com/profile/Chuck_Coulson",
        ],
    }

    items = _fetch(client, run_input)
    profiles, errors = _split(items)
    print(f"Returned {len(profiles)} profile(s) and {len(errors)} error row(s).\n")

    for person in profiles:
        print(person.get("fullName", "(no name)"))
        print(f"  title:     {person.get('jobTitle', '')}")
        print(f"  location:  {person.get('city', '')} {person.get('countryCode', '')}".rstrip())
        print(f"  member:    {person.get('membership', '')}")
        # Skills come back as the member entered them, German and English mixed.
        print(f"  skills:    {', '.join(person.get('skills', [])) or '(none listed)'}")
        print(f"  languages: {', '.join(person.get('languages', [])) or '(none listed)'}")
        print(f"  profile:   {person.get('profileUrl', '')}")
        # Every profile row ships a one-line plain-language summary, handy when
        # an agent reads the record without post-processing it.
        print(f"  summary:   {person.get('summary', '')}\n")

    _report_errors(errors)


def run_career(client: ApifyClient) -> None:
    """Read employment history and education for a small batch.

    Shows both accepted input shapes: a full profile URL and a bare handle.
    """
    # Two inputs only. One profile-scraped event is charged per profile
    # returned, and inputs that return nothing are not charged.
    run_input: dict[str, Any] = {
        "profileUrls": [
            "https://www.xing.com/profile/Chuck_Coulson",
            "Andreas_Lappano",  # a bare handle works the same as a full URL
        ],
    }

    items = _fetch(client, run_input)
    profiles, errors = _split(items)
    print(f"Returned {len(profiles)} profile(s) and {len(errors)} error row(s).\n")

    for person in profiles:
        print(f"{person.get('fullName', '(no name)')} ({person.get('jobTitle', '')})")

        experience = person.get("experience", [])
        print(f"  experience ({len(experience)} entr(y/ies)):")
        for role in experience:
            title = role.get("title", "")
            dates = " to ".join(x for x in [role.get("startDate"), role.get("endDate")] if x)
            line = ", ".join(x for x in [role.get("company", ""), title, dates] if x)
            print(f"    - {line}")

        education = person.get("education", [])
        print(f"  education ({len(education)} entr(y/ies)):")
        for school in education:
            line = ", ".join(
                x for x in [school.get("institution", ""), school.get("qualification", "")] if x
            )
            print(f"    - {line}")

        # Fields a member did not publish are omitted from the row rather than
        # returned empty, so a sparse profile reads as sparse rather than broken.
        for optional in ("groups", "interests", "similarProfiles"):
            values = person.get(optional)
            if values:
                print(f"  {optional}: {len(values)} listed")
        print()

    _report_errors(errors)


def main() -> None:
    """Dispatch one of the example runs."""
    parser = argparse.ArgumentParser(description="Xing Profile API examples")
    parser.add_argument(
        "--example",
        default="default",
        choices=["default", "career"],
        help="Which example to run: 'default' prints key profile fields, 'career' prints role and education history.",
    )
    args = parser.parse_args()

    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        raise SystemExit("Set APIFY_API_TOKEN in .env or the environment.")

    client = ApifyClient(token)
    dispatch = {
        "default": run_default,
        "career": run_career,
    }
    dispatch[args.example](client)


if __name__ == "__main__":
    main()
