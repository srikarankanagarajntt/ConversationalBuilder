# Conversational NTT DATA CV Builder — Requirements

Goal
- Enable NTT DATA employees to create a professional CV by conversing with a chat bot (text) or a speech-enabled interface (voice).
- Capture, validate, and normalize information into a canonical CV schema.
- Generate a branded NTT DATA CV using the active template version; if no standard template is provided, the system proposes options, allows preview, and then produces the final CV.

Primary user journeys
1) Text chat flow (web, mobile, messaging platforms)
   - User starts a session and chats to provide CV details.
   - Assistant guides with prompts, validates entries, and confirms sections.
   - User previews the CV and downloads the final output.

2) Speech flow (web, mobile, IVR)
   - User speaks; system performs speech-to-text (S2T) transcription.
   - Assistant reads back confirmations, asks contextual follow-ups, and guides to complete required fields.
   - User previews and downloads the final output.

Key capabilities
- Conversational capture
  - Guided prompts, progressive disclosure, contextual follow-ups.
  - Inline validation (required fields, formats, completeness).
  - Edit/overwrite: user can revise previously entered sections.

- Speech-to-text (S2T)
  - Accept microphone audio.
  - Robust transcription (multilingual), timestamps when available.
  - Interruptions/restarts supported; user can switch between voice and text mid-session.

- Template suggestion engine
  - If no standard template is supplied, propose NTT DATA-branded options (with logo) and short descriptions.
  - Allow selection and live preview before finalization.

- Canonical schema mapping
  - Normalize all captured content into a single canonical CV schema (header, skills, summary, experience, declaration, etc.).
  - Maintain data provenance (chat or voice) within metadata.

- Output generation
  - HTML for preview.
  - PDF/DOCX for export (print-ready, brand-consistent).
  - JSON for downstream integrations.

- Validation and review
  - Hard-required fields must be present before finalization.
  - Preview and edit loop before export.
  - Optional human-in-the-loop review step to approve or request changes.

- Multilingual and accessibility
  - Support multiple languages for prompts and transcription.
  - WCAG-aligned UI elements, screen-reader-friendly labels, keyboard navigation.

- Session management
  - Create/reuse sessions with TTL, safe cleanup, and user context tracking.
  - Session resume and continuity (recent history and last edits preserved).

Non-functional requirements
- Security: authenticated access, protection of PII, secure storage of sessions and files.
- Compliance: enterprise logging and audit trails (PII-aware).
- Performance: quick prompt-response roundtrips, scalable S2T and generation pipeline.
- Reliability: graceful degradation when external AI/STT services are slow/unavailable.
- Observability: metrics and logs for sessions, latencies, and failures.

High-level flow
1) Start
   - User initiates a session (text or voice).
   - System greets and identifies missing required sections.

2) Capture and guide
   - For each section (header, summary, skills, experience, declaration), ask targeted prompts.
   - Validate and confirm entries; allow edits.

3) Template handling
   - If the user provides a template, validate and use it.
   - If not, suggest NTT DATA templates; on selection, render a preview.

4) Preview and finalize
   - Show a branded preview; user can continue editing until satisfied.
   - On finalize, generate outputs (PDF/DOCX/JSON) and provide download links.

5) Post-processing (optional)
   - Human reviewer can approve or request updates.
   - Archive or distribute the final CV as needed.

Acceptance criteria
- Sessions
  - Session can be created and reused within TTL.
  - Users can switch between text and voice without losing context.

- Data capture and schema
  - Required fields are enforced (e.g., name, job title, contact email, summary, primary skills, experience, declaration place).
  - All captured data maps into the canonical schema with no loss.

- S2T transcription
  - Accurate transcription for supported languages.
  - Handles pauses, restarts; user can confirm or correct transcriptions.

- Template suggestion and preview
  - System offers at least one NTT DATA-branded template when not supplied.
  - User can preview with their captured data before finalization.

- Output generation
  - Final CV can be generated in branded PDF/DOCX and a JSON representation.
  - HTML preview matches the selected template styling and placeholders.

- Validation and review
  - System blocks finalization until required fields are complete.
  - Human reviewer can approve or request changes (if enabled).

- Accessibility and multilingual
  - Key user flows accessible via keyboard and screen readers.
  - Prompts and messages localize based on selected language.

Future enhancements (optional)
- Rich media (profile photo, signatures) with secure storage.
- Import from existing Word/PDF to prefill fields using extraction.
- Role-based access control for reviewers vs. authors.
- Analytics dashboard for adoption and quality metrics.

Out of scope (initial phase)
- End-to-end DLP scanning and full retention policies (can be added later).
- Native mobile apps (initially responsive web-first; mobile clients can call APIs).
