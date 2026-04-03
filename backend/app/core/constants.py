"""Shared application constants."""

# CV section keys (used by PromptService and SchemaService)
CV_SECTIONS = [
    "personalInfo",
    "skills",
    "experience",
    "education",
    "projects",
    "certifications",
    "languages",
]

# Minimum fields required before export is allowed
REQUIRED_EXPORT_FIELDS = ["personalInfo.fullName", "experience", "skills"]

# Supported export formats
EXPORT_FORMATS = ["pdf", "docx", "json"]

# Supported upload MIME types
SUPPORTED_UPLOAD_MIMES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/msword",
]

# Session TTL (seconds) — used for future Redis expiry
SESSION_TTL_SECONDS = 3600
