from app.domain.explanation.explanation_service import enrich_decision_support_with_explanations


class FeatherlessExplanationAgent:
    name = "Featherless Business Explanation Agent"
    version = "v1"

    def enrich(self, decision_support: dict) -> dict:
        enriched = enrich_decision_support_with_explanations(decision_support)

        enriched["explanation_agent"] = {
            "name": self.name,
            "version": self.version,
            "role": (
                "Transforms ML score, reason codes, alternative evidence, missing records, "
                "risk context, and fairness context into business-ready officer, farmer, branch, "
                "committee, and audit outputs."
            ),
        }

        return enriched


explanation_agent = FeatherlessExplanationAgent()