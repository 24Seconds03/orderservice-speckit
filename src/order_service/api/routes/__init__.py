from __future__ import annotations

from fastapi import APIRouter

from order_service.api.routes.order_checkout import router as order_checkout_router
from order_service.api.routes.order_items import router as order_items_router
from order_service.api.routes.orders import router as orders_router
from order_service.api.routes.payments import router as payments_router

api_router = APIRouter()
api_router.include_router(orders_router)
api_router.include_router(order_items_router)
api_router.include_router(order_checkout_router)
api_router.include_router(payments_router)
