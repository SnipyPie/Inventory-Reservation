from fastapi import FastAPI

from app.api.routers.products import router as products_router
from app.api.routers.inventory import router as inventory_router

app = FastAPI()


app.include_router(products_router)

app.include_router(inventory_router)