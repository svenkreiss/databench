Development
-----------

To contribute to Databench, fork the GitHub repository and then follow these
steps:

.. code-block:: bash

    # clone the repository to your local machine
    git clone https://github.com/<username>/databench.git
    cd databench

    # create a virtual environment and activate it
    virtualenv venv
    source venv/bin/activate
    # install this version in editable mode
    pip install -e .[tests]

    # install JavaScript dependencies
    npm install
    # build the JavaScript
    webpack


Now you can:

.. code-block:: bash

    # run Databench
    databench --log DEBUG
    # and open http://localhost:5000 in a web browser

    # run tests
    nosetests -vv --with-coverage --cover-erase --cover-inclusive

    # lint Python
    flake8

    # lint JavaScript
    npm run lint

    # validate html (with Databench running)
    localcrawl --start http://localhost:5000
    html5validator --root _crawled

    # create JavaScript docs at docs/jsdoc/index.html
    npm run typedoc

    # create Python docs at docs/_build/html/index.html
    cd docs; make html

For new contributions, create a feature branch and submit a Pull Request.
