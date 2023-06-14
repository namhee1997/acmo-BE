import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from app.interfaces.http.rest.api_v1.api import api_router

from app.config import config

from dotenv import load_dotenv

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

load_dotenv(".env")


app = FastAPI()

engine = create_engine(config["DATABASE_URI"])

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
app.add_middleware(DBSessionMiddleware, db_url=config["DATABASE_URI"])
Base.metadata.create_all(bind=engine)

@app.get("/")
def get():
    return config['DATABASE_URI']


app.include_router(api_router, prefix=config['API_V1_STR'])

# To run locally
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
