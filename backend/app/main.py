from fastapi import FastAPI

from app.core.config import settings
from app.core.cors import configure_cors
from app.core.logging_config import configure_logging

from app.api.routes import (
    health,
    farmers,
    reviews,
    scoring,
    graph,
    explanations,
    ussd,
    officer_ussd,
    masumi,
    human_review,
    exports,
)


configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Masumi-compatible ML credit-readiness agent for rural lenders reviewing "
        "thin-file smallholder farmers."
    ),
    version=settings.API_VERSION,
)

configure_cors(app)

app.include_router(health.router)
app.include_router(farmers.router)
app.include_router(reviews.router)
app.include_router(scoring.router)
app.include_router(graph.router)
app.include_router(explanations.router)
app.include_router(ussd.router)
app.include_router(officer_ussd.router)
app.include_router(masumi.router)
app.include_router(human_review.router)
app.include_router(exports.router)
