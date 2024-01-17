FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8501

CMD python create_vector_database.py && streamlit run memory_chatV3.py

# docker run \
#     --name neo4j \
#     -p 7474:7474 -p 7687:7687 \
#     -d \
#     -e NEO4J_AUTH=neo4j/pleaseletmein \
#     -e NEO4J_PLUGINS=\[\"apoc\"\]  \
#     neo4j:latest