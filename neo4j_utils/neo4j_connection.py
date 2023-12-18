from neo4j import GraphDatabase

NODE_PROPERTIES_QUERY = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
RETURN {labels: nodeLabels, properties: properties} AS output
"""

REL_PROPERTIES_QUERY = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "relationship"
WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
RETURN {type: nodeLabels, properties: properties} AS output
"""

REL_QUERY = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE type = "RELATIONSHIP" AND elementType = "node"
UNWIND other AS other_node
RETURN "(:" + label + ")-[:" + property + "]->(:" + toString(other_node) + ")" AS output
"""

class Graph:
    """Class to interact with the neo4j database"""

    def __init__(self, bolt_url: str, username: str, password: str):
        
        self.driver = GraphDatabase.driver(
            uri = bolt_url,
            auth = (username, password)
        )

    def run_query(self, query: str) -> str:
        """Query Neo4j database"""
        with self.driver.session(database="neo4j") as session:

            data = session.run(query, {})
            result = [r.data() for r in data]

        return result

    def get_schema(self) -> str:
        """Get a description of the database for the LLM"""

        # node_properties = self.run_query(NODE_PROPERTIES_QUERY)
        # relationships_properties = self.run_query(REL_PROPERTIES_QUERY)
        # relationships = self.run_query(REL_QUERY)

        # schema = f"""
        # Las propiedades de los nodos son las siguientes:
        # {[el['output'] for el in node_properties]}
        # Las propiedades de relaciones son las siguientes:
        # {[el['output'] for el in relationships_properties]}
        # Las relaciones son las siguientes:
        # {[el['output'] for el in relationships]}
        # """

        schema = f"""
            Tipos de nodos: Producto, Seccion.
            Hay los siguientes productos con nombre:
                - AAR315-4+2+6 EXTRA NA-V FERTIGOTA
                - AAR315-4+2+6 AZUFRE NA FERTIGOTA
            Las secciones estan relacionadas a los productos mediante la relación PERTENECE
            Las secciones representan secciones de un documento que recoje la ficha técnica del producto.
            Cada producto tiene 16 secciones associadas. El nombre del nodo de la sección es su numero seguido
            del nombre del producto. Por ejemplo: 'Sección 9 AAR315-4+2+6 AZUFRE NA FERTIGOTA' o 'Sección 1 AAR315-4+2+6 EXTRA NA-V FERTIGOTA'
            cada sección recoje los siguientes datos:
                - Sección 1: Identificador, nombre y código. Usos pertinentes identificados de la sustancia o de la mezcla y usos desaconsejados. Datos del proveedor de la ficha de datos de seguridad.  Indica el número de teléfono de emergencia y su disponibilidad.
                - Sección 2: Clasificación de la sustancia o de la mezcla: Lista con todos los riesgos/peligros del producto. Detalla la información que debe aparecer en la etiqueta del producto químico, conforme al Reglamento (CE) No 1272/2008. Indica otros peligros del producto

            Ejemplo: Si te preguntan sobre el código de un producto, tienes que devolver los nodos Seccion que contengan la información sobre el código del producto que se ha pedido. En este caso tendrias que devolver todas las secciones 1 de todos los productos.
            Otro ejemplo: Si te preguntan por algun tipo de peligro o riesgo tienes que devolver todas las secciones 2 de todos los productos.
            
        """

        return schema