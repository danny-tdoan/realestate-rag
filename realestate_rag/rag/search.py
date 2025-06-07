from chromadb import Collection


def search_using_text(collection: Collection, query: str, n_results:int=5) -> str | None:
    """
    Search for properties using a text query only.
    """

    results = collection.query(query_texts=query, n_results=n_results)

    chunks = results["documents"][0] # type: ignore
    metadatas = results["metadatas"][0] # type: ignore

    context = ""

    for chunk, meta in zip(chunks, metadatas):
        # context += f"[#{meta['number']}] {meta['title']}] \n{chunk}\n\n"
        context += f"[#{meta['title']}] \n{chunk}\n\n"

    return context

def search_using_text_with_filter(
    collection: Collection, query: str, filters: dict, n_results=5
) -> str | None:

    results = collection.query(query_texts=query, n_results=n_results, where=filters)

    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = ""

    for chunk, meta in zip(chunks, metadatas):
        # context += f"[#{meta['number']}] {meta['title']}] \n{chunk}\n\n"
        context += f"[#{meta['title']}] \n{chunk}\n\n"

    return context

def search_within_suburb(
    collection: Collection, suburb: str, query: str, n_results=5
) -> str | None:
    """
    Search for properties within a specific suburb using a text query.
    """

    filters = {"suburb": suburb}
    return search_using_text_with_filter(collection, query, filters, n_results)

def search_within_suburb_code(
    collection: Collection, suburb_code: str, query: str, n_results=5
) -> str | None:
    """
    Search for properties within a specific suburb code using a text query.
    """

    filters = {"suburb": suburb_code}
    return search_using_text_with_filter(collection, query, filters, n_results)