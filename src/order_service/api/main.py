from __future__ import annotations

from fastapi import FastAPI

from order_service.adapters.db import init_db
from order_service.api.error_handlers import register_exception_handlers
from order_service.api.routes import api_router
from order_service.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(title="order-service")
    register_exception_handlers(app)
    app.include_router(api_router)

    @app.on_event("startup")
    def _startup() -> None:
        init_db()

    return app


app = create_app()
