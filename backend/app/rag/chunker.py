import re

class TextChunker:
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted document text."""
        if not text:
            return ""
        # Remove null characters & normalize whitespace
        text = text.replace("\x00", " ")
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    @staticmethod
    def chunk_pages(extracted_pages: list, chunk_size: int = 500, chunk_overlap: int = 100) -> list:
        """
        Splits extracted pages into overlapping chunks.
        Returns a list of dicts:
        [{
            "chunk_index": idx,
            "chunk_text": text,
            "page_number": page,
            "char_count": len(text)
        }]
        """
        chunks = []
        chunk_index = 0

        for item in extracted_pages:
            page_num = item.get("page", 1)
            raw_text = item.get("text", "")
            cleaned = TextChunker.clean_text(raw_text)

            if not cleaned:
                continue

            # Split text by paragraphs or sentences first
            paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]

            current_chunk = ""
            for para in paragraphs:
                if len(current_chunk) + len(para) + 2 <= chunk_size:
                    current_chunk = f"{current_chunk}\n\n{para}".strip()
                else:
                    if current_chunk:
                        chunks.append({
                            "chunk_index": chunk_index,
                            "chunk_text": current_chunk,
                            "page_number": page_num,
                            "char_count": len(current_chunk)
                        })
                        chunk_index += 1
                    
                    # If paragraph itself is larger than chunk size, slide window
                    if len(para) > chunk_size:
                        start = 0
                        while start < len(para):
                            sub = para[start:start + chunk_size].strip()
                            if sub:
                                chunks.append({
                                    "chunk_index": chunk_index,
                                    "chunk_text": sub,
                                    "page_number": page_num,
                                    "char_count": len(sub)
                                })
                                chunk_index += 1
                            start += chunk_size - chunk_overlap
                        current_chunk = ""
                    else:
                        current_chunk = para

            if current_chunk:
                chunks.append({
                    "chunk_index": chunk_index,
                    "chunk_text": current_chunk,
                    "page_number": page_num,
                    "char_count": len(current_chunk)
                })
                chunk_index += 1

        return chunks
