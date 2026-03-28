from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import urlopen

from app.db.session import SessionLocal
from app.models.entities import User
from app.services.company_seed import (
    INTERNATIONAL_COMPANIES_GIST_PAGE_URL,
    cleanup_imported_markdown_link_companies,
    parse_international_companies_markdown,
    upsert_company_seeds,
)

INTERNATIONAL_COMPANIES_GIST_RAW_URL = (
    "https://gist.githubusercontent.com/idontknowjs/22f3257bed32dd3ab99ff22316e51eb8/raw"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import company directory records from the international companies hiring gist.",
    )
    parser.add_argument("--user-email", default="defaultuser@applyforge.dev", help="User email to seed companies for.")
    parser.add_argument(
        "--markdown-path",
        help="Optional local path to a downloaded markdown snapshot. If omitted, the raw gist URL is fetched.",
    )
    parser.add_argument(
        "--source-url",
        default=INTERNATIONAL_COMPANIES_GIST_RAW_URL,
        help="Raw markdown URL to fetch when --markdown-path is not provided.",
    )
    parser.add_argument(
        "--source-page-url",
        default=INTERNATIONAL_COMPANIES_GIST_PAGE_URL,
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
        seeds = parse_international_companies_markdown(markdown, source_page_url=args.source_page_url)
        deleted_count = cleanup_imported_markdown_link_companies(
            db,
            user_id=user.id,
            source_page_url=args.source_page_url,
        )
        result = upsert_company_seeds(db, user_id=user.id, seeds=seeds)
        print(
            json.dumps(
                {
                    "user_email": args.user_email,
                    "source_page_url": args.source_page_url,
                    "requested_count": result.requested_count,
                    "deleted_count": deleted_count,
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
