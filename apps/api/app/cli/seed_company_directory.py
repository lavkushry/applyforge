from __future__ import annotations

import argparse

from app.db.session import SessionLocal
from app.models.entities import Company, User
from app.services.company_directory import normalize_company_name

SOFTWARE_ENGINEERING_SOURCE = "https://builtin.com/articles/companies-hiring-software-engineers"
ENTRY_LEVEL_ENGINEERING_SOURCE = "https://builtin.com/articles/companies-hiring-engineers-entry-level"

SOFTWARE_ENGINEERING_COMPANIES = [
    ("DraftKings", "Boston, Massachusetts", "Sports Gambling"),
    ("Capital One", "McLean, Virginia", "Fintech"),
    ("SoFi", "San Francisco, California", "Fintech"),
    ("GRAIL", "Menlo Park, California", "Biotechnology"),
    ("Dropbox", "San Francisco, California", "Data Storage"),
    ("Achieve", "San Mateo, California", "Fintech"),
    ("Grubhub", "Chicago, Illinois", "Food, E-commerce"),
    ("Thrive Market", "Los Angeles, California", "Food, E-commerce"),
    ("AlertMedia", "Austin, Texas", "Threat Intelligence"),
    ("Chamberlain Group", "Oak Brook, Illinois", "IoT, Home Security"),
    ("CAIS", "New York, New York", "Fintech"),
    ("Square", "Atlanta, Georgia", "Payment Processing"),
    ("tastytrade/ tastylive/ tastyfx/ tastycrypto", "Chicago, Illinois", "Fintech"),
    ("bet365", "Denver, Colorado", "Sports Betting"),
    ("Kepler", "New York, New York", "Software, AI, Fintech"),
    ("Greenlight Guru", "Indianapolis, Indiana", "Healthtech"),
    ("Dscout", "Chicago, Illinois", "Professional Services"),
    ("GitLab", "San Francisco, California", "Software Development, Cybersecurity"),
    ("Air Space Intelligence", "Boston, Massachusetts", "Defense, Aerospace, Logistics"),
    ("Findhelp", "Austin, Texas", "Healthtech, Wellness"),
    ("ePayPolicy", "Austin, Texas", "Insurance"),
    ("Toast", "Boston, Massachusetts", "Fintech, Hospitality"),
    ("Airwallex", "Singapore", "Fintech"),
    ("Clearwater Analytics (CWAN)", "Chicago, Illinois", "Fintech"),
    ("Click Therapeutics", "New York, New York", "Healthtech"),
    ("Block", "Oakland, California", "Fintech"),
    ("Flourish", "New York, New York", "Fintech"),
    ("PagerDuty", "Atlanta, Georgia", "IT, Artificial Intelligence"),
    ("Rula", "Los Angeles, California", "Mental Healthcare"),
    ("Cash App", "Atlanta, Georgia", "Fintech"),
    ("NinjaTrader", "Chicago, Illinois", "Fintech"),
    ("Level Access", "Stafford, Virginia", "Software, IT"),
    ("McCain Foods", "New Brunswick, Canada", "Food and Beverage, Logistics"),
    ("Caliola Engineering", "Colorado Springs, Colorado", "Defense, Aerospace"),
    ("Perchwell", "New York, New York", "Real Estate Tech"),
    ("EZ Texting", "Santa Monica, California", "Marketing"),
    ("Sonar", "Geneva, Switzerland", "Artificial Intelligence, Software Development"),
    ("Forward Financing", "Boston, Massachusetts", "Fintech"),
    ("Carbon Robotics", "Seattle, Washington", "Robotics, Agriculture"),
    ("Oso", "New York, New York", "Security"),
    ("Jasper", "Austin, Texas", "Generative AI"),
    ("Clear Street", "New York, New York", "Fintech"),
    ("Attain", "Chicago, Illinois", "Advertising, Marketing"),
    ("Chime", "", ""),
    ("Narmi", "", ""),
    ("Zapier", "San Francisco, California", "Artificial Intelligence, Productivity"),
    ("Runpod", "San Francisco, California", "Cloud Infrastructure"),
    ("Gynger", "New York, New York", "Fintech"),
    ("Templafy", "Copenhagen, Denmark", "Business Operations"),
    ("Alloy", "New York, New York", "Fintech"),
    ("Dandy", "New York, New York", "Healthtech"),
    ("Clari", "Sunnyvale, California", "Fintech"),
    ("Spring Health", "New York, New York", "Mental Healthcare"),
    ("Superhuman", "San Francisco, California", "Generative AI"),
    ("Bilt", "New York, New York", "Fintech"),
    ("Cargill", "Wayzata, Minnesota", "Agriculture, Greentech"),
    ("Milestone Systems", "Lake Oswego, Oregon", "Video Technology Software"),
    ("FareHarbor", "Amsterdam, the Netherlands", "Software, Travel"),
    ("Rubrik", "Palo Alto, California", "Cybersecurity"),
    ("Axle Health", "Santa Monica, California", "Healthtech"),
    ("Formation Bio", "New York, New York", "Pharmaceutical"),
    ("8th Light", "Chicago, Illinois", "Design"),
    ("Golden Hippo", "Los Angeles, California", "Marketing"),
    ("Empower.me", "San Francisco, California", "Fintech"),
    ("Gusto", "Denver, Colorado", "HR Tech"),
    ("Striveworks", "Austin, Texas", "Artificial Intelligence"),
    ("CertifID", "Austin, Texas", "Cybersecurity"),
    ("Cockroach Labs", "New York, New York", "Data Management"),
    ("Datadog", "New York, New York", "Cybersecurity"),
    ("Atlassian", "San Francisco, California", "Business Productivity"),
    ("Hiro Systems", "New York, New York", "Blockchain, Cryptocurrency"),
    ("Boomi", "Conshohocken, Pennsylvania", "Automation, Artificial Intelligence, Data Management"),
    ("Edmunds", "Santa Monica, California", "Automotive, Advertising"),
    ("Coinbase", "Remote", "Cryptocurrency"),
    ("HERE Technologies", "Amsterdam, Netherlands", "Automotive, Artificial Intelligence"),
    ("Comcast", "New York, New York", "Entertainment"),
    ("FusionAuth", "Westminster, Colorado", "Cybersecurity"),
    ("Apex Fintech Solutions", "Dallas, Texas", "Fintech"),
    ("Hi Marley", "Boston, Massachusetts", "Insurtech, Conversational AI"),
    ("Spectrum", "Stamford, Connecticut", "Telecommunications"),
    ("DigitalOcean", "Broomfield, Colorado", "Artificial Intelligence, Cloud, Software"),
    ("Render", "San Francisco, California", "Cloud, Consumer Web"),
    ("Notion", "San Francisco, California", "Productivity"),
    ("FloQast", "Los Angeles, California", "Fintech"),
    ("Prolaio", "Chicago, Illinois", "Healthtech"),
    ("AirDNA", "Denver, Colorado", "Travel, Rental"),
    ("Klaviyo", "Boston, Massachusetts", "Marketing, Retail"),
    ("Vestmark, Inc.", "Wakefield, Massachusetts", "Fintech"),
]

ENTRY_LEVEL_ENGINEERING_COMPANIES = [
    "Affirm",
    "Grainger",
    "BAE Systems, Inc.",
    "Remitly",
    "UL Solutions",
    "General Motors",
    "Navan",
    "Vertafore",
    "IMC Trading",
    "Superblocks",
    "Sierra Space",
    "Northrop Grumman",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Seed sourced company directory entries for a user.")
    parser.add_argument("--user-email", default="defaultuser@applyforge.dev", help="User email to seed companies for.")
    return parser


def _upsert_company(
    *,
    user_id: int,
    name: str,
    hq_location: str,
    industry: str,
    notes: str,
) -> tuple[str, int]:
    db = SessionLocal()
    try:
        normalized_name = normalize_company_name(name)
        company = (
            db.query(Company)
            .filter(Company.user_id == user_id, Company.normalized_name == normalized_name)
            .first()
        )
        created = company is None
        if company is None:
            company = Company(
                user_id=user_id,
                name=name,
                normalized_name=normalized_name,
                website_url="",
                careers_url="",
                linkedin_url="",
                hq_location=hq_location,
                industry=industry,
                notes=notes,
                active=True,
            )
            db.add(company)
        else:
            company.name = name
            company.active = True
            if hq_location and not company.hq_location:
                company.hq_location = hq_location
            if industry and not company.industry:
                company.industry = industry
            if notes not in company.notes:
                company.notes = "\n\n".join(part for part in [company.notes.strip(), notes] if part).strip()
        db.commit()
        db.refresh(company)
        return ("created" if created else "updated", company.id)
    finally:
        db.close()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == args.user_email).first()
        if user is None:
            raise SystemExit(f"User not found: {args.user_email}")
        user_id = user.id
    finally:
        db.close()

    created_count = 0
    updated_count = 0

    software_note = (
        "Actively hiring for software engineering roles per Built In source: "
        f"{SOFTWARE_ENGINEERING_SOURCE}"
    )
    for name, hq_location, industry in SOFTWARE_ENGINEERING_COMPANIES:
        action, _company_id = _upsert_company(
            user_id=user_id,
            name=name,
            hq_location=hq_location,
            industry=industry,
            notes=software_note,
        )
        if action == "created":
            created_count += 1
        else:
            updated_count += 1

    entry_note = (
        "Actively hiring engineering talent per Built In source: "
        f"{ENTRY_LEVEL_ENGINEERING_SOURCE}"
    )
    for name in ENTRY_LEVEL_ENGINEERING_COMPANIES:
        action, _company_id = _upsert_company(
            user_id=user_id,
            name=name,
            hq_location="",
            industry="",
            notes=entry_note,
        )
        if action == "created":
            created_count += 1
        else:
            updated_count += 1

    print(
        {
            "user_email": args.user_email,
            "requested_company_count": len(SOFTWARE_ENGINEERING_COMPANIES) + len(ENTRY_LEVEL_ENGINEERING_COMPANIES),
            "created_count": created_count,
            "updated_count": updated_count,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
