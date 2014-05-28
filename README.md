# databench

Data analysis tool using Flask, SocketIO and d3.js. Optional parallelization with Redis queue and datastore.


## Install

Standard install from the repository on github:

```
pip install git+https://github.com/svenkreiss/databench.git@v0.0.1
```

Or installing in editable mode for development of databench itself (usually not required):

```
pip install -e git+https://github.com/svenkreiss/databench.git#egg=databench
```


## Usage

Create a project with this structure:

```
- analyses
    - templates
        - myanalysis.html
	- __init__.py
	- myanalysis.py
```

On the command line, all that should be necessary is `databench` and the url (ususally `http://localhost:5000`) will be shown that you can open in a browser.
