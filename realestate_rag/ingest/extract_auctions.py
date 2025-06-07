import datetime
import json
import logging
from realestate_rag.ingest.utils import get_one_page

from bs4 import BeautifulSoup, Tag

ARTICLE_CLASS = "css-3xqrp1"
SUBURB_CLASS = "css-1czqru0"
UL_CLASS = "css-1q8knlq"
PROPERTY_CLASS = "css-1b9txmm"
PROPERTY_DETAILS = "css-dpwygs"
NUM_BEDS_CLASS = "css-1g2pbs1"
OUTCOME_CLASS = "css-43wvni"
AGENT_CLASS = "css-1wxwou3"
PASSEDIN_CLASS = "css-pczn8c"


ROOT_URL = "https://www.domain.com.au/auction-results"
all_results_df = None


def download_auction_result(city: str, startdate: datetime.datetime, enddate: datetime.datetime, output: str) -> None:
    results = []
    while startdate < enddate:
        dt = startdate.strftime("%Y-%m-%d")
        logging.debug(f"Extracting data for city {city} date {dt}")

        url = f"{ROOT_URL}/{city}/{dt}"
        logging.debug(f"Extracting from URL {url}")
        auctions = get_one_page(url)
        all_suburbs = extract_all_suburbs(auctions)

        logging.debug("Extracted the list of suburbs")
        for suburb in all_suburbs:
            suburb_name, sold_properties = extract_one_suburb_section(suburb)

            for property in sold_properties:
                property_detail = extract_one_property(property)
                property_detail["suburb_name"] = suburb_name
                property_detail["sold_date"] = dt

                results.append(property_detail)

        logging.debug(f"Extracted {len(results)} properties up to {dt}")
        startdate = startdate + datetime.timedelta(days=7)

    with open(output, "w") as f:
        json.dump(results, f, indent=2)


def extract_one_property(rea_property: Tag)-> dict:
    address = ""
    domain_link = ""
    property_type = ""
    property_beds = ""
    agent = ""
    outcome_sold = ""
    outcome_price = ""

    res:dict = {}

    property_link = rea_property.find("a", {"class": PROPERTY_CLASS})
    if property_link is None:
        logging.debug("No property link found, skipping this property")
        return res

    address = property_link.text
    domain_link = property_link["href"]

    # Get the details
    property_details = rea_property.find("li", {"class": PROPERTY_DETAILS})
    property_details = property_details.find_all("span") # type: ignore
    property_type = property_details[0].text
    property_beds = property_details[1].text

    # Get the agent
    agent = rea_property.find("li", {"class": AGENT_CLASS}).find("a").text # type: ignore

    # Get the outcome
    outcome = rea_property.find("li", {"class": OUTCOME_CLASS})
    try:
        outcome = outcome.find_all("span") # type: ignore
        outcome_sold = outcome[0].text
        outcome_price = outcome[1].text
    except:
        # if fail, try to get the pass in
        outcome = rea_property.find("li", {"class": PASSEDIN_CLASS})
        if len(outcome) > 0: # type: ignore
            outcome_sold = "Passed in"
            outcome_price = -1

    res["address"] = address
    res["domain_link"] = domain_link
    res["property_type"] = property_type
    res["property_beds"] = property_beds
    res["agent"] = agent
    res["outcome_sold"] = outcome_sold
    res["outcome_price"] = outcome_price

    return res


def extract_one_suburb_section(suburb:str) -> tuple[str, list[Tag]]:
    try:
        suburb_name = suburb.find("h3").text
    except AttributeError:
        suburb_name = "Unable to extract"
        logging.debug("Failed to extract suburb name")

    all_properties = suburb.find_all("ul", {"class": UL_CLASS}) # type: ignore

    return suburb_name, all_properties


def extract_all_suburbs(page):
    soup = BeautifulSoup(page)

    all_suburbs = soup.find_all("article", {"class": ARTICLE_CLASS})

    return all_suburbs
