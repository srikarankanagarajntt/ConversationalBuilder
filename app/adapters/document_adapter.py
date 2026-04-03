class DocumentAdapter:
    def generate_document(self, schema: dict, template_id: str, format: str) -> bytes:
        text = f"Template: {template_id}\nFormat: {format}\nSchema: {schema}"
        return text.encode("utf-8")

_document_adapter = DocumentAdapter()

def get_document_adapter() -> DocumentAdapter:
    return _document_adapter
