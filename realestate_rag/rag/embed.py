import json
import os
from typing import List
from chromadb import PersistentClient
from chromadb.config import Settings
import chromadb.utils.embedding_functions as embedding_functions
from sentence_transformers import SentenceTransformer
import realestate_rag.config as config
import realestate_rag.rag.utils as utils


def load_docs(jsonl_path: str) -> List[dict]:
    docs = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            docs.append(json.loads(line))
    return docs


def split_text(text: str, chunk_size: int = 500) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
    return chunks


def embed_into_vecdb(jsonl_path: str, collection_name: str):
    # 1. Load docs
    docs = load_docs(jsonl_path)

    # 2. Load embedder
    embedder = SentenceTransformer(config.SENTENCE_TRANSFORMER_MODEL)

    # 3. Setup Chroma DB
    chroma_client = PersistentClient(path=os.path.expanduser(config.CHROMA_DB_PATH))
    collection = chroma_client.get_or_create_collection(
        name=collection_name, configuration={"hnsw": {"space": "cosine"}}
    )

    # 4. Process and insert
    all_texts = []
    all_metadata = []
    all_ids = []

    for doc in docs:
        description = doc.get("full_description", "")
        listing_id = str(doc.get("listing_id", ""))

        # extract suburb and code
        # the format is <Address> <suburb> <state> <postcode>
        address = doc.get("title", "")
        suburb,state,code = utils.extract_suburb_and_state(address)


        # Collect metadata excluding 'description' and 'listing_id'
        metadata = {}
        for k, v in doc.items():
            if k in ("full_description", "listing_id"):
                continue
            if v is None:
                v = "Not Available"
            if k == "photos" and isinstance(v, list):
                metadata[k] = json.dumps(v)
            else:
                metadata[k] = v

        metadata["suburb"] = suburb
        metadata["state"] = state
        metadata["suburb_code"] = code

        all_texts.append(description)
        all_ids.append(listing_id)
        all_metadata.append(metadata)

    # 5. Embed and add to Chroma
    embeddings = embedder.encode(all_texts, show_progress_bar=True, batch_size=64)
    print(f"Embedded {len(all_texts)} chunks for embedding...")

    collection.add(documents=all_texts, embeddings=embeddings.tolist(), metadatas=all_metadata, ids=all_ids)

    # 6. Save to disk
    print(f"Stored {len(all_texts)} chunks into Chroma at {config.CHROMA_DB_PATH} in collection {collection_name}.")
