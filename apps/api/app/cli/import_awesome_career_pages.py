from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import urlopen

from app.db.session import SessionLocal
from app.models.entities import User
from app.services.company_seed import (
    AWESOME_CAREER_PAGES_PAGE_URL,
    parse_awesome_career_pages_markdown,
    upsert_company_seeds,
)

AWESOME_CAREER_PAGES_RAW_URL = "https://raw.githubusercontent.com/CSwala/awesome-career-pages/main/README.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import company directory records from the Awesome Career Pages README.",
    )
    parser.add_argument("--user-email", default="defaultuser@applyforge.dev", help="User email to seed companies for.")
    parser.add_argument(
        "--markdown-path",
        help="Optional local path to a downloaded README.md snapshot. If omitted, the raw GitHub URL is fetched.",
    )
    parser.add_argument(
        "--source-url",
        default=AWESOME_CAREER_PAGES_RAW_URL,
        help="Raw markdown URL to fetch when --markdown-path is not provided.",
    )
    parser.add_argument(
        "--source-page-url",
        default=AWESOME_CAREER_PAGES_PAGE_URL,
        help="Human-facing source URL written into company notes.",
    )
    return parser


def _load_markdown(markdown_path: str | None, source_url: str) -> str:
    if markdown_path:
        return Path(markdown_path).read_text(encoding="utf-8")
    with urlopen(source_url, timeout=30) as response:
        return response.read().decode("utf-8")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == args.user_email).first()
        if user is None:
            raise SystemExit(f"User not found: {args.user_email}")

        markdown = _load_markdown(args.markdown_path, args.source_url)
        seeds = parse_awesome_career_pages_markdown(markdown, source_page_url=args.source_page_url)
        result = upsert_company_seeds(db, user_id=user.id, seeds=seeds)
        print(
            json.dumps(
                {
                    "user_email": args.user_email,
                    "source_page_url": args.source_page_url,
                    "requested_count": result.requested_count,
                    "created_count": result.created_count,
                    "updated_count": result.updated_count,
                    "unchanged_count": result.unchanged_count,
                }
            )
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
