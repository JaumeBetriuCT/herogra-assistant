import semantic_kernel as sk
import streamlit as st

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from memory_chat_utils.prompts import QA_GENERATION_TEMPLATE_SK2
from memory_chat_utils.vector_database import VectorDatabase
from typing import Tuple

class SemanticQueryEngine:
    
    def __init__(self, data_path: str, model_name: str):
        
        # Create the vector database using the files in the data_path
        self.vector_database = VectorDatabase(data_path)
        # Define the kernel:
        self.kernel = sk.Kernel()

        # Define the LLM model you want to use:
        if model_name not in ["gpt-35-16k", "gpt-4-32k"]:
            raise ValueError(f"{model_name}  is an invalid model. Alowed model: ['gpt-35-16k', 'gpt-4-32k']")

        deployment_name = f"{model_name}-herogra"
        llm = AzureChatCompletion(
            deployment_name = deployment_name, 
            endpoint = st.secrets["ENDPOINT"], 
            api_key = st.secrets["AZURE_API_KEY"]
        )

        # Add the model, create context, initialize memory and create the semantic funcion:
        self.kernel.add_chat_service("qa", llm)
        self.context_qa = self.kernel.create_new_context()
        self.initialize_memory()
        self.qa = self.kernel.create_semantic_function(QA_GENERATION_TEMPLATE_SK2)

    def initialize_memory(self) -> None:
        """
        Initializes the memory of the assistant
        """
        self.context_qa["question1"] = ""
        self.context_qa["response1"] = ""
        self.context_qa["question2"] = ""
        self.context_qa["response2"] = ""

    def update_qa_memory(self, question: str, response: str) -> None:
        """
        Update the memory of the assistant so we always have two steps back of memory
        """
        # Move question2 to question1 and get rid of question1:
        self.context_qa["question1"] = self.context_qa["question2"]
        # Same with response:
        self.context_qa["response1"] = self.context_qa["response2"]

        self.context_qa["question2"] = question
        self.context_qa["response2"] = response

    def return_qa_memory(self) -> Tuple[str]:
        """
        Returns the active memory of the assistant
        """
        return self.context_qa["question1"], self.context_qa["response1"], self.context_qa["question2"], self.context_qa["response2"]

    def execute_query(self, query: str) -> str:
        """
        Get's the infromation from the vector database and passes the model to create an understandable response    
        """

        print("Getting products info from the vector database...")
        products_info = self.vector_database.run_query(query)

        print("Data extracted:")
        print(products_info)

        # Add the product data to the context of the model:
        self.context_qa["products_info"] = products_info

        # Generate the response from the LLM:
        response = self.qa(query, context=self.context_qa)["input"]
        
        # Update the memory of the assistant:
        self.update_qa_memory(question=query, response=response)

        return response

if __name__ == "__main__":
    
    semantic_query_engine = SemanticQueryEngine(
        data_path = "/home/leibniz/Desktop/herogra-assistant/data/data_by_sections",
        model_name = "gpt-4-32k"
    )

    query = "Que productos tienen como uso pertinente Fertilizante?"

    response = semantic_query_engine.execute_query(query)

    print(response)