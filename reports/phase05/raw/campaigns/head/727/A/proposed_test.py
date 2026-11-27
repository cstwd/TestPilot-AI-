from subject import first

def test_first():
    assert first([8]) == 8
    assert first([]) == 0
    assert first([1]) == 1
    assert first([1, 2, 3]) == 1
    assert first([1, 2, 3, 4]) == 2
    assert first([1, 2, 3, 4, 5]) == 3
    assert first([1, 2, 3, 4, 5, 6]) == 4
    assert first([1, 2, 3, 4, 5, 6, 7]) == 5
    assert first([1, 2, 3, 4, 5, 6, 7, 8]) == 6
    assert first([1, 2, 3, 4, 5, 6, 7, 8, 9]) == 7
    assert first([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == 10
