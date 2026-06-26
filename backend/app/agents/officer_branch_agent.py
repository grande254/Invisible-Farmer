from app.domain.ussd.officer_ussd_flow import handle_officer_ussd


class OfficerBranchUSSDServiceAgent:
    name = "Officer Branch USSD Service Agent"
    version = "v1"

    def handle(self, text: str | None = None, phone_number: str | None = None) -> dict:
        response = handle_officer_ussd(
            text=text,
            phone_number=phone_number,
        )

        response["agent"] = {
            "name": self.name,
            "version": self.version,
            "role": (
                "Allows branch loan officers to start reviews, check compact summaries, "
                "copy farmer-safe SMS, check Masumi job status, and record human outcomes "
                "from a low-bandwidth USSD workflow."
            ),
        }

        response["loan_officer_final_decision_required"] = True
        return response


officer_branch_agent = OfficerBranchUSSDServiceAgent()