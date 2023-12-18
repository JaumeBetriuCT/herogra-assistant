# Herogras chatbot
This repo contains the implementation of a virtual assistant of Herogra

## Data
The data used in this proje

## Run the streamlit app

To run the aplication locally simply type into a terminal:

```
streamlit run memory_chatV2.py
```

## Cloud deploy
The repo can be deployed on streamlit cloud following the instructions in the page: https://streamlit.io/cloud

Once deployed the app will be accessible from any device using a navigator.

## Open AI api-keys management
To add the Open AI key create a folder in the repo with the name .streamlit and inside crate a file named secrets.toml and add the key with the format:

OPENAI_API_KEY="sk-..."
ENDPOINT = "https://..."
AZURE_API_KEY = "3..."