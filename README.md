# Databench

> Data analysis tool using Flask, SocketIO and d3.js. Optional parallelization with Redis queue and datastore. Live demos are at [databench-examples-viewer.svenkreiss.com](http://databench-examples-viewer.svenkreiss.com).

[![Build Status](https://travis-ci.org/svenkreiss/databench.png?branch=master)](https://travis-ci.org/svenkreiss/databench)


## Environment and Install

Setup your environment with

```bash
virtualenv venv
source venv/bin/activate
pip install -e git+https://github.com/svenkreiss/databench.git#egg=databench
```

Or installing locally and in editable mode for development of databench itself (usually not required):

```bash
git clone https://github.com/svenkreiss/databench.git .

virtualenv venv
source venv/bin/activate
pip install -e .
```

Now you can run
```python
databench
```
and open `http://localhost:5000` in a web browser.


## More Documentation

Please have a look at the first blog post describing analyses with Databench [www.svenkreiss.com/blog/databench-initial/](www.svenkreiss.com/blog/databench-initial/) and have a look at the [databench_examples](https://github.com/svenkreiss/databench_examples) repository. Live demos are at [databench-examples-viewer.svenkreiss.com](http://databench-examples-viewer.svenkreiss.com).
