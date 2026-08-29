import os
import pypdf
import docx

class DocumentExtractor:
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> list:
        """
        Extracts text from file.
        Returns a list of dicts: [{"page": page_num, "text": text_content}]
        """
        file_type = file_type.lower().strip(".")
        if file_type == "pdf":
            return DocumentExtractor._extract_pdf(file_path)
        elif file_type == "docx":
            return DocumentExtractor._extract_docx(file_path)
        elif file_type == "txt":
            return DocumentExtractor._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def _extract_pdf(file_path: str) -> list:
        pages_content = []
        try:
            reader = pypdf.PdfReader(file_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_content.append({"page": i + 1, "text": text.strip()})
        except Exception as e:
            raise RuntimeError(f"Error reading PDF {file_path}: {str(e)}")
        
        if not pages_content:
            pages_content.append({"page": 1, "text": "Empty document or non-extractable PDF."})
        return pages_content

    @staticmethod
    def _extract_docx(file_path: str) -> list:
        try:
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text.strip())
            text = "\n".join(full_text)
            return [{"page": 1, "text": text if text else "Empty DOCX document."}]
        except Exception as e:
            raise RuntimeError(f"Error reading DOCX {file_path}: {str(e)}")

    @staticmethod
    def _extract_txt(file_path: str) -> list:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read().strip()
            return [{"page": 1, "text": text if text else "Empty text document."}]
        except Exception as e:
            raise RuntimeError(f"Error reading TXT {file_path}: {str(e)}")
