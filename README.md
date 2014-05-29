# databench

Data analysis tool using Flask, SocketIO and d3.js. Optional parallelization with Redis queue and datastore.


## Environment

Setup your environment with

```shell
virtualenv venv
source venv/bin/activate
```


## Install

Standard install from the repository on github:

```
pip install git+https://github.com/svenkreiss/databench.git@v0.0.1
```

Or installing in editable mode for development of databench itself (usually not required):

```
git clone https://github.com/svenkreiss/databench.git .
pip install -e .
```

The advantage is that this also includes the example `analyses` folder as described below.


## Usage

Create a project with this structure:
```
- analyses
    - templates
        - simplepi.html
	- __init__.py
	- simplepi.py
```

The repository comes with an `analyses` folder as an example. The necessary extra dependencies for these examples can be installed using:
```
pip install -r requirements_analyses.txt
```

On the command line, all that should be necessary is `databench` and the url (usually `http://localhost:5000`) will be shown that you can open in a browser.

This is the backend in `simplepi.py`:

```python
import math
from time import sleep
from random import random

import databench


signals = databench.Signals('simplepi')

@signals.on('connect')
def onconnect():
	inside = 0
	for i in range(10000):
		sleep(0.001)
		r1, r2 = (random(), random())
		if r1*r1 + r2*r2 < 1.0:
			inside += 1

		if (i+1)%100 == 0:
			draws = i+1
			signals.emit('log', {
				'draws':draws,
				'inside':inside,
				'r1':r1,
				'r2':r2
			})

			p = inside/draws
			uncertainty = 4.0*math.sqrt(draws*p*(1.0 - p)) / draws
			signals.emit('status', {
				'pi-estimate': 4.0*inside/draws,
				'pi-uncertainty': uncertainty
			})

	signals.emit('log', {'action': 'done'})


simplepi = databench.Analysis('simplepi', __name__, signals)
simplepi.description = "Calculating \(\pi\) the simple way."
```

And on the frontend `simplepi.html`:

```html
{% extends "base.html" %}
{% block title %}simplepi{% endblock %}


{% block content %}
<h1>
    simplepi
    <small><i>
        π = <span id="pi-estimate">0.0 ± 1.0</span>
    </i></small>
</h1>

<p>This little demo uses two random numbers \(r_1\) and \(r_2\) and
then does a comparison $$r_1^2 + r_2^2 < 1.0$$ to figure out whether
the generated point is inside the first quadrant of the unit circle.</p>

<pre id="log"></pre>
{% endblock %}


{% block footerscripts %}
<script>
	var databench = Databench('simplepi');
	databench.genericElements.log($('#log'));

	databench.signals.on('status', function(msg) {
		$('#pi-estimate').text(
            msg['pi-estimate'].toFixed(3) + ' ± '
            + msg['pi-uncertainty'].toFixed(3)
        );
	});
</script>
{% endblock %}
```

And `__init__.py` is:
```python
import simplepi
```
