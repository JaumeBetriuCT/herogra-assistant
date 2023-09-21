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

# llm = OpenAI(openai_api_key="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")
# Personal: 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

# Streamlit cloud has some problems with the version of sqlite3. So we are adding to the requirements the package pysqlite3-binary and using them:
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

def show_chat_history() -> None:

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

logo = Image.open('images/gurit_logo.png')
gpt_logo = Image.open("images/Chat_gpt_logo.png")
icon = Image.open("images/gurit_icon.png")

st.set_page_config(page_icon=icon, page_title="Gurit chatbot")

# Define the chat history:
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Define if is is the first time the user enters the sessin or not:
if "first_refresh_session" not in st.session_state:
    st.session_state.first_refresh_session = True
else:
    st.session_state.first_refresh_session = False

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

st.title("Gurit virtual assistant")

st.image(logo, width=350)

if st.session_state.first_refresh_session:
    with st.spinner("Loading chatbot..."):
        
        documents = []
        for file in os.listdir("chatbot_databases"):
            pdf_path = "./chatbot_databases/" + file
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())

        text_splitter = CharacterTextSplitter(chunk_size=10000, chunk_overlap=200) # chunk_size=1000, chunk_overlap=200
        documents = text_splitter.split_documents(documents)

        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(documents, embeddings)

        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Store the qa in session state so it can be always accessed:
        st.session_state.qa = ConversationalRetrievalChain.from_llm(
            ChatOpenAI(model="gpt-3.5-turbo-16k"), 
            vectorstore.as_retriever(), 
            memory=memory
        )

show_chat_history()

query = st.chat_input("Escribe tu consulta")

if query:
    with st.spinner("Generando respuesta..."):
        
        # Get only th etwo lasts question and answers from the chat_history to avoid huge costs:
        context = st.session_state.chat_history[-2:]

        # Generate the answer:
        result = st.session_state.qa({"question": query, "chat_history": context})

        # Show the question:
        with st.chat_message("user"):
            st.write(result["question"])
        # Show the answer:
        with st.chat_message("assistant", avatar=icon):
            st.write(result["answer"])
        
        # Add the queries to the chat_history
        st.session_state.chat_history.append((query, result["answer"]))

with st.columns(2)[1]:
    st.write("Powered by:")
    st.image(gpt_logo, width=250)

# Noticies: https://teams.microsoft.com/l/message/19:meeting_NWQ1ODdlMGEtZDE2MS00NzJhLTg0NzYtYmY1NmNlZjQxZmJj@thread.v2/1694510592323?context=%7B%22contextType%22%3A%22chat%22%7D
# https://www.dqsconsulting.com/noticias/categoria/dqsteam/