import json
import re
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta
import logging
import base64

from app.core.constants import SUPPORTED_TEMPLATES
from app.models.requests import SelectTemplateRequest, CreateSessionRequest
from app.models.responses import TemplateOptionsResponse, TemplateOption, TemplateSelectionResponse, SessionResponse
from app.models.cv_schema import CvSchema
from app.models.session import SessionContext
from app.services.state_service import get_state_service

logger = logging.getLogger(__name__)


class TemplateService:
    TEMPLATE_FILE_MAP = {
        "ntt_default": {
            "docx": "NTT_DATA_Resume_Templates.docx",
            "pptx": "Resume - Java Lead Architect.pptx",
        },
        "simple": {
            "docx": "NTT_DATA_Resume_Templates.docx",
        },
    }

    @staticmethod
    def _get_template_base64(file_name: str | None) -> str | None:
        if not file_name:
            return None
        file_path = Path(__file__).resolve().parents[2] / "template" / file_name
        if not file_path.exists():
            return None
        content = file_path.read_bytes()
        return base64.b64encode(content).decode("ascii")

    def get_template_options(self) -> TemplateOptionsResponse:
        """
        Discover HTML templates in /template, render them using mock cv_schema.json,
        and return options with base64-encoded rendered HTML.
        """
        root_dir = Path(__file__).resolve().parents[2]
        template_dir = root_dir / "template"
        mock_data_path = template_dir / "mock_data" / "cv_schema.json"

        # Load mock CV schema data
        try:
            with mock_data_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        except Exception:
            data = {}

        def resolve_path(ctx_stack: list, path: str):
            if path == ".":
                return ctx_stack[0]
            keys = path.split(".")
            for ctx in ctx_stack:
                val = ctx
                ok = True
                for k in keys:
                    if isinstance(val, dict) and k in val:
                        val = val[k]
                    else:
                        ok = False
                        break
                if ok:
                    return val
            return ""

        def render_template(tpl: str, context: dict) -> str:
            # Recursive render for sections and then variables
            def render_sections(s: str, stack: list) -> str:
                # Handle list/section tags: {{#path}} ... {{/path}}
                section_open_re = re.compile(r"{{\s*#\s*([.\w\-]+)\s*}}")
                while True:
                    m = section_open_re.search(s)
                    if not m:
                        break
                    name = m.group(1)
                    start_open = m.start()
                    end_open = m.end()
                    close_tag = f"{{{{/{name}}}}}"
                    end_close = s.find(close_tag, end_open)
                    if end_close == -1:
                        # No closing tag; break to avoid infinite loop
                        break
                    inner = s[end_open:end_close]
                    value = resolve_path(stack, name)
                    replacement = ""
                    if isinstance(value, list):
                        for item in value:
                            child_stack = [item] + stack
                            replacement += render_sections(inner, child_stack)
                    elif isinstance(value, dict):
                        child_stack = [value] + stack
                        replacement = render_sections(inner, child_stack)
                    elif value:
                        # Truthy scalar -> render inner once with same context
                        replacement = render_sections(inner, stack)
                    else:
                        replacement = ""
                    s = s[:start_open] + replacement + s[end_close + len(close_tag):]
                # Replace variables after sections are resolved
                var_re = re.compile(r"{{\s*([.\w\-]+)\s*}}")
                def repl_var(mv):
                    key = mv.group(1)
                    # Skip if it's an unprocessed section/closing (defensive)
                    if key.startswith("#") or key.startswith("/"):
                        return ""
                    val = resolve_path(stack, key)
                    if isinstance(val, (dict, list)):
                        return ""
                    return "" if val is None else str(val)
                return var_re.sub(repl_var, s)

            return render_sections(tpl, [context])

        options: list[TemplateOption] = []

        # Collect all HTML templates in /template
        html_files = sorted(template_dir.glob("*.html"))
        for html_file in html_files:
            try:
                template_str = html_file.read_text(encoding="utf-8")
            except Exception:
                template_str = ""

            rendered = render_template(template_str, data) if template_str else ""
            rendered_b64 = base64.b64encode(rendered.encode("utf-8")).decode("ascii") if rendered else None

            template_id = html_file.stem  # e.g., resume_template_1
            template_name = html_file.stem.replace("_", " ").title()
            description = f"Rendered HTML for {template_name}"

            options.append(
                TemplateOption(
                    template_id=template_id,
                    template_name=template_name,
                    description=description,
                    template_file_name=html_file.name,
                    template_base64=rendered_b64,
                )
            )

        return TemplateOptionsResponse(options=options)

    def select_template(self, request: SelectTemplateRequest) -> TemplateSelectionResponse:
        session = get_state_service().get_session(request.session_id)
        session.selected_template = request.template_id
        session.cv_schema.meta.template_version = request.template_id
        get_state_service().update_session(session)
        return TemplateSelectionResponse(
            session_id=request.session_id,
            template_id=request.template_id,
            template_name=request.template_id.title(),
            message="Template selected successfully.",
        )

    def get_export_manifest(self, session_id: str, include_content: bool = False):
        """
        Build an export manifest for the selected template (or a sensible default),
        including master DOCX/PPTX file names and which outputs are available.
        Optionally include base64-encoded master files.
        """
        session = get_state_service().get_session(session_id)
        # Prefer explicitly selected template; fallback to meta.template_version; then default
        template_id = getattr(session, "selected_template", None) or session.cv_schema.meta.template_version or "ntt_default"

        mapping = self.TEMPLATE_FILE_MAP.get(template_id) or self.TEMPLATE_FILE_MAP.get("ntt_default", {})
        docx_name: str | None = mapping.get("docx") if isinstance(mapping, dict) else None
        pptx_name: str | None = mapping.get("pptx") if isinstance(mapping, dict) else None

        root_dir = Path(__file__).resolve().parents[2]
        template_dir = root_dir / "template "

        def file_exists(name: str | None) -> bool:
            return bool(name) and (template_dir / name).exists()

        available_outputs: list[str] = ["json", "pdf"]
        if file_exists(docx_name):
            available_outputs.append("docx")
        if file_exists(pptx_name):
            available_outputs.append("pptx")

        docx_b64 = self._get_template_base64(docx_name) if include_content and docx_name else None
        pptx_b64 = self._get_template_base64(pptx_name) if include_content and pptx_name else None

        # Lazy import to avoid circulars on module import
        from app.models.export_manifest import ExportManifest, ExportAsset

        assets: list[ExportAsset] = []
        if docx_name:
            assets.append(ExportAsset(kind="docx", file_name=docx_name, base64=docx_b64))
        if pptx_name:
            assets.append(ExportAsset(kind="pptx", file_name=pptx_name, base64=pptx_b64))

        return ExportManifest(
            session_id=session_id,
            template_id=template_id,
            assets=assets,
            available_outputs=available_outputs,
        )

_template_service = TemplateService()

def get_template_service() -> TemplateService:
    return _template_service
