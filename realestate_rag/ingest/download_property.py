from realestate_rag.ingest.utils import get_one_page
from bs4 import BeautifulSoup
import logging
import re
import json


def download_property_detail(url:str) -> dict | None:
    try:
        page = get_one_page(url)
        soup = BeautifulSoup(page)

        # all important info is stored as javascript variables
        # Extract all JavaScript variables defined in <script> tags
        js_vars = {}
        for script in soup.find_all("script"):
            if script.text:
                # Example: find variables like var foo = {...};
                matches = re.findall(r"var\s+(\w+)\s*=\s*(\{.*?\});", script.text, re.DOTALL)
                for var, value in matches:
                    js_vars[var] = value

        # assume the names and structure of the variables
        vars = json.loads(js_vars["digitalData"])
        page_info = vars["page"]["pageInfo"]

        property_info = page_info["property"]
        # 1. title (use address as title)
        title = property_info.get("address")

        # 2. description (not present, fallback to features or empty string)
        description = property_info.get("propertyFeatures", "")

        # 3. all links of photos
        photos = property_info.get("images", [])

        # 4. whether it has a floorplan
        has_floorplan = property_info.get("hasFloorplan", False)

        # 5. whether it has a displayed price
        has_displayed_price = property_info.get("hasDisplayPrice", False)

        # 6. number of bedrooms
        bedrooms = property_info.get("bedrooms")

        # 7. number of bathrooms
        bathrooms = property_info.get("bathrooms")

        # 8. number of parkings
        parkings = property_info.get("parking")

        # 10. Area
        area = property_info.get("landArea")

        # 11. Property type (house or unit)
        property_type = property_info.get("primaryPropertyType") or property_info.get("secondaryPropertyType")

        listing_id = page_info["pageId"]

        # Extract full description from the page
        full_description = ""
        desc_div = soup.find("div", {"data-testid": "listing-details__description"})
        if desc_div:
            # Find all <p> tags inside the description div
            paragraphs = desc_div.find_all("p")
            full_description = " ".join(p.get_text(strip=True) for p in paragraphs)

        data = {
            "title": title,
            "description": description,
            "full_description": full_description,
            "photos": photos,
            "has_floorplan": has_floorplan,
            "has_displayed_price": has_displayed_price,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "parkings": parkings,
            "area": area,
            "property_type": property_type,
            "listing_id": listing_id,
            "url": url,
        }
        return data

    except Exception as e:
        logging.error(f"Error downloading property detail from {url}: {e}")
        return None
