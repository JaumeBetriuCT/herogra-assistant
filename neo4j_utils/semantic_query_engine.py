import streamlit as st
from neo4j_utils.prompts import CYPHER_GENERATION_TEMPLATE_SK, CYPHER_QA_TEMPLATE_SK
from neo4j_utils.neo4j_connection import Graph
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, AzureChatCompletion
from typing import Tuple

import semantic_kernel as sk

class SemanticQueryEngine:
    def __init__(self):

        self.graph = Graph(
            st.secrets["BOLT_URL"],
            st.secrets["USERNAME"],
            st.secrets["PASSWORD"]
        )
        self.kernel_cypher, self.kernel_qa = sk.Kernel(), sk.Kernel()
        self.api_key = st.secrets["OPENAI_API_KEY"]

        # Add two different models to the kernels:
        self.kernel_cypher.add_chat_service("cypher", OpenAIChatCompletion("gpt-3.5-turbo", self.api_key))
        self.kernel_qa.add_chat_service("qa", OpenAIChatCompletion("gpt-3.5-turbo", self.api_key))

        # Add the schema information from the database to the cypher kernel:
        self.context_cypher = self.kernel_cypher.create_new_context()
        self.context_cypher["schema"] =  self.graph.get_schema()
        # Initialize the context of the conversation history for the cypher generator:
        self.initialize_cypher_memory()

        # Create the object for the context of the qa model:
        self.context_qa = self.kernel_qa.create_new_context()
        # Initialize the context of the qa generator to initialize the history:
        self.initialize_qa_memory()

        # Create the functions of the cypher generator and the QA:
        self.cypher_generator = self.kernel_cypher.create_semantic_function(CYPHER_GENERATION_TEMPLATE_SK)
        self.qa_generator = self.kernel_qa.create_semantic_function(CYPHER_QA_TEMPLATE_SK)
    
    def initialize_cypher_memory(self) -> None:
        self.context_cypher["question1"] = ""
        self.context_cypher["response1"] = ""
        self.context_cypher["db_output1"] = ""
        self.context_cypher["question2"] = ""
        self.context_cypher["response2"] = ""
        self.context_cypher["db_output2"] = ""

    def initialize_qa_memory(self) -> None:
        self.context_qa["question1"] = ""
        self.context_qa["response1"] = ""
        self.context_qa["question2"] = ""
        self.context_qa["response2"] = ""
    
    def update_cypher_memory(self, question: str, response: str, db_output: str) -> None:
        # Move question2 to question1 and get rid of question1:
        self.context_cypher["question1"] = self.context_cypher["question2"]
        # Same with response:
        self.context_cypher["response1"] = self.context_cypher["response2"]
        # Same with the oputput of the database:
        self.context_cypher["db_output1"] = self.context_cypher["db_output2"]

        self.context_cypher["question2"] = question
        self.context_cypher["response2"] = response
        self.context_cypher["db_output2"] = db_output
    
    def update_qa_memory(self, question: str, response: str) -> None:
        # Move question2 to question1 and get rid of question1:
        self.context_qa["question1"] = self.context_qa["question2"]
        # Same with response:
        self.context_qa["response1"] = self.context_qa["response2"]

        self.context_qa["question2"] = question
        self.context_qa["response2"] = response

    def execute_query(self, input_text: str) -> str:
        """Creates the cypher query, executes it and returns the response from the LLM"""
        
        print("generating cypher query...")
        # First generate the cypher query using the input text provided by the user:
        generated_cypher_query = self.cypher_generator(input_text, context=self.context_cypher)["input"]

        print("Generated cypher query:")
        print(generated_cypher_query)

        # Execute the query and get the results from the database. Convert the results to string:
        db_output = self.graph.run_query(generated_cypher_query)
        db_output = str(db_output)

        print("DB results:")
        print(db_output)

        # Add the generated cypher query and the input text to the memory of the model:
        self.update_cypher_memory(question=input_text, response=generated_cypher_query, db_output=db_output)

        # Add the database output as context for the QA kernel:
        self.context_qa["db_output"] = db_output

        # Generate the response of the QA:
        response = self.qa_generator(input_text, context=self.context_qa)["input"]

        # Add the generated response and the input text to the memory of the model:
        self.update_qa_memory(question=input_text, response=response)

        return response
    
    def return_qa_memory(self) -> Tuple[str]:

        return self.context_qa["question1"], self.context_qa["response1"], self.context_qa["question2"], self.context_qa["response2"] 
    
    def return_cypher_memory(self) -> Tuple[str]:

        return (
            self.context_cypher["question1"], 
            self.context_cypher["response1"], 
            self.context_cypher["db_output1"],
            self.context_cypher["question2"], 
            self.context_cypher["response2"],
            self.context_cypher["db_output2"]
            )