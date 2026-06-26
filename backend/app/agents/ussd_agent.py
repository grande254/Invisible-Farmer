from app.domain.ussd.farmer_ussd_flow import handle_farmer_ussd


class FarmerUSSDServiceAgent:
    name = "Farmer USSD Service Agent"
    version = "v1"

    def handle(self, text: str | None = None, phone_number: str | None = None) -> dict:
        response = handle_farmer_ussd(
            text=text,
            phone_number=phone_number,
        )

        response["agent"] = {
            "name": self.name,
            "version": self.version,
            "role": (
                "Provides farmer-safe credit-readiness status, review request, improvement tips, "
                "and branch contact guidance through USSD."
            ),
        }

        response["farmer_safe"] = True
        return response


ussd_agent = FarmerUSSDServiceAgent()