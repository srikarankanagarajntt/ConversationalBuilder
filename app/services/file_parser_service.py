import re
from io import BytesIO
from fastapi import UploadFile
from PyPDF2 import PdfReader
from docx import Document
from app.models.responses import UploadCvResponse
from app.services.state_service import get_state_service
from app.services.cv_schema_service import get_cv_schema_service
from app.core.exceptions import AppException

class FileParserService:
    ALLOWED_EXTENSIONS = {".pdf", ".docx"}

    async def parse_cv_upload(self, session_id: str, upload: UploadFile) -> UploadCvResponse:
        """
        Parse uploaded CV file and extract information into canonical CV schema.

        Args:
            session_id: The session ID for the user
            upload: The uploaded file (PDF or DOCX only)

        Returns:
            UploadCvResponse with extracted data and missing fields

        Raises:
            AppException: If file format is invalid
        """
        # Validate file type
        self._validate_file_type(upload.filename or "")

        # Read file content
        content = await upload.read()

        # Extract text based on file type
        text_content = await self._extract_text(upload.filename or "", content)

        # Parse CV data from extracted text
        extracted_data = self._parse_cv_content(text_content)

        # Update session with extracted data
        state_service = get_state_service()
        session = state_service.get_session(session_id)
        session.cv_schema = get_cv_schema_service().merge_partial_update(session.cv_schema, extracted_data)
        state_service.update_session(session)

        # Find missing required fields
        missing_fields = get_cv_schema_service().find_missing_fields(session.cv_schema)

        return UploadCvResponse(session_id=session_id, extracted_data=extracted_data, missing_fields=missing_fields)

    def _validate_file_type(self, filename: str) -> None:
        """
        Validate that the uploaded file is PDF or DOCX.

        Args:
            filename: The name of the uploaded file

        Raises:
            AppException: If file type is not allowed
        """
        if not filename:
            raise AppException(
                code="INVALID_FILE",
                message="File name is required",
                status_code=400
            )

        file_ext = self._get_file_extension(filename).lower()

        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise AppException(
                code="INVALID_FILE_TYPE",
                message=f"Only PDF and DOCX files are allowed. Received: {file_ext}",
                status_code=400,
                details=[{"field": "file", "issue": f"Unsupported file type: {file_ext}"}]
            )

    async def _extract_text(self, filename: str, content: bytes) -> str:
        """
        Extract text from PDF or DOCX file.

        Args:
            filename: The name of the file
            content: The file content as bytes

        Returns:
            Extracted text content

        Raises:
            AppException: If file parsing fails
        """
        file_ext = self._get_file_extension(filename).lower()

        try:
            if file_ext == ".pdf":
                return self._extract_from_pdf(content)
            elif file_ext == ".docx":
                return self._extract_from_docx(content)
        except Exception as e:
            raise AppException(
                code="FILE_PARSE_ERROR",
                message=f"Failed to parse file: {str(e)}",
                status_code=400,
                details=[{"field": "file", "issue": f"Error parsing {file_ext} file"}]
            )

    def _extract_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF file."""
        pdf_reader = PdfReader(BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text

    def _extract_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX file."""
        doc = Document(BytesIO(content))
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
        return text

    def _parse_cv_content(self, text: str) -> dict:
        """
        Parse CV content and extract structured information.

        Args:
            text: The extracted text from the CV

        Returns:
            Dictionary with extracted CV data in canonical schema format
        """
        extracted = {}

        # Extract header information
        header = self._extract_header(text)
        if header:
            extracted["header"] = header

        # Extract professional summary
        summary = self._extract_professional_summary(text)
        if summary:
            extracted["professionalSummary"] = summary

        # Extract technical skills
        skills = self._extract_technical_skills(text)
        if skills:
            extracted["technicalSkills"] = skills

        # Extract work experience
        work_exp = self._extract_work_experience(text)
        if work_exp:
            extracted["workExperience"] = work_exp

        return extracted

    def _extract_header(self, text: str) -> dict | None:
        """Extract header information (name, job title, contact info)."""
        header = {}
        lines = text.split('\n')[:20]  # Look in first 20 lines

        # Try to extract full name (usually first meaningful line)
        for line in lines:
            line = line.strip()
            if line and len(line) > 0 and not any(x in line.lower() for x in ['email', 'phone', 'address']):
                # Simple heuristic: if it's not too long and looks like a name
                if 5 < len(line) < 100 and not line.isupper():
                    header["fullName"] = line
                    break

        # Extract email
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails = re.findall(email_pattern, text)
        if emails:
            header["email"] = emails[0]

        # Extract phone
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            header["phone"] = phones[0]

        # Try to extract job title (look for common patterns)
        job_patterns = [
            r'(?:Position|Title|Role|Current Role)[\s:]+([^\n]+)',
            r'(?:Designation|Designation)[\s:]+([^\n]+)',
        ]
        for pattern in job_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                header["jobTitle"] = match.group(1).strip()
                break

        return header if header else None

    def _extract_professional_summary(self, text: str) -> list[str] | None:
        """Extract professional summary."""
        summary_patterns = [
            r'(?:Professional Summary|Summary|Professional Profile|Profile)[\s:]+(.+?)(?=(?:Skills|Experience|Education|Technical|$))',
        ]

        for pattern in summary_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary_text = match.group(1).strip()
                # Split into sentences
                sentences = [s.strip() for s in re.split(r'[.\n]', summary_text) if s.strip()]
                if sentences:
                    return sentences

        return None

    def _extract_technical_skills(self, text: str) -> dict | None:
        """Extract technical skills."""
        skills = {"primary": [], "secondary": []}

        skills_patterns = [
            r'(?:Technical Skills|Skills|Expertise|Technology Stack)[\s:]+(.+?)(?=(?:Experience|Projects|Work|Education|$))',
            r'(?:Technologies|Tools|Languages)[\s:]+(.+?)(?=(?:Experience|Projects|Work|Education|$))',
        ]

        for pattern in skills_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                skills_text = match.group(1).strip()
                # Split by common delimiters
                skill_list = re.split(r'[,\n•-]', skills_text)
                for idx, skill in enumerate(skill_list):
                    skill = skill.strip()
                    if skill and len(skill) < 50:
                        skill_item = {
                            "skill_name": skill,
                            "category": "programming",
                            "proficiency": "intermediate"
                        }
                        if idx < len(skill_list) // 2:
                            skills["primary"].append(skill_item)
                        else:
                            skills["secondary"].append(skill_item)

        return skills if (skills["primary"] or skills["secondary"]) else None

    def _extract_work_experience(self, text: str) -> list[dict] | None:
        """Extract work experience."""
        work_exp = []

        # Pattern to find work experience sections
        exp_pattern = r'(?:Work Experience|Experience|Employment|Career History)([\s\S]*?)(?=(?:Education|Projects|Skills|Technical|References|$))'
        match = re.search(exp_pattern, text, re.IGNORECASE)

        if match:
            exp_section = match.group(1)
            # Split by common separators for multiple jobs
            job_blocks = re.split(r'\n(?=[A-Z][a-z]+\s+(?:at|from|,|\d)|\d{4})', exp_section)

            for block in job_blocks:
                if block.strip():
                    job_info = {}

                    # Extract employer/company
                    employer_pattern = r'(?:at|Company|Employer|Organization)[\s:]*([^\n]+)'
                    emp_match = re.search(employer_pattern, block, re.IGNORECASE)
                    if emp_match:
                        job_info["employer"] = emp_match.group(1).strip()

                    # Extract position
                    position_pattern = r'(?:as|position|role|designation)[\s:]*([^\n]+)'
                    pos_match = re.search(position_pattern, block, re.IGNORECASE)
                    if pos_match:
                        job_info["position"] = pos_match.group(1).strip()

                    # Extract project description
                    if block.strip():
                        job_info["project_description"] = block.strip()[:200]

                    if job_info:
                        work_exp.append(job_info)

        return work_exp if work_exp else None

    @staticmethod
    def _get_file_extension(filename: str) -> str:
        """Get file extension from filename."""
        if not filename or '.' not in filename:
            return ""
        return filename[filename.rfind('.'):]

_file_parser_service = FileParserService()

def get_file_parser_service() -> FileParserService:
    return _file_parser_service
