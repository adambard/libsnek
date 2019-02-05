from libsnek import movement


def test_surroundings():
    assert movement.surroundings((1, 2)) == [
        (1, 1), (2, 2), (1, 3), (0, 2)
    ]

