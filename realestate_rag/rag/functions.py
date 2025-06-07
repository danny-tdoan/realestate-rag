functions = [
    {
        "name": "search_using_text",
        "description": "Search for properties using a text query only.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The user's search query."}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_within_suburb",
        "description": "Search for properties within a specific suburb using a text query.",
        "parameters": {
            "type": "object",
            "properties": {
                "suburb": {"type": "string", "description": "The suburb to search in."},
                "query": {"type": "string", "description": "The user's search query."}
            },
            "required": ["suburb", "query"]
        }
    },
    {
        "name": "search_within_suburb_code",
        "description": "Search for properties within a specific suburb code using a text query.",
        "parameters": {
            "type": "object",
            "properties": {
                "suburb_code": {"type": "string", "description": "The suburb to search in."},
                "query": {"type": "string", "description": "The user's search query."}
            },
            "required": ["suburb_code", "query"]
        }
    }
]