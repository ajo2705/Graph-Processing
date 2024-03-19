from neo4j import GraphDatabase


class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def bfs(self, start_node, last_node):
        graph_name = "BFSGraph"
        result = None

        graph_creation_query = f"""CALL gds.graph.project('{graph_name}', 'Location', 'TRIP')"""

        bfs_search_query = f"""MATCH (start: Location {{name: {start_node}}}), 
                                    (dest: Location {{name: {last_node}}})
                               WITH id(start) AS source, id(dest) as target
                               CALL gds.bfs.stream('{graph_name}', {{
                                    sourceNode: source,
                                    targetNodes: target }})
                               YIELD path
                               RETURN path"""

        graph_deletion_query = f"""CALL gds.graph.drop('{graph_name}', false)"""

        with self._driver.session() as session:
            session.run(graph_creation_query)
            result = session.run(bfs_search_query).data()
            session.run(graph_deletion_query)

        return result

    def pagerank(self, max_iterations, weight_property):
        graph_name = "RankGraph"
        result = None

        graph_creation_query = f"""CALL gds.graph.project(
                                  '{graph_name}',
                                  'Location',
                                  'TRIP',
                                  {{
                                    relationshipProperties: '{weight_property}'
                                  }}
                                )"""

        page_rank_query = f"""CALL gds.pageRank.stream('{graph_name}', {{
                              maxIterations: {max_iterations},
                              relationshipWeightProperty: '{weight_property}'
                            }})
                            YIELD nodeId, score
                            RETURN gds.util.asNode(nodeId).name AS name, score
                            ORDER BY score DESC, name ASC"""

        graph_deletion_query = f"""CALL gds.graph.drop('{graph_name}', false)"""

        with self._driver.session() as session:
            session.run(graph_creation_query)
            result = list(session.run(page_rank_query))
            session.run(graph_deletion_query)

        return result[0], result[-1]