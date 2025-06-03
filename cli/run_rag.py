import os

from chromadb import PersistentClient
from fastapi import FastAPI
from pydantic import BaseModel

from realestate_rag import config
from realestate_rag.rag import answer

chroma_client = PersistentClient(path=os.path.expanduser(config.CHROMA_DB_PATH))
collection = chroma_client.get_or_create_collection(
    name=config.CHROMA_COLLECTION_NAME, configuration={"hnsw": {"space": "cosine"}}
)

app = FastAPI(title="Search realestate RAG", description="Search real estate RAG")


class QueryRequest(BaseModel):
    query: str


@app.post("/query")
def query_rag(request: QueryRequest):
    response = answer(collection, request.query)
    return {"response": response}
