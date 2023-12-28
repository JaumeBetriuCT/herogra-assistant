# from langchain.embeddings import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from typing import List

import streamlit as st
import os
import re

class VectorDatabase:
    """Class to interact with the vectordatabase"""

    def __init__(self, data_path: str, action: str, chunk_size: int=400, chunk_overlap: int=100):

        self.data_path = data_path
        self.embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["OPENAI_API_KEY"])

        # os.environ["AZURE_OPENAI_API_KEY"] = st.secrets["AZURE_API_KEY_EMBEDDINGS"]
        # os.environ["AZURE_OPENAI_ENDPOINT"] = st.secrets["ENDPOINT_EMBEDDINGS"]
        # self.embeddings = AzureOpenAIEmbeddings(
        #     azure_deployment = "ada-embeddings",
        #     openai_api_version = "2023-05-15"
        # )

        if action == "store":
            print("Creating vectordatabase...")
            vectorstore_to_store = self.create_vector_database(chunk_size, chunk_overlap)
            
            # Store the database:
            vectorstore_to_store.save_local("faiss_db")
            print("Vectordatabase successfully created and stored")
        
        if action == "load":
            print("Loading database...")
            self.vectorstore = FAISS.load_local("faiss_db", self.embeddings)
            print("Database loaded")

    def create_vector_database(self, chunk_size: int, chunk_overlap: int) -> FAISS:
        """
        Creates the vectorstore database
        """

        documents = []
        for file in os.listdir(self.data_path):
            pdf_path = f"{self.data_path}/{file}"
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())
            print(f"{pdf_path} added to the vector database")

        text_splitter = CharacterTextSplitter(
            chunk_size = chunk_size, 
            chunk_overlap = chunk_overlap, 
            separator = " "
        )
        documents = text_splitter.split_documents(documents)

        return FAISS.from_documents(documents, self.embeddings)
    
    def clean_source(self, source: str) -> str:
        """
        Cleans the name of the source of chunk extracted from the vector database
        """

        # Patterns to be deleted:
        pattern_section = " Seccion_\d+\.pdf"
        # pattern_data_path = f"{self.data_path}/"
        pattern_data_path = "data/data_by_sections/"
        print(pattern_data_path)
        print(source)

        # Return the source without the section name and the data_path to keep only product name
        cleaned_source = re.sub(pattern_section, "", source).replace(pattern_data_path, "").replace(" - ", "")

        print(cleaned_source)

        return cleaned_source
    
    def filter_chunks(self, chunks: List, threshold: float) -> List:
        """
        Returns the chunks filtered using the threshold
        """
        output = []
        for chunk in chunks:
            if chunk["score"] >= threshold:
                output.append(chunk)

        return output
    
    def compact_output(self, chunks: List) -> List:
        """
        Compacts the info by products from the output of the funcion filter_chunks
        """
        output = []
        stored_products = []

        for chunk in chunks:
            # If we have no info from this product name:
            if chunk["product_name"] not in stored_products:
                output.append(
                    {
                        "product_name": chunk["product_name"],
                        "text": f"Información producto {chunk['product_name']}: {chunk['chunk']}"
                    }
                )

                # Add the product name to the list of stored_products:
                stored_products.append(chunk["product_name"])

            # If we have already created an entry for the product in the list output
            # just add the text to the already created entry:
            else:
                for chunk_output in output:
                    if chunk_output["product_name"] == chunk["product_name"]:
                        # Add the new information from the product:
                        chunk_output["text"] += f". {chunk['chunk']}"
        
        # Delete "\n" characters:
        for chunk_output in output:
            chunk_output["text"] = chunk_output["text"].replace("\n", " ")

        return output
    
    def structure_output(self, chunks: List) -> str:
        """
        Structures the output of the function compact_output in a string of text ready for the model
        """
        output_string = ""

        for chunk in chunks:
            output_string += f"{chunk['text']} \n"

        return output_string

    def run_query(self, query: str, k: int=15, threshold: float=0.1) -> str:
        """
        From the k chunks of text with highest similarity to the query
        """
        output = []
        
        # Return the k most similar chunks:
        k_similar_chunks = self.vectorstore.similarity_search_with_score(query, k)

        print("RAW DATABASE OUTPUT:")
        print(k_similar_chunks)

        # Iterate trough the similar chunks information and get the text, the source and the score:
        for chunk_info in k_similar_chunks:
            score = chunk_info[1]
            text = chunk_info[0].page_content
            source = chunk_info[0].metadata["source"]
            
            cleaned_source = self.clean_source(source)

            # Create the output that contains the score and the text of the chunk with the information
            # of what product it belongs to
            output.append(
                {
                    "product_name": cleaned_source,
                    "chunk": text,
                    "score": score
                }
            )

        # Filter the responses using the threshold:
        output = self.filter_chunks(output, threshold)

        # Compact the information from all the products:
        output = self.compact_output(output)

        # Structure the output in one string ready for the model:
        output = self.structure_output(output)

        return output

if __name__ == "__main__":
    
    vector_database = VectorDatabase(data_path="/home/leibniz/Desktop/herogra-assistant/data/data_by_sections")

    result = vector_database.run_query("Que productos estan clasificados como inflamables, explosivos o comburente?")