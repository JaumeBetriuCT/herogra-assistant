from pdfminer.high_level import extract_text
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

import openai
import re
import streamlit as st

class DocumentSummarizer:

    def __init__(self):

        openai.api_key = st.secrets["OPENAI_API_KEY"]

    def extract_text_from_pdf(self, input_pdf_file: str) -> str:
        """
        Extract text from each page of the input PDF using PDFMiner.
        """
        return extract_text(input_pdf_file)

    def delete_page_breaks(self, input_string: str) -> str:
        """
        Deletes the page breaks of a string
        """
        return input_string.replace("\n", "")

    def process_pdf_text(self, input_string: str) -> str:
        """
        Process PDF text by deleting the header and adding page titles to sections.
        Return: List of tuples, where each tuple contains (section title, section text)
        """
        lines = input_string.split('\n\n')

        # Initialize variables to track page boundaries and page titles
        page_start = 0

        result_sections = []  # List to store section texts

        # Get the title from the 3rd line of the page 1
        title = lines[page_start + 1]
        title = title.strip()  # Update the current page title

        i = 0
        current_section_title = ""
        current_section_text = ""

        while i < len(lines):
            # Check if the line contains "Continúa en la página siguiente"
            if lines[i] == "-Continúa en la página siguiente.- ":
                # Skip this line as it's a page break indicator
                i += 1
                continue
            
            #Remove header 
            if 'FICHA DE DATOS DE SEGURIDAD' in lines[i]:
                # Skip this line as it's a page header indicator
                i += 6
                continue

            # Process and modify section titles
            if lines[i].startswith("SECCIÓN"):
                section_title = lines[i].strip()
                # Add the page title as a prefix to the section title
                modified_section_title = f"{section_title} DE {title}"
                
                # Store the previous section text if it's not empty
                if current_section_title and current_section_text:
                    result_sections.append((current_section_title, current_section_text))
                
                # Initialize the current section title and text with the modified title
                current_section_title = modified_section_title
                current_section_text = ""
            else:
                # Append the line to the current section text
                current_section_text += "\n\n" + lines[i]

            i += 1
            
        # Append the last section to the result list
        if current_section_title and current_section_text:
            result_sections.append((current_section_title, current_section_text))

        return result_sections

    def get_message_history(self) -> dict:
        """
        Returns the context for chatgpt depending for sumarization
        """

        message_history = [
            {
                "role": "user",
                "content": "Te voy a dar el texto contenido en una sección de una ficha tecnica de un producto quimico. Necesito que compactes el texto en un solo parrafo sin perder informacion." 
            },
            {
                "role": "assistant",
                "content": "Claro, estaré encantado de ayudarte a resumir el texto de la ficha técnica del producto químico. Por favor, proporciona el texto que deseas que resuma y lo compactaré en un solo párrafo sin perder información."
            }
        ]

        return message_history

    def chat_sections(self, sections):
        summarized_sections = []
        for section_title, section_text in sections:
            print(f"Summarizing {section_title}")
            
            # Set message history with the context and section text
            message_history = self.get_message_history()
            message_history.append({"role": "user", "content": section_text})
            
            print("Waiting for openAI...")
            # Use the large models for summarization:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=message_history
            )
            print("Done")
            
            reply_content = completion.choices[0].message.content
            
            # Append the original section title and summarized content to the list
            summarized_sections.append((section_title, reply_content))
        
        return summarized_sections

    def create_pdf_with_summarized_sections(self, sections, output_pdf_file):
        # Define the page size and margins
        page_width, page_height = letter
        left_margin = 0.75 * inch
        right_margin = 0.75 * inch
        top_margin = 0.75 * inch
        bottom_margin = 0.75 * inch

        # Create a PDF document with specified margins
        doc = SimpleDocTemplate(output_pdf_file, pagesize=(page_width, page_height),
                                leftMargin=left_margin, rightMargin=right_margin,
                                topMargin=top_margin, bottomMargin=bottom_margin)

        # Create a list of paragraphs to hold the text
        story = []

        # Define styles for paragraphs (you can customize as needed)
        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
        normal_style.leading = 12  # Line spacing

        for section_title, section_content in sections:
            # Add the section title as a heading
            section_title_paragraph = Paragraph(section_title, normal_style)
            story.append(section_title_paragraph)

            # Split the section content into paragraphs
            paragraphs = section_content.split("\n\n")

            for paragraph in paragraphs:
                # Clean up any extra spaces and line breaks
                paragraph = paragraph.strip()
                paragraph = re.sub(r'\s+', ' ', paragraph)

                # Create a Paragraph object and add it to the story
                story.append(Paragraph(paragraph, normal_style))

            # Add a spacer between sections
            story.append(Spacer(1, 0.2 * inch))

        # Build the PDF document
        doc.build(story)

    def transform_pdf(self, input_pdf_file, output_pdf_file):
        # Extract all the text:
        extracted_text = self.extract_text_from_pdf(input_pdf_file)

        #Process pdf text and split in sections
        extracted_text_per_section = self.process_pdf_text(extracted_text)

        # Set message history with the context:
        print(f"Summarizing {input_pdf_file}...")
        
        # Sumarize the text sections in one paragraph with chatgpt:
        summarized_sections  = self.chat_sections(extracted_text_per_section)

        # Create the pdf using the summarized sections text:
        self.create_pdf_with_summarized_sections(summarized_sections, output_pdf_file)