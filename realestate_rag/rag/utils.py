def extract_suburb_and_state(address: str) -> tuple:
    """
    Extract suburb, state, and postcode from an address string.
    The expected format is "<Address>, <Suburb> <State> <Postcode>".
    """
    # Split the address by comma and take the second part
    try:
        half = address.split(',')[1].strip()
    except IndexError:
        return "Not available","Not available","Not available"

    # Split the second part by spaces
    parts = half.split()
    if len(parts) < 3:
        return "Not available","Not available","Not available"  # Not enough parts to extract suburb, state, and postcode

    suburb = " ".join(parts[:-2]) # suburb could be multiple words
    state = parts[-2]
    postcode = parts[-1]

    return suburb, state, postcode
