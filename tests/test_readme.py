import databench


def test_md():
    data = databench.Readme('tests/readme_md')
    print(data.meta)
    print(data.text)
    assert data.meta['title'] == 'testtitle'
    assert data.meta['description'] == 'testdescription of a test'


def test_rst():
    data = databench.Readme('tests/readme_rst')
    print(data.meta)
    print(data.text)
    assert data.meta['title'] == 'testtitle'
    assert data.meta['description'] == 'testdescription of a test'


if __name__ == '__main__':
    test_md()
    test_rst()
