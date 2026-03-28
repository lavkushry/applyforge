import argparse
import json
import shutil
from pathlib import Path

from app.services.files import render_resume_pdf
from app.services.resume_templates import list_resume_templates, render_resume_template
from app.services.resume_themes import DEFAULT_RESUME_THEMES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="applyforge-resume", description="Resume template and export utilities for ApplyForge.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-templates", help="List packaged resume templates.")
    subparsers.add_parser("list-themes", help="List built-in resume themes.")

    render_parser = subparsers.add_parser("render-template", help="Render a packaged resume template from JSON content.")
    render_parser.add_argument("--input", required=True, help="Path to a canonical resume JSON payload.")
    render_parser.add_argument("--template-key", default="ats-markdown-starter", help="Template key to render.")
    render_parser.add_argument("--output", help="Optional path to write the rendered template output.")

    export_parser = subparsers.add_parser("export-pdf", help="Export a resume JSON payload to PDF using the current PDF pipeline.")
    export_parser.add_argument("--input", required=True, help="Path to a canonical resume JSON payload.")
    export_parser.add_argument("--theme-slug", default="classic-ats-light", help="Theme slug for accent metadata.")
    export_parser.add_argument("--output", help="Optional destination path for the PDF.")
    return parser


def _load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_or_print(content: str, output_path: str | None) -> None:
    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
        print(output_path)
        return
    print(content)


def _theme_by_slug(slug: str) -> dict:
    for theme in DEFAULT_RESUME_THEMES:
        if theme["slug"] == slug:
            return dict(theme)
    raise ValueError(f"Unknown theme slug: {slug}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list-templates":
        for template in list_resume_templates():
            print(f"{template['key']}\t{template['format']}\t{template['label']}")
        return 0

    if args.command == "list-themes":
        for theme in DEFAULT_RESUME_THEMES:
            print(f"{theme['slug']}\t{theme['label']}")
        return 0

    if args.command == "render-template":
        rendered = render_resume_template(_load_json(args.input), args.template_key)
        _write_or_print(rendered, args.output)
        return 0

    if args.command == "export-pdf":
        rendered_path = Path(render_resume_pdf(_load_json(args.input), _theme_by_slug(args.theme_slug)))
        if args.output:
            target = Path(args.output)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(rendered_path, target)
            print(str(target))
            return 0
        print(str(rendered_path))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
