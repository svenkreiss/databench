import databench


@databench.on
def fn_with_doc():
    """Function with docstring."""
    pass


@databench.on_action('bla')
def fn_with_doc_2():
    """Function with docstring."""
    pass


def test_action_decorator_docstring():
    assert fn_with_doc.__doc__ == 'Function with docstring.'


def test_action_decorator_docstring_2():
    assert fn_with_doc_2.__doc__ == 'Function with docstring.'
