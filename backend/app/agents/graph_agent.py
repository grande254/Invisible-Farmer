from app.domain.graph.graph_analytics import analyze_farmer_graph


class Neo4jGraphIntelligenceAgent:
    name = "Neo4j Graph Intelligence Agent"
    version = "v1"

    def analyze(self, farmer: dict, scoring_result: dict | None = None) -> dict:
        graph_result = analyze_farmer_graph(farmer)

        graph_result["agent"] = {
            "name": self.name,
            "version": self.version,
            "role": (
                "Uses Neo4j relationship intelligence to reveal cooperative, savings group, buyer, "
                "input supplier, extension support, county, crop, and peer-similarity evidence."
            ),
        }

        graph_result["linked_scoring_context"] = {
            "ml_provider": (scoring_result or {}).get("provider"),
            "ml_score": (scoring_result or {}).get("score"),
            "ml_tier": (scoring_result or {}).get("tier"),
            "important_boundary": (
                "Graph intelligence supports verification and context. "
                "It does not override the ML score and does not make the final lending decision."
            ),
        }

        return graph_result


graph_agent = Neo4jGraphIntelligenceAgent()