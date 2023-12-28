import streamlit as st

from memory_chat_utils.semantic_query_engine import SemanticQueryEngine
from PIL import Image
from yaml.loader import SafeLoader

def show_chat_history(avatar_icon) -> None:
    # Get the history:
    chat_history = st.session_state.chat_history

    # If there is no chat history:
    if len(chat_history) == 0:
        pass

    else:
        # Iterate trough the history chat
        for question_answer_dict in chat_history:
            with st.chat_message("user"):
                st.write(question_answer_dict["user"])
            with st.chat_message("assistant", avatar=avatar_icon):
                st.write(question_answer_dict["avatar"])

def main():
    logo = Image.open('images/herogra_logo.png')
    gpt_logo = Image.open("images/Chat_gpt_logo.png")
    icon = Image.open("images/herogra_icon.png")

    st.set_page_config(page_icon=icon, page_title="Herogra assistant")

    # Define the chat history:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # # Define if is is the first time the user enters the session or not:
    # if "first_refresh_session" not in st.session_state:
    #     st.session_state["first_refresh_session"] = "first_session"

    st.title("Asitente virtual Herogra")
    st.image(logo)

    # # Prepare the assitant if it is the first session:
    # if st.session_state["first_refresh_session"] == "first_session":
    #     print(st.session_state["first_refresh_session"])
    #     print("We prepare the assistant")
    #     with st.spinner("Preparing the assistant..."):
    #         st.session_state.semantic_query_engine = SemanticQueryEngine(
    #             data_path = "data/data_by_sections",
    #             model_name = "gpt-4-32k"
    #         )

    #         print("Assistant prepared")

    #         # Set the refresh session to false so the the database does not get created again
    #         st.session_state["first_refresh_session"] = "other_session"

    show_chat_history(icon)

    input_text = st.chat_input("Pregunta al asistente...")

    if input_text:
        with st.spinner("Generating response..."):
            # Create the assistant:
            semantic_query_engine = SemanticQueryEngine(
                data_path = "data/data_by_sections",
                model_name = "gpt-4-32k"
            )

            # Generate a response:
            response = semantic_query_engine.execute_query(input_text)

            # Show the question:
            with st.chat_message("user"):
                st.write(input_text)
            # Show the answer:
            with st.chat_message("assistant", avatar=icon):
                st.write(response)

            # Store the question and the response to the chat memory of the session:
            st.session_state.chat_history.append({"user": input_text, "avatar": response})
            
    with st.columns(2)[1]:
        st.write("Powered by:")
        st.image(gpt_logo, width=250)

if __name__ == "__main__":
    main()