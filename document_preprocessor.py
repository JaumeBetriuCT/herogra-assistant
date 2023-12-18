import os
from data_preprocessing_utils.document_summarizer import DocumentSummarizer
from data_preprocessing_utils.section_splitter import SectionSplitter

def main():
    # DOCUMENT SUMMARIZATION:
    document_summarizer = DocumentSummarizer()

    directory_original = "data/original_docs"
    directory_summarized = "data/data_summarized"
    directory_splitted = "data/data_by_sections"

    for _, original_file in enumerate(os.listdir(directory_original)):
        print(f'Summarizing file {original_file}')
        input_path = os.path.join(directory_original, original_file)
        output_path = os.path.join(directory_summarized, original_file)

        document_summarizer.transform_pdf(input_path, output_path)

    print("Documents summarized successfully")

    # SPLITTER DOCUMENTS:
    document_splitter = SectionSplitter(
        path_to_folder_origin = directory_summarized,
        path_to_folder_out = directory_splitted
    )

    for pdf_path in os.listdir(directory_summarized):
        print(f"Splitting file {pdf_path}")
        document_splitter.split_document(f"{directory_summarized}/{pdf_path}")

    print("Documents splitted successfully")

if __name__ == "__main__":
    main()