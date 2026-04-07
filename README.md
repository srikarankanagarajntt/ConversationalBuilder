# Conversational CV Builder Backend Skeleton (NTT Schema)

Run locally:

```bash
python -m venv .venv
.venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Environment setup:

```bash
# Edit .env in project root and set your real key
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4.1
OPENAI_AUDIO_MODEL=whisper-1
OPENAI_TIMEOUT_SECONDS=8
OPENAI_MAX_RETRIES=0

# TLS settings for enterprise/proxy certificates:
# Keep OPENAI_SSL_VERIFY=true in production
OPENAI_SSL_VERIFY=true
# Optional: path to your org CA bundle file if SSL verification fails
OPENAI_CA_BUNDLE_PATH=C:\\path\\to\\company-ca.pem
```

Swagger:
- http://127.0.0.1:8000/docs
