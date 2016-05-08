import databench


def test_md():
    data = databench.Readme('tests/readme_md')
    print(data.meta)
    print(data.text)
    assert data.meta['title'] == 'testtitle'
    assert data.meta['description'] == 'testdescription of a test'
    assert data.meta['watch'] == '*.md'


def test_rst():
    data = databench.Readme('tests/readme_rst')
    print(data.meta)
    print(data.text)
    assert data.meta['title'] == 'testtitle'
    assert data.meta['description'] == 'testdescription of a test'


def test_unknown_dir():
    data = databench.Readme('tests/readme_does_not_exist')
    print(data.meta)
    print(data.text)
    assert 'title' not in data.meta
    assert 'description' not in data.meta


if __name__ == '__main__':
    test_md()
    test_rst()
    test_unknown_dir()
