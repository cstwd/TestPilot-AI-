from subject import prefix_length

def test_prefix_length():
    assert prefix_length([4, None, 2]) == 1
    assert prefix_length([None, 2, 3]) == 2
    assert prefix_length([None, None, None]) == 3
    assert prefix_length([None, None, None, None]) == 4
    assert prefix_length([]) == 0
