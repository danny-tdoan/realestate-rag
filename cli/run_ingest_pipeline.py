import json
import logging
import os
import random
import time
from datetime import datetime
from typing import Annotated

import typer

from realestate_rag.config import DATA_PATH, LOG_INGEST
from realestate_rag.ingest.download_property import download_property_detail
from realestate_rag.ingest.extract_auctions import download_auction_result

log_file = os.path.expanduser(LOG_INGEST)
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(process)s %(levelname)s %(message)s",
    filename=log_file,
    filemode="a",
)


def download(url_file: str, output: str, save_every: int = 10) -> None:
    with open(url_file) as f:
        property_blobs = json.load(f)

    output = os.path.expanduser(output)

    downloaded_urls = _get_downloaded_urls(output)

    results = []
    count = 0

    for item in property_blobs:
        url = item.get("domain_link")
        if not url or url in downloaded_urls:
            continue

        detail = download_property_detail(url)
        results.append(detail)
        count += 1

        if len(results) >= save_every:
            logging.info(f"Writing {len(results)} property details to {output} at count {count}")
            with open(output, "a") as out_f:
                for res in results:
                    if res is not None:
                        out_f.write(json.dumps(res) + "\n")

                    # marked as downloaded
                    downloaded_urls.add(res.get("url") or res.get("domain_link"))
            results = []

        time.sleep(random.uniform(0.5, 1.5))  # noqa: S311

    # last batch
    if results:
        with open(output, "a") as out_f:
            for res in results:
                if res is not None:
                    out_f.write(json.dumps(res) + "\n")


def _get_downloaded_urls(output: str) -> set:
    """Get already downloaded URLs from the output file."""
    downloaded_urls = set()
    if os.path.exists(output):
        with open(output) as f:
            for line in f:
                try:
                    data = json.loads(line)
                    url = data.get("url") or data.get("domain_link")
                    if url:
                        downloaded_urls.add(url)
                except json.JSONDecodeError:
                    continue
    return downloaded_urls


def main(
    city: Annotated[str, typer.Argument(help="Download data for this city")],
    startdate: Annotated[str, typer.Argument(help="Start date in YYYY-MM-DD format")],
    enddate: Annotated[str, typer.Argument(help="End date in YYYY-MM-DD format")],
) -> None:
    start_dt = datetime.strptime(startdate, "%Y-%m-%d")
    end_dt = datetime.strptime(enddate, "%Y-%m-%d")

    if start_dt > end_dt:
        raise ValueError("Start date must be before end date")  # noqa: TRY003

    # Extract auction results to get property urls
    path = os.path.expanduser(DATA_PATH)
    url_file = f"{path}/{city}_results_{startdate}_{enddate}.json"
    download_auction_result(city, start_dt, end_dt, url_file)

    # Download property details
    download(url_file=url_file, output=f"{path}/{city}_property_details_{startdate}_{enddate}.jsonl", save_every=10)


if __name__ == "__main__":
    typer.run(main)
