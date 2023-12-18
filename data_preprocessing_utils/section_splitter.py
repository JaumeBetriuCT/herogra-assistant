from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pdfminer.high_level import extract_text
from typing import List

import re

class SectionSplitter():

    def __init__(self, path_to_folder_origin: str, path_to_folder_out: str):
        
        self.path_to_folder_origin = path_to_folder_origin
        self.path_to_folder_out = path_to_folder_out

    def extract_sections(self, text: str) -> List:
        """
        Extracts the sections of the compacted document
        """
        pattern_section = r"SECCIÓN \d+:"
        matches = list(re.finditer(pattern_section, text))
        sections = []
        for i in range(len(matches)):
            start = matches[i].end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            sections.append(text[start:end].strip())
        return sections
    
    def create_pdf_by_section(self, sections: List, product_name: str) -> None:
        """
        Creates a pdf for each one of the sections passed as a list
        """
        for i, section in enumerate(sections, start=1):
            pdf_name = f"{self.path_to_folder_out}/{product_name} Seccion_{i}.pdf"
            c = canvas.Canvas(pdf_name, pagesize=letter)
            c.drawString(72, 720, f"SECCIÓN {i}")
            text = c.beginText(72, 700)
            text.textLines(section)
            c.drawText(text)
            c.save()
            print(f"Created PDF: {pdf_name}")
    
    def get_product_name(self, path_pdf: str) -> str:
        return path_pdf.replace(self.path_to_folder_origin, "").replace("(Español).pdf", "")
    
    def split_document(self, document_path: str) -> None:
        # Extract the pdf from the pdf
        pdf_text = extract_text(document_path)

        # Extract the name of the product from the path of the document
        product_name = self.get_product_name(document_path)

        # Extra the sections in a list
        sections = self.extract_sections(pdf_text)

        # Create the one document for each one of the sections
        self.create_pdf_by_section(sections, product_name)