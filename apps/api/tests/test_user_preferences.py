from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.api.routes import profile as profile_routes
from app.models.entities import Setting, TargetRole
from app.services.user_preferences import build_user_preferences_snapshot, render_user_preferences_text


def test_build_user_preferences_snapshot_aggregates_profile_settings_and_roles(
    db_session: Session, user, profile
) -> None:
    db_session.add_all(
        [
            Setting(
                user_id=user.id,
                key="automation_preferences",
                value={"mode": "auto", "pause_on_risk": True},
            ),
            Setting(
                user_id=user.id,
                key="job_filters",
                value={"keyword_focus": ["python", "platform", "remote"]},
            ),
            Setting(
                user_id=user.id,
                key="resume_preferences",
                value={"default_theme": "compact-technical-light", "ats_mode": True},
            ),
            TargetRole(
                user_id=user.id,
                name="Senior Platform Engineer",
                aliases=["Platform Engineer"],
                keywords=["python", "kubernetes", "platform"],
                preferred_locations=["Remote"],
                remote_preference="remote",
                salary_target="$180k+",
                visa_preference="authorized",
                seniority="senior",
                companies_include=["OpenAI"],
                companies_exclude=["ExampleCorp"],
                scrape_cadence_minutes=15,
                automation_enabled=True,
                min_auto_apply_score=88.0,
                active=True,
            ),
        ]
    )
    db_session.commit()

    snapshot = build_user_preferences_snapshot(db_session, user.id)

    assert snapshot["candidate"]["full_name"] == "Alex Builder"
    assert snapshot["automation"]["mode"] == "auto"
    assert snapshot["job_filters"]["keyword_focus"] == ["python", "platform", "remote"]
    assert snapshot["resume"]["default_theme"] == "compact-technical-light"
    assert snapshot["target_roles"][0]["name"] == "Senior Platform Engineer"
    assert snapshot["company_preferences"]["include"] == ["OpenAI"]
    assert snapshot["company_preferences"]["exclude"] == ["ExampleCorp"]


def test_render_user_preferences_text_is_operator_readable(db_session: Session, user, profile) -> None:
    snapshot = build_user_preferences_snapshot(db_session, user.id)

    rendered = render_user_preferences_text(snapshot)

    assert "# ApplyForge User Preferences" in rendered
    assert "Candidate: Alex Builder" in rendered
    assert "Default apply mode" in rendered
    assert "Saved answers" in rendered


def test_export_user_preferences_supports_text_and_json(db_session: Session, user, profile) -> None:
    text_response = profile_routes.export_user_preferences("text", user, db_session)
    json_response = profile_routes.export_user_preferences("json", user, db_session)

    assert isinstance(text_response, PlainTextResponse)
    assert "ApplyForge User Preferences" in text_response.body.decode("utf-8")
    assert isinstance(json_response, JSONResponse)
    assert b'"candidate"' in json_response.body
