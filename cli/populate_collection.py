from typing import Annotated

import typer

from realestate_rag.rag.embed import embed_into_vecdb


def populate_collection(collection_name, property_details_path):
    print(f"Populating collection {collection_name} with data from {property_details_path}")
    embed_into_vecdb(property_details_path, collection_name)


def main(
    collection_name: Annotated[str, typer.Argument(help="Collection name to populate property details too")],
    property_details_path: Annotated[str, typer.Argument(help="Property details")],
) -> None:
    populate_collection(collection_name, property_details_path)


if __name__ == "__main__":
    typer.run(main)
