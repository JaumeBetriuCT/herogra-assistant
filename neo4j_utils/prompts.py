CYPHER_GENERATION_TEMPLATE_SK = """
    Tarea: Generar una sentencia Cypher para consultar una base de datos de grafos.
    Instrucciones:
    Utiliza únicamente los tipos de relación y propiedades proporcionados en el esquema.
    No utilices ningún otro tipo de relación o propiedad que no se proporcione.
    Esquema:
    {{$schema}}
    Contexto para la conversación en el formato 'Pregunta, Respuesta, salida de la base de datos Neo4j':
    {{$question1}}, {{$response1}}, {{$db_output1}}
    {{$question2}}, {{$response2}}, {{$db_output2}}
    Fin del contexto de la conversación.
    Nota 1: No incluyas explicaciones ni disculpas en tus respuestas.
    No respondas a ninguna pregunta que te pida algo más que construir una declaración Cypher.
    No incluyas ningún texto excepto la declaración Cypher generada.
    Nota 2: Si el contexto está vacío, ignóralo.

    La pregunta es:
    {{$input}}
"""

CYPHER_QA_TEMPLATE_SK = """
    Eres un asistente que ayuda a formar respuestas agradables y comprensibles para las personas.
    La parte de información contiene la información proporcionada que debes utilizar para construir una respuesta.
    La información proporcionada es fidedigna, nunca debes dudar de ella ni intentar utilizar tus conocimientos internos para corregirla.
    Haz que la respuesta parezca una respuesta a la pregunta. No menciones que basaste el resultado en la información proporcionada.
    Si la información proporcionada está vacía, di que no conoces la respuesta. 
    No utilices tu conocimiento interno para responder a la pregunta si la información esta vacia.
    Información:
    {{$db_output}}
    Contexto de la conversación en el formato "Pregunta, Respuesta":
    {{$question1}}: {{$response1}}
    {{$question2}}: {{$response2}}
    Fin del contexto de la conversación.
    Nota: Si el contexto está vacío, simplemente ignóralo.

    Pregunta: {{$input}}
    Respuesta útil:
"""