def test_range_basic():
    assert list(range(5)) == [0, 1, 2, 3, 4]
    assert list(range(0, 5)) == [0, 1, 2, 3, 4]
    assert list(range(1, 5)) == [1, 2, 3, 4]
    assert list(range(0, 10, 2)) == [0, 2, 4, 6, 8]
    assert list(range(10, 0, -2)) == [10, 8, 6, 4, 2]
    assert list(range(5, 5)) == []
    assert list(range(5, 0)) == []
    assert list(range(0, 5, -1)) == []

def test_range_negative_step():
    assert list(range(5, -1, -1)) == [5, 4, 3, 2, 1, 0]
    assert list(range(0, -5, -1)) == [0, -1, -2, -3, -4]

def run_all_tests():
    test_range_basic()
    test_range_negative_step()
    print("All range() tests passed!")

run_all_tests()