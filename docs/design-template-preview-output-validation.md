# Design: Template Suggestion & Preview, Output Generation, Validation and Review

North-star experience
- Two-minute-to-wow: users see a branded preview with their own details in under 2 minutes.
- No dead-ends: clear actions to fix missing data and finalize.
- Quality by default: brand-compliant templates, accessible UI, and high-fidelity exports.

Practical implementation approach (step-by-step)

Phase 1 — Template gallery and live preview
- Template registry: Define a small catalog of branded templates with metadata (id, name, tags, locale, thumbnail, master binding if any).
- Gallery UX: Show 3–6 options; rank by role/seniority; ensure keyboard navigation and alt text.
- Live preview: Render HTML using the canonical schema; cache renders keyed by (template_id, schema_hash); add print CSS for fidelity.
- Click-to-edit: Annotate preview hotspots to trigger focused prompts for the underlying schema path (e.g., header.job_title).

Phase 2 — Validation gating
- Blocking rules: Enforce presence of name, job title, contact email, at least one summary bullet, one primary skill, one experience, and declaration place.
- Contextual rules: Add role-specific checks (e.g., project_title, client for consulting profiles).
- UX: Show a checklist with status; disable “Finalize” until blocking issues pass; deep-link fixes to chat.

Phase 3 — Master-driven exports (DOCX, PDF, PPTX, JSON)
- DOCX (master: “NTT_DATA_Resume_Templates.docx”)
  - Prepare the master with named content controls/bookmarks (e.g., header.full_name, header.job_title).
  - Repeating regions: Use repeating content controls for lists (professional_summary, technical_skills.primary/secondary, work_experience.responsibilities).
  - Mapping: Bind canonical schema → content controls; sanitize text; preserve brand styles (headings, bullets, spacing, logo margins).
  - Pagination: Guardrails for widows/orphans; auto-fit bullets; don’t overflow brand-safe areas.
- PDF
  - Strategy A: Print-to-PDF from the HTML preview with print CSS for pixel accuracy and selectable text.
  - Strategy B: Export-to-PDF from the populated DOCX master when HTML print isn’t acceptable for brand/legal contexts.
  - Ensure embedded fonts, correct margins, page numbers, and section breaks.
- PPTX (master: “Resume - Java Lead Architect.pptx”)
  - Use the master’s slide layouts; map schema to slides:
    - Cover: full_name, job_title, (optional) location/portal_id/headline.
    - Summary: professional_summary bullets (auto-fit; 5–7 lines guardrail).
    - Skills: primary/secondary split across columns; wrap and truncate gracefully.
    - Experience: duplicate an “Experience” layout slide per role; fill position, employer, employment_period.display_text, responsibilities; add technology as tags or a sub-bullet line.
    - Closing: optional declaration or branding slide per master.
  - Respect text boxes and safe areas; auto-duplicate slides on overflow rather than shrinking fonts.
- JSON
  - Return the canonical schema snapshot used for rendering; include meta (template_version, language, last_updated).

Phase 4 — Storage, delivery, and observability
- Storage layout: /exports/{session_id}/{template_id}/{schema_hash}.{pdf|docx|pptx|json}.
- Delivery: Return time-limited links, checksum, size, created_at; keep server-side copies for review history.
- Telemetry: Log template impressions, preview render time, export time, validation failures; build a simple CTR and completion dashboard.

Phase 5 — Review workflow (optional for MVP)
- Queue: Submissions enter a review queue with role/locale metadata.
- Anchored comments: Reviewers comment on schema paths (e.g., work_experience[0].responsibilities[2]).
- Approvals: On approval, freeze template_version and schema; keep versioned export artifacts.

Data mapping guide (essentials)
- Header: full_name → Title field, job_title → Subtitle, headline → short subline, portal_id → reference line, location.city/country → contact block.
- Contact: email_id|official_email_id → email placeholder; phone_number → phone; others optional.
- Professional summary: map bullets 1:1; trim overly long items to maintain brand spacing.
- Technical skills: primary and secondary as pill-style bullets or lists; cap count for aesthetic balance.
- Work experience items:
  - position, employer, client, employment_period.display_text.
  - responsibilities as bullets; project_title and project_description under a “Project” subheading.
  - technology as comma-separated tags or bullets depending on the master.
- Declaration: statement, place, signature_name.

Quality gates and QA checklist
- Visual fidelity: Compare exports to the masters for typography, spacing, logo usage, and color tokens.
- Accessibility: Semantic headings in HTML preview; alt text for logos; sufficient contrast.
- Content integrity: No missing placeholders/brackets; empty optional sections are omitted gracefully.
- Internationalization: Headings localized; date formats and phone normalization per locale.
- Performance: Preview within 1s on cached runs; exports under a few seconds for typical resumes.

Performance and caching
- Cache compiled templates and recent previews by (template_id, schema_hash).
- Debounce export actions; avoid re-rendering if schema unchanged; serve from storage when checksums match.

Security and compliance
- Sanitize inputs; no active scripts/styles in templates beyond brand tokens.
- Protect PII in logs; encrypt-at-rest exports; short-lived signed links.

Sprint plan (competition-ready)
- Week 1: Gallery, live preview, validation gating baseline, schema-to-HTML mapping, print CSS.
- Week 2: DOCX population from the master, PDF from HTML or DOCX, PPTX population from the master; storage and links.
- Week 3: Polish (a11y, telemetry, localization for headings), reviewer queue MVP, click-to-edit hotspots, ATS-friendly switch.

Demo script tips to win
- Start with no template → show gallery → select → live preview.
- Intentionally leave a required field empty → show gating and “Fix now” flow.
- One-click export to PDF/DOCX/PPTX → show pixel-perfect brand fidelity and selectable text in PDF.
- Optional: Reviewer adds a comment → author updates → re-export and approve.

1) Template suggestion and preview

1.1 UX flow
- Entry point
  - If no template is chosen, surface a "Template Gallery" panel with 3–6 NTT DATA-branded options.
  - Show small, fast-loading thumbnail previews and a short description (e.g., "Modern two-column, great for developers").
- Smart ranking
  - Rank suggestions using role, seniority, business unit, and content density from captured schema.
  - Cold-start defaults: "Modern Professional", "Executive", "Single-Column ATS-friendly".
  - Allow filters: "One-page", "With sidebar", "Minimal", "Graphic accents".
- Live preview
  - On hover/click, render a live HTML preview bound to the current schema data.
  - Display a skeleton shimmer while rendering.
  - Side-by-side layout on desktop: Conversation/chat on the left, Live Preview on the right.
- Interact to edit
  - Click-to-edit hotspots in the preview that jump the chat to that section (e.g., click job title → prompt to edit header.job_title).
  - Missing fields are highlighted in preview with subtle callouts and "Fix now" deep-links.
- Accessibility
  - Keyboard-accessible gallery cards, visible focus rings.
  - Alt text on logo, semantic headings in templates.
  - High-contrast mode toggle for preview.

1.2 Template model (registry)
- Fields
  - id, display_name, version, description, tags: [“2-column”, “ats-friendly”, “executive”]
  - locales: [“en”, “es”, …], brand_tokens (CSS variables), logo_path
  - schema_compat: min/max schema versions or features
  - preview_thumbnail (base64 or URL), preview_html_file, export_profiles (pdf, docx)
- Governance
  - Brand checks: enforce logo usage and spacing; color palette constraints via CSS tokens.
  - Versioning: keep older template versions available for resume updates.

1.3 Rendering for preview
- Mustache-like placeholders mapped to the canonical CV schema keys.
- Sections support lists and conditionals, with safe HTML escaping.
- Fonts and assets locally hosted or data-URI embedded for offline/secure envs.
- Cache compiled templates + "last N rendered" previews keyed by (template_id, schema_hash).

2) Output generation

2.1 Targets (master-compliant)
- HTML (preview): faithful to the selected template with print CSS.
- PDF (export): print-ready with branded margins and footers; may be derived from HTML print-to-PDF or from the DOCX master.
- DOCX (export): strictly based on the master file “NTT_DATA_Resume_Templates.docx” (styles, sections, logo spacing).
- PPTX (export): based on the master deck “Resume - Java Lead Architect.pptx” (slide masters, layouts, brand tokens).
- JSON: the canonical schema as-is for integration.

2.2 Pipeline (with masters)
- Input: (template_id, cv_schema, locale).
- Preflight: validate required fields; if failing, return actionable report (see section 3).
- Render HTML (for preview and optional PDF path)
  - Attach print styles; embed brand logo; resolve locale strings; ensure semantic headings.
- Generate PDF (two strategies)
  - Strategy A (preferred for pixel fidelity): Headless Chromium/Playwright print-to-PDF from the HTML preview (print CSS).
  - Strategy B (DOCX-led): Populate “NTT_DATA_Resume_Templates.docx”, then export/save-as PDF via a DOCX-to-PDF engine.
  - Ensure selectable text, embedded fonts, correct pagination and widows/orphans rules.
- Generate DOCX (master-bound)
  - Use “NTT_DATA_Resume_Templates.docx” as the master; fill via content controls/bookmarks or XML mapping from schema.
  - Preserve brand styles: headings, lists, spacing, colors, and logo placement.
  - Auto-fit bullets, avoid orphan headings; enforce one/two-column layout per master.
- Generate PPTX (master-bound)
  - Use “Resume - Java Lead Architect.pptx” slide masters/layouts.
  - Map schema to slides:
    - Cover: full_name, job_title, location (if available).
    - Summary: professional_summary bullets (auto-fit with 5–7-line guardrail).
    - Skills: split primary/secondary across columns; auto-wrap tags.
    - Experience: 1–3 slides with position, employer, dates (employment_period.display_text), responsibilities/achievements.
    - Declaration/metadata (optional): light footer or final slide as per master.
  - Respect auto-fit and safe text areas; truncate or overflow to additional slides as needed.
- Store and link
  - Object storage (versioned) with keys:
    - /exports/{session_id}/{template_id}/{hash}.pdf
    - /exports/{session_id}/{template_id}/{hash}.docx
    - /exports/{session_id}/{template_id}/{hash}.pptx
    - /exports/{session_id}/{template_id}/{hash}.json
  - Return signed or time-limited URLs to the client; include checksum and size.

2.3 Print and ATS considerations
- Print CSS: hide navigation, ensure 1-inch margins, avoid color-heavy backgrounds on print.
- ATS-friendly option: minimal styling, pure text, clear headings, single column; suppress decorative icons.
- PPT safety: keep within safe text boxes; avoid small fonts; ensure sufficient contrast for projection and print.

3) Validation and review

3.1 Validation model
- Base required (hard requirements):
  - header.full_name, header.job_title, header.contact.email_id|official_email_id
  - professional_summary (>=1 item)
  - technical_skills.primary (>=1 skill)
  - work_experience (>=1 item)
  - declaration.place
- Contextual required (role-specific):
  - e.g., for Consulting roles, “project_title” and “client” must be set for each experience.
  - For leadership, at least one achievement or impact metric.
- Format rules
  - Email format, phone normalized per locale, dates consistent, no future end-dates.
- Readability hints (non-blocking)
  - Summary length within target range; responsibilities as bullets; consistent verb tense.

3.2 Validation UX
- Real-time validation meter with sections checklist (complete/needs attention/blocking).
- Inline callouts in preview with “Fix now” actions to open targeted chat prompts.
- The “Finalize” CTA stays disabled until all hard requirements pass; tooltip shows unmet items.

3.3 Human-in-the-loop review
- Reviewer role and queue
  - Submissions land in a review queue with metadata (role, BU, language).
  - Reviewers can claim, comment, request changes, or approve.
- Review workspace
  - Side-by-side: preview on left, structured checklist on right (branding, completeness, clarity, PII).
  - Comment threads anchored to schema paths (e.g., work_experience[1].responsibilities[2]).
- Approvals and versioning
  - On approve, freeze template_id and schema snapshot; watermark internal/external if needed.
  - Maintain history with diffs between versions.
- Notifications and SLAs
  - Email/Teams/Slack notifications for submitter and reviewer; breach alerts if SLA missed.

4) Multilingual and accessibility

- i18n
  - Localize static section headings and boilerplate; dates formatted per locale.
  - RTL support for languages like Arabic/Hebrew (dir="rtl", logical properties).
  - Font fallback stacks for non-Latin scripts.
- A11y
  - Semantic headings in templates, alt text for logos.
  - Keyboard-friendly focus order; ARIA roles for gallery and dialog controls.
  - Color contrast >= 4.5:1; motion reduced for users preferring reduced animation.

5) Telemetry and ranking

- Events
  - Template impressions, clicks, previews, selection, exports, abandon points, validation failures.
- Metrics
  - CTR per template, time-to-preview, time-to-finalize, defect rate by reviewer, export success rate.
- Suggestion learning loop
  - Re-rank templates by role/locale using aggregated metrics.
  - Controlled A/B tests (e.g., show different top-3) with guardrails.

6) Architecture sketch

- Services (can be logical modules initially)
  - Template Registry: CRUD, metadata, thumbnails, brand checks.
  - Preview Service: binds schema → HTML with caching; returns base64 or URL.
  - Export Service: HTML → PDF/DOCX; manages storage and links.
  - Validation Service: runs rule engine returning blocking/warning results.
  - Review Service: queue, comments, approvals, versioning, notifications.
- Storage
  - Object store buckets for templates, thumbnails, and exports.
  - Key convention: predictable and cacheable, with content hashes.
- Security
  - AuthZ roles: author, reviewer, admin.
  - Sanitize template HTML; disallow remote scripts; content-security-policy for previews.
  - PII-aware logging; encrypted-at-rest storage for exports.

7) API sketch (contract-first)

- GET /api/template/options?locale=en&role=developer
  - Returns: [{ template_id, name, version, description, tags, thumbnail_b64 }]
- POST /api/template/preview
  - Body: { session_id, template_id }
  - Returns: { html_b64, warnings: [ ... ], missing: [ ... ] }
- POST /api/template/select
  - Body: { session_id, template_id } → pins active template_version in meta.
- GET /api/validation/report?session_id=...
  - Returns: { blocking: [...], warnings: [...], suggestions: [...] }
- POST /api/export/pdf|docx|pptx|json
  - Body: { session_id, template_id, locale }
  - Returns: { url, checksum, size, created_at }
- POST /api/review/submit
  - Body: { session_id, notes }
  - Returns: { review_id, status }
- POST /api/review/decision
  - Body: { review_id, decision: approve|changes_requested, comments }
  - Returns: { status, next_actions }

8) Demo-focused acceptance scenarios

- Suggestion & preview
  - Given no template, top-3 options appear with thumbnails; selecting one renders within 1s.
- Validation block
  - With missing email/summary, Finalize is disabled; callouts link to chat prompts; once fixed, Finalize enables.
- Export quality
  - PDF: print-accurate, selectable text, correct pagination, matches brand tokens; either from HTML print CSS or DOCX-to-PDF.
  - DOCX: structure and styles strictly conform to the master “NTT_DATA_Resume_Templates.docx” (headings, bullets, spacing, logo).
  - PPTX: slide layouts and styling conform to the master “Resume - Java Lead Architect.pptx”; auto-fit respected; no text overflow.
  - JSON: faithful serialization of the canonical schema.
- Review loop
  - Reviewer adds 2 comments and requests changes; author edits; reviewer approves; version frozen.

9) Milestones (competition-ready)

- Week 1
  - Template Gallery UI with ranking; basic preview endpoint; skeleton loading.
  - Validation report with blocking/warnings; CTA gating in UI.
- Week 2
  - PDF export (headless print) with print CSS; DOCX MVP (basic headings and lists).
  - Reviewer queue MVP with comment anchors and approve/changes states.
- Week 3 (polish)
  - A11y pass, localization for headings, telemetry dashboards for CTR and completion.
  - Thumbnails caching; “click-to-edit” hotspots in preview; ATS-friendly export toggle.

10) Differentiators to win
- Click-to-edit hotspots tied to conversational prompts (fast corrections).
- Data-driven template ranking with continuous learning.
- Instant live preview with brand tokens, print-accurate PDF, and ATS-friendly variant.
- Reviewer workspace with anchored comments and schema diffs.
