# Databench

> Data analysis tool using Flask, SocketIO and d3.js. Optional parallelization with Redis queue and datastore.

[![Build Status](https://travis-ci.org/svenkreiss/databench.png?branch=master)](https://travis-ci.org/svenkreiss/databench)


## Environment and Install

Setup your environment with

```bash
virtualenv venv
source venv/bin/activate
pip install git+https://github.com/svenkreiss/databench.git@v0.0.1
```

Or installing in editable mode for development of databench itself (usually not required):

```bash
git clone https://github.com/svenkreiss/databench.git .

virtualenv venv
source venv/bin/activate
pip install -e .
```


## Usage

Create a project with this structure:
```
- analyses
    - templates
        - simplepi.html
	- __init__.py
	- simplepi.py
```

See the [databench_examples](https://github.com/svenkreiss/databench_examples) repository.
