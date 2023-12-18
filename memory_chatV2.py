import streamlit as st
import yaml
import streamlit_authenticator as stauth

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

    with open("credentials.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    name, authentication_status, username = authenticator.login('Login', 'main')

    print("Authentication status:")
    print(authentication_status)

    if authentication_status:

        # Define the chat history:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Define if is is the first time the user enters the session or not:
        if "first_refresh_session" not in st.session_state:
            st.write("No session state")
            st.session_state.first_refresh_session = True
        else:
            st.write("Session state already fill:")
            st.write(st.session_state.first_refresh_session)
            st.session_state.first_refresh_session = False

        if "number_of_refreshes" not in st.session_state:
            st.session_state.number_of_refreshes = 1
        else:
            st.session_state.number_of_refreshes += 1

        st.title("Asitente virtual Herogra")
        st.image(logo)

        # Prepare the assitant if it is the first session:
        # For some reason streamlit cloud reruns the app 3 times before
        if st.session_state.first_refresh_session <= 3:
            with st.spinner("Preparing the assistant..."):
                st.session_state.semantic_query_engine = SemanticQueryEngine(
                    data_path = "data/data_by_sections",
                    model_name = "gpt-4-32k"
                )

        show_chat_history(icon)

        st.write(st.session_state.number_of_refreshes)

        input_text = st.chat_input("Pregunta al asistente...")

        st.write("Input text:")
        st.write(input_text)
        st.write("End input text")

        if input_text:
            with st.spinner("Generating response..."):
                # Generate a response:
                response = st.session_state.semantic_query_engine.execute_query(input_text)

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

    elif authentication_status == False:
        st.error('Username/password is incorrect')

    elif authentication_status == None:
        st.warning('Please enter your username and password')

if __name__ == "__main__":
    main()