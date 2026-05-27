from __future__ import annotations

from fastapi import FastAPI

from feature_review.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Feature Review Service",
        version="0.1.0",
        description="Read-only deterministic backend for feature documentation review.",
    )
    app.include_router(router)
    return app


app = create_app()
