from sqlalchemy.orm import Session

from app.models.entities import Company
from app.services.company_seed import (
    cleanup_imported_markdown_link_companies,
    parse_awesome_career_pages_markdown,
    parse_international_companies_markdown,
    upsert_company_seeds,
)


def test_parse_awesome_career_pages_markdown_extracts_links_and_dedupes_variants() -> None:
    markdown = """
###  [[24]7.ai](https://www.247.ai/career-search)
###  [3i Infotech](3i-infotech.com/careers/)
###  [Master Card](https://www.mastercard.us/en-us/vision/who-we-are/careers.html)
###  [Mastercard](https://www.mastercard.us/en-us/vision/who-we-are/careers.html)
###  [Cognizant](https://www.linkedin.com/company/cognizant/jobs/)
###  [Cognizant](https://careers.cognizant.com/in/en)
"""

    seeds = parse_awesome_career_pages_markdown(markdown, source_page_url="https://example.com/source")

    assert [seed.name for seed in seeds] == ["3i Infotech", "[24]7.ai", "Cognizant", "Master Card"]
    assert seeds[0].careers_url == "https://3i-infotech.com/careers/"
    assert seeds[1].careers_url == "https://www.247.ai/career-search"
    assert seeds[2].careers_url == "https://careers.cognizant.com/in/en"
    assert all(seed.notes == "Imported from Awesome Career Pages: https://example.com/source" for seed in seeds)


def test_upsert_company_seeds_fills_missing_fields_without_overwriting_existing_values(
    db_session: Session,
    user,
) -> None:
    existing = Company(
        user_id=user.id,
        name="Mastercard",
        normalized_name="mastercard",
        website_url="https://www.mastercard.com",
        careers_url="",
        linkedin_url="",
        hq_location="",
        industry="",
        notes="Priority target",
        active=False,
    )
    preserved = Company(
        user_id=user.id,
        name="Cognizant",
        normalized_name="cognizant",
        website_url="",
        careers_url="https://internal.example/careers",
        linkedin_url="",
        hq_location="",
        industry="",
        notes="",
        active=True,
    )
    db_session.add_all([existing, preserved])
    db_session.commit()

    seeds = parse_awesome_career_pages_markdown(
        """
###  [Master Card](https://www.mastercard.us/en-us/vision/who-we-are/careers.html)
###  [Cognizant](https://careers.cognizant.com/in/en)
###  [Airbnb](https://careers.airbnb.com/)
""",
        source_page_url="https://example.com/source",
    )

    result = upsert_company_seeds(db_session, user_id=user.id, seeds=seeds)

    mastercard = db_session.query(Company).filter(Company.normalized_name == "mastercard").first()
    cognizant = db_session.query(Company).filter(Company.normalized_name == "cognizant").first()
    airbnb = db_session.query(Company).filter(Company.normalized_name == "airbnb").first()

    assert result.requested_count == 3
    assert result.created_count == 1
    assert result.updated_count == 2
    assert result.unchanged_count == 0

    assert mastercard is not None
    assert mastercard.careers_url == "https://www.mastercard.us/en-us/vision/who-we-are/careers.html"
    assert mastercard.active is False
    assert mastercard.notes.endswith("https://example.com/source")

    assert cognizant is not None
    assert cognizant.careers_url == "https://internal.example/careers"
    assert cognizant.notes.endswith("https://example.com/source")

    assert airbnb is not None
    assert airbnb.careers_url == "https://careers.airbnb.com/"
    assert airbnb.active is True


def test_parse_international_companies_markdown_collects_locations_and_normalizes_entries() -> None:
    markdown = """
**London**
* [Google](https://careers.google.com/)
* [Booking.com](https://careers.booking.com/)

---

**Berlin, Germany**
* [Google, Munich](https://careers.google.com/)
* [Booking.com](https://careers.booking.com/)
* [OneFootball](https://jobs.lever.co/onefootball/?department=Engineering)

---

**Australia**
* Mentioned in the GitHub repo.
"""

    seeds = parse_international_companies_markdown(markdown, source_page_url="https://example.com/gist")

    assert [seed.name for seed in seeds] == ["Booking.com", "Google", "OneFootball"]
    assert seeds[0].careers_url == "https://careers.booking.com/"
    assert seeds[0].hq_location == ""
    assert "Berlin, Germany" in seeds[0].notes
    assert "London" in seeds[0].notes
    assert "Munich" not in seeds[1].name


def test_cleanup_imported_markdown_link_companies_removes_only_broken_source_rows(
    db_session: Session,
    user,
) -> None:
    broken = Company(
        user_id=user.id,
        name="[Google](https://careers.google.com/)",
        normalized_name="google https careers google com",
        careers_url="",
        notes="Imported from international companies hiring list: https://example.com/gist",
        active=True,
    )
    keep_company = Company(
        user_id=user.id,
        name="Google",
        normalized_name="google",
        careers_url="https://careers.google.com/",
        notes="Imported from international companies hiring list: https://example.com/gist",
        active=True,
    )
    other_source = Company(
        user_id=user.id,
        name="[24]7.ai",
        normalized_name="24 7 ai",
        careers_url="https://www.247.ai/career-search",
        notes="Imported from Awesome Career Pages: https://example.com/awesome",
        active=True,
    )
    db_session.add_all([broken, keep_company, other_source])
    db_session.commit()

    deleted_count = cleanup_imported_markdown_link_companies(
        db_session,
        user_id=user.id,
        source_page_url="https://example.com/gist",
    )
    db_session.commit()

    remaining_names = [company.name for company in db_session.query(Company).order_by(Company.id.asc()).all()]

    assert deleted_count == 1
    assert remaining_names == ["Google", "[24]7.ai"]
