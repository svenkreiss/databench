from databench import sanitize_message


def test_nan():
    data = sanitize_message(float('NaN'))
    assert data == 'NaN'


def test_inf():
    data = sanitize_message(float('inf'))
    assert data == 'inf'


def test_neg_inf():
    data = sanitize_message(float('-inf'))
    assert data == '-inf'


def test_list():
    data = sanitize_message([1, float('inf')])
    assert data == [1, 'inf']


def test_dict():
    data = sanitize_message({'one': 1, 'inf': float('inf')})
    assert data['one'] == 1 and data['inf'] == 'inf'


def test_set():
    data = sanitize_message({1, float('inf')})
    assert data == [1, 'inf']


def test_tuple():
    data = sanitize_message((1, float('inf')))
    assert data == [1, 'inf']


if __name__ == '__main__':
    test_nan()
    test_inf()
    test_neg_inf()
    test_list()
    test_dict()
    test_set()
    test_tuple()
