import uuid

RAW_YOU = {
        "id": str(uuid.uuid4()),
        "health": 63,
        "name": "Jim-bob",
        "body": [
            {"x": 4, "y": 2},
            {"x": 4, "y": 3},
            {"x": 5, "y": 3},
            {"x": 5, "y": 4}
            ]
        }
RAW = {
        "you": RAW_YOU,
        "turn": 7,
        "board": {
            "width": 12,
            "height": 12,
            "food": [
                {"x": 2, "y": 4},
                {"x": 5, "y": 2},
                {"x": 5, "y": 6},
                ],
            "snakes": [
                {
                    "id": str(uuid.uuid4()),
                    "health": 98,
                    "name": "Bob-jim",
                    "body": [
                        {"x": 9, "y": 1},
                        {"x": 9, "y": 2},
                        {"x": 9, "y": 3},
                        {"x": 9, "y": 4},
                        {"x": 9, "y": 5},
                        {"x": 8, "y": 5},
                        {"x": 8, "y": 4},
                        ]
                    },
                RAW_YOU 
                ]
            },
        "game": {
            "id": str(uuid.uuid4()),
            },
        }

