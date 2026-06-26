from app.domain.ml.scoring_service import score_farmer_with_ml
from app.domain.scoring.fairness_checks import run_fairness_checks


class MLScoringAgent:
    name = "ML Scoring Agent"
    version = "synthetic-v1"

    def score(self, farmer: dict) -> dict:
        scoring_result = score_farmer_with_ml(farmer)
        fairness = run_fairness_checks(farmer, scoring_result)

        return {
            "agent": self.name,
            "version": self.version,
            "scoring_result": scoring_result,
            "fairness": fairness,
        }


scoring_agent = MLScoringAgent()