import databench


def test_md():
    data = databench.Readme('tests/analyses/simple1')  # contains README.md
    print(data.meta)
    print(data.text)
    assert data.meta['title'] == 'Simple1'
    assert data.meta['description'] == 'A short description of this analysis.'
    assert data.meta['watch'] == '*.md'


def test_rst():
    data = databench.Readme('tests/analyses/simple2')  # contains README.rst
    print(data.meta)
    print(data.text)
    assert data.meta['title'] == 'testtitle'
    assert data.meta['description'] == 'testdescription of a test'


def test_no_readme():
    data = databench.Readme('tests/analyses/simple3')  # contains no README
    print(data.meta)
    print(data.text)
    assert 'title' not in data.meta
    assert 'description' not in data.meta


def test_unknown_dir():
    data = databench.Readme('tests/does_not_exist')  # directory does not exist
    print(data.meta)
    print(data.text)
    assert 'title' not in data.meta
    assert 'description' not in data.meta


if __name__ == '__main__':
    test_md()
    test_rst()
    test_no_readme()
    test_unknown_dir()
