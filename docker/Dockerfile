# Use one image of Neo4j
FROM neo4j:latest

# Define environment variables:
ENV NEO4J_AUTH=neo4j/pleaseletmein

# Install APOC plugin
RUN sh -c 'cd /var/lib/neo4j/plugins && wget https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/<apoc_version>/apoc-<apoc_version>-all.jar'

# Expose ports:
EXPOSE 7474 7687

# Comand to execute Neo4j:
CMD ["neo4j"]

# docker run \
#     --name neo4j \
#     -p 7474:7474 -p 7687:7687 \
#     -d \
#     -e NEO4J_AUTH=neo4j/pleaseletmein \
#     -e NEO4J_PLUGINS=\[\"apoc\"\]  \
#     neo4j:latest