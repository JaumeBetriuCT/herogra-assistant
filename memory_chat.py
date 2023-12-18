import os
import sys
import streamlit as st
from PIL import Image

from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# Tutorial langchain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

from neo4j_utils.raw_text import herosol_multicolor, fertigota_suspension, azufre_na_fertigota

# llm = OpenAI(openai_api_key="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")
# Personal: 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

# Streamlit cloud has some problems with the version of sqlite3. So we are adding to the requirements the package pysqlite3-binary and using them:
# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

def show_chat_history(icon) -> None:

    # If there is no chat history:
    if len(st.session_state.chat_history) == 0:
        pass
    else:
        # Iterate trough the messages in the chat history and show them in html format:
        for question_answer in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(question_answer[0])
            with st.chat_message("assistant", avatar=icon):
                st.write(question_answer[1])

def main():
    logo = Image.open('images/herogra_logo.png')
    gpt_logo = Image.open("images/Chat_gpt_logo.png")
    icon = Image.open("images/herogra_icon.png")

    st.set_page_config(page_icon=icon, page_title="Herogra assistant")

    # Define the chat history:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Define if is is the first time the user enters the sessin or not:
    if "first_refresh_session" not in st.session_state:
        st.session_state.first_refresh_session = True
    else:
        st.session_state.first_refresh_session = False

    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

    st.title("Asistente virtual Herogra")

    st.image(logo, width=350)
    #st.info("The chatbot works better with specific questions such as 'How can I create a prepayment sales order?'")
    #st.info("The chatbot has memory too so if you have to ask a different question and it has no relation with the previous one it is better to reload the page to delete the history.")

    if st.session_state.first_refresh_session:
        with st.spinner("Loading chatbot..."):
            
            documents = []
            for file in os.listdir("data"):
                pdf_path = "./data/" + file
                loader = PyPDFLoader(pdf_path)
                documents.extend(loader.load())

            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200) # chunk_size=1000, chunk_overlap=200
            documents = text_splitter.split_documents(documents)

            embeddings = OpenAIEmbeddings()
            vectorstore = Chroma.from_documents(documents, embeddings)

            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

            # Store the qa in session state so it can be always accessed:
            st.session_state.qa = ConversationalRetrievalChain.from_llm(
                ChatOpenAI(model="gpt-4"), 
                vectorstore.as_retriever(search_type="similarity", k=3), 
                memory=memory
            )

    show_chat_history(icon)

    query = st.chat_input("Send a message")

    if query:
        with st.spinner("Generating response..."):
            
            # Get only th etwo lasts question and answers from the chat_history to avoid huge costs:
            context = st.session_state.chat_history[-2:]

            # TO DELETE
            # Add all the text from the Fichas:
            # query = "Información de los productos: " + herosol_multicolor + fertigota_suspension + azufre_na_fertigota +" Pregunta: " + query_
            # query = "Primera ficha: " + herosol_multicolor + "Segunda ficha: " + azufre_na_fertigota + " Pregunta: " + query_ + "Nota: Contesta siempre en forma de lista y por puntos."

            # Generate the answer:
            result = st.session_state.qa({"question": query, "chat_history": context})

            # Show the question:
            with st.chat_message("user"):
                # st.write(query_)
                st.write(result["question"])
            # Show the answer:
            with st.chat_message("assistant", avatar=icon):
                st.write(result["answer"])

            # Add the queries to the chat_history
            st.session_state.chat_history.append((query, result["answer"]))

    with st.columns(2)[1]:
        st.write("Powered by:")
        st.image(gpt_logo, width=250)

if __name__ == "__main__":
    main()