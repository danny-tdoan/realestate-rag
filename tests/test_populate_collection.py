import pytest
from unittest.mock import patch
from cli.populate_collection import populate_collection, main


def test_populate_collection_calls_embed():
    with patch('cli.populate_collection.embed_into_vecdb') as mock_embed:
        populate_collection('test_collection', 'test_path.jsonl')
        mock_embed.assert_called_once_with('test_path.jsonl', 'test_collection')


def test_main_invokes_populate(monkeypatch):
    called = {}
    def fake_populate(collection_name, property_details_path):
        called['collection_name'] = collection_name
        called['property_details_path'] = property_details_path
    monkeypatch.setattr('cli.populate_collection.populate_collection', fake_populate)
    # Simulate Typer CLI call
    main('my_collection', 'my_path.jsonl')
    assert called['collection_name'] == 'my_collection'
    assert called['property_details_path'] == 'my_path.jsonl'
