import pytest
from realestate_rag.rag.utils import extract_suburb_and_state

def test_extract_suburb_and_state_standard():
    address = "51 Warner Avenue, Ashburton VIC 3147"
    suburb, state, postcode = extract_suburb_and_state(address)
    assert suburb == "Ashburton"
    assert state == "VIC"
    assert postcode == "3147"

def test_extract_suburb_and_state_multiword_suburb():
    address = "10 Main St, Box Hill South VIC 3205"
    suburb, state, postcode = extract_suburb_and_state(address)
    assert suburb == "Box Hill South"
    assert state == "VIC"
    assert postcode == "3205"

def test_extract_suburb_and_state_missing_comma():
    address = "10 Main St South Melbourne VIC 3205"
    suburb, state, postcode = extract_suburb_and_state(address)
    assert suburb is None
    assert state is None
    assert postcode is None

def test_extract_suburb_and_state_incomplete():
    address = "10 Main St, VIC 3205"
    suburb, state, postcode = extract_suburb_and_state(address)
    assert suburb is None
    assert state is None
    assert postcode is None

def test_extract_suburb_and_state_too_short():
    address = "10 Main St, VIC"
    suburb, state, postcode = extract_suburb_and_state(address)
    assert suburb is None
    assert state is None
    assert postcode is None
