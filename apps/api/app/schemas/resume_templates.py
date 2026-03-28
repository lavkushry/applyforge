from pydantic import BaseModel


class ResumeTemplateSectionOut(BaseModel):
    key: str
    label: str
    description: str
    repeatable: bool
    required: bool
    placeholder: str


class ResumeTemplateOut(BaseModel):
    key: str
    label: str
    description: str
    format: str
    asset_name: str
    recommended_theme_slugs: list[str]
    section_keys: list[str]


class ResumeTemplateCatalogResponse(BaseModel):
    templates: list[ResumeTemplateOut]
    sections: list[ResumeTemplateSectionOut]


class ResumeTemplateRenderRequest(BaseModel):
    template_key: str = "ats-markdown-starter"
    content: dict | None = None


class ResumeTemplateRenderResponse(BaseModel):
    template: ResumeTemplateOut
    rendered_content: str
    sections: list[ResumeTemplateSectionOut]
