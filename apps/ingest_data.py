import logging
import os
from datetime import datetime
from typing import Annotated

import typer

from realestate_rag.config import DATA_PATH
from realestate_rag.extract_data import download_auction_result

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(process)s %(levelname)s %(message)s",
    filename="/tmp/get-domains.log",
    filemode="a",
)


def main(
    city: Annotated[str, typer.Argument(help="Download data for this city")],
    startdate: Annotated[str, typer.Argument(help="Start date in YYYY-MM-DD format")],
    enddate: Annotated[str, typer.Argument(help="End date in YYYY-MM-DD format")],
) -> None:
    start_dt = datetime.strptime(startdate, "%Y-%m-%d")
    end_dt = datetime.strptime(enddate, "%Y-%m-%d")

    if start_dt > end_dt:
        raise ValueError("Start date must be before end date")

    path = os.path.expanduser(DATA_PATH)
    download_auction_result(city, start_dt, end_dt, f"{path}/{city}_results_{startdate}_{enddate}.json")


if __name__ == "__main__":
    typer.run(main)
