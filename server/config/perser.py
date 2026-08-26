from langchain_core.documents import Document
import pymupdf4llm

def load_with_pymupdf4llm(file_path: str) -> list[Document]:
    md_text = pymupdf4llm.to_markdown(file_path)
    return [Document(page_content=md_text, metadata={"source": file_path})]