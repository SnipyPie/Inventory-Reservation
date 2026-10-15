import os

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

engine = create_engine(
    URL.create(
        "postgresql+psycopg",
        username="inventory_app",
        password=os.environ["DB_PASSWORD"],
        host="localhost",
        port=5432,
        database="postgres",
    )
)